from concurrent.futures import ThreadPoolExecutor
import sys
import time
from threading import Thread, Lock
try:
    from uwsgidecorators import postfork, thread
    isinuwsgi = True
except:
    isinuwsgi = False

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
            try:
                task["func"](*task["args"])
            except:
                from .util import log
                import traceback
                log(__name__, traceback.format_exc())
            task["next"] = now+task["interval"]
    tasks_lock.release()


# @postfork
# @thread
def time_ticker(tick_interval_sec=1):
    while True:
        check_tasks()
        time.sleep(tick_interval_sec)


# if isinuwsgi:
#     time_ticker = postfork(thread(time_ticker))


def init(tick_interval_sec=1):
    t = Thread(target=time_ticker, kwargs={"tick_interval_sec": tick_interval_sec})
    t.start()


isinpackage = not __name__ in ['scheduler', '__main__']

if not isinpackage:
    import subprocess
    from wsgiref.simple_server import make_server
    add_task(1, lambda: print('hoge'))
    if isinuwsgi:
        init(0.1)
    time.sleep(4)
    try:
        subprocess.check_call(['bash', '-c', f'kill -9 `lsof -t -i:8888`'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    finally:
        time.sleep(1)

    with make_server('', 8888, lambda a, b: [b'hoge']) as httpd:
        print(__name__, f'Listen on port: ')
        httpd.serve_forever()


pool = ThreadPoolExecutor(1000)


__all__ = ["init", "add_task", "pool"]
