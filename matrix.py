import random
import sys
import time
from collections import deque, namedtuple
from functools import partial

katana = range(0xFF65, 0xFF9E)
numbers = range(0x30, 0x3A)
chars = [chr(n) for n in (*katana, *numbers)]
glyph = lambda: random.choice(chars)

BLACK, WHITE, GREEN = 30, 37, 32
NORMAL, BOLD = 0, 1
BLANK = ' '

countdown = lambda total: range(total-1, -1, -1)

Drop = namedtuple('Drop', 'x y char')

def colordrop(drop, color, style):
    return (f'\x1b[{drop.y};{drop.x}f\x1b[{color};'
            f'{style}m{drop.char}')

whitedrop = partial(colordrop, color=WHITE, style=BOLD)
greendrop = partial(colordrop, color=GREEN, style=BOLD)
blackdrop = partial(colordrop, color=BLACK, style=BOLD)
erase = lambda d: blackdrop(Drop(d.x, d.y, BLANK))


def stream(x, y, length, speed):
    drop = Drop(x, y, '')
    glyphs = deque()

    while True:
        for _ in countdown(speed):
            drop = Drop(x, y, glyph())
            yield whitedrop(drop)

        y += 1
        glyphs.append(drop)

        yield greendrop(drop)

        if len(glyphs) > length:
            yield erase(glyphs.popleft())
            yield blackdrop(glyphs[0])


def main():
    # disable cursos
    print('\x1b[?25l\x1b[s', end='')

    x, y = 1, 1
    length = 9
    speed = 10

    try:
        for s in stream(x, y, length, speed):
            print(s, end='', flush=True)
            time.sleep(0.01)
    except KeyboardInterrupt:
        sys.exit()

    print('\x1b[m\x1b[2J\x1b[u\x1b[?25h', end='')


if __name__ == '__main__':
    main()