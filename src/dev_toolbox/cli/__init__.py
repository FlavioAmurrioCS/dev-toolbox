from __future__ import annotations

import time

def fib(n: int) -> int:
    if n <= 1:
        return n
    else:
        return fib(n - 2) + fib(n - 1)

def dev_toolbox():
    t0 = time.time()
    fib(32)
    print(time.time() - t0)
    print('Hello world!')
