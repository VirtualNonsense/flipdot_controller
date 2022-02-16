import time

from clock import Clock
from flipdot import FlipDotMatrix

if __name__ == '__main__':
    m = FlipDotMatrix("192.168.47.9", 69)
    clock = Clock(m)
    while True:
        clock.update()
        time.sleep(1)
