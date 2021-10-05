import os
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


def stream(x, y, length, speed, ttl):
    drop = Drop(x, y, '')
    glyphs = deque()

    for _ in countdown(ttl):
        for _ in countdown(speed):
            drop = Drop(x, y, glyph())
            yield whitedrop(drop)

        y += 1
        glyphs.append(drop)

        yield greendrop(drop)

        if len(glyphs) > length:
            yield erase(glyphs.popleft())
            yield blackdrop(glyphs[0])

    while len(glyphs) > 1:
        yield erase(glyphs.popleft())
        yield blackdrop(glyphs[0])

    yield erase(glyphs.popleft())


def random_stream():
    w, h = os.get_terminal_size()
    min_len, max_len = 5, h//2
    min_x, max_x = 1, w
    min_y, max_y = 1, h//3
    min_speed, max_speed = 3, 15

    length = random.randint(min_len, max_len)
    ttl = random.randint(length, length * 2)

    return stream(random.randint(min_x, max_x),
                  random.randint(min_y, max_y),
                  length,
                  random.randint(min_speed, max_speed),
                  ttl)


def main():
    # disable cursos
    print('\x1b[?25l\x1b[s', end='')

    try:
        for drop in rain(100):
            print(drop, end='', flush=True)

    except KeyboardInterrupt:
        sys.exit()

    # print('\x1b[m\x1b[2J\x1b[u\x1b[?25h', end='')

def rain(max_streams, delay=0.005):
    active = set()
    done = set()
    spawn = lambda n: (random_stream() for _ in range(n))

    while True:
        active.update(spawn(max_streams-len(active)))
        for stream in active:
            try:
                yield next(stream)
            except StopIteration:
                done.add(stream)
        active.difference_update(done)
        time.sleep(delay)



if __name__ == '__main__':
    main()