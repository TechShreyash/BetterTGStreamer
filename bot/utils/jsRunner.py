import threading, js2py, asyncio
from utils.other import random_string

JS_CACHE = {}


def _js_runner(js: str, hash: str):
    global JS_CACHE
    try:
        JS_CACHE[hash] = js2py.eval_js(js)
    except Exception as e:
        JS_CACHE[hash] = "Error: " + str(e)


async def evaluate_js(js: str):
    global JS_CACHE

    hash = random_string(10)
    while hash in JS_CACHE:
        hash = random_string(10)

    JS_CACHE[hash] = False
    threading.Thread(target=_js_runner, args=(js, hash)).start()

    while not JS_CACHE[hash]:
        await asyncio.sleep(1)

    data = JS_CACHE.pop(hash)

    if data.startswith("Error:"):
        raise Exception(data)
    return data
