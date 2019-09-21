import time
from threading import Thread, Lock

tasks = []
tasks_lock = Lock()


def add_task(interval, func, args=()):
    tasks_lock.acquire()
    tasks.append({
        "func": func,
        "next": time.time(),
        "args": args,
        "interval": interval
    })
    tasks_lock.release()


def check_tasks():
    tasks_lock.acquire()
    now = time.time()
    for task in tasks:
        if task["next"] < now:
            task["func"](*task["args"])
            task["next"] = now+task["interval"]
    tasks_lock.release()


def time_ticker(tick_interval_sec):
    while True:
        check_tasks()
        time.sleep(tick_interval_sec)


def init(tick_interval_sec=1):
    t = Thread(target=time_ticker, kwargs={"tick_interval_sec": tick_interval_sec})
    t.start()


__all__ = ["init", "add_task"]
