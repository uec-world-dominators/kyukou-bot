import asyncio
import greenlet
from kyukou import Router, log


@asyncio.coroutine
def run(me, f, environ):
    status, headers, ret = Router.do(environ)
    log(__name__, f'{environ["HTTP_X_REAL_IP"].ljust(15)}  |  {status.ljust(15)}  [{environ["REQUEST_METHOD"].ljust(5)}] {environ["PATH_INFO"]}  ({environ["SERVER_PROTOCOL"]}) {environ["HTTP_X_REQUEST_ID"]}')
    f.set_result((status, headers, ret))
    me.switch()


def application(environ, start_response):
    myself = greenlet.getcurrent()
    future = asyncio.Future()
    asyncio.Task(run(myself, future, environ))
    myself.parent.switch()
    status, headers, ret = future.result()
    start_response(status, headers)
    return ret
