import os
import random
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from functools import partialmethod

katana = range(0xFF65, 0xFF9E)
numbers = range(0x30, 0x3A)
chars = [chr(n) for n in (*katana, *numbers)]
glyph = lambda: random.choice(chars)

countdown = lambda total: range(total - 1, -1, -1)

BLACK, WHITE, GREEN = 30, 37, 32
NORMAL, BOLD = 0, 1
BLANK = " "


@dataclass
class Drop:
    x: int
    y: int
    char: str = field(default_factory=glyph)
    color: int = BLACK
    style: int = BOLD

    def __str__(self):
        return f"\x1b[{self.y};{self.x}f\x1b[{self.color};{self.style}m{self.char}"

    def empty(self):
        self.__dict__.update(char=BLANK, color=BLACK)
        return self

    def _color(self, value):
        self.color = value
        return self

    white = partialmethod(_color, WHITE)
    green = partialmethod(_color, GREEN)
    black = partialmethod(_color, BLACK)


def stream(x, y, length, speed, ttl):
    drop = None
    glyphs = deque()

    for _ in countdown(ttl):
        for _ in countdown(speed):
            drop = Drop(x, y)
            yield drop.white()

        y += 1
        glyphs.append(drop)

        yield drop.green()

        if len(glyphs) > length:
            yield glyphs.popleft().empty()
            yield glyphs[0].black()

    while len(glyphs) > 1:
        yield glyphs.popleft().empty()
        yield glyphs[0].black()

    yield glyphs.popleft().empty()


def random_stream():
    w, h = os.get_terminal_size()
    min_len, max_len = 5, h // 2
    min_x, max_x = 1, w
    min_y, max_y = 1, h // 3
    min_speed, max_speed = 3, 15

    length = random.randint(min_len, max_len)
    ttl = random.randint(length, length * 2)

    return stream(
        random.randint(min_x, max_x),
        random.randint(min_y, max_y),
        length,
        random.randint(min_speed, max_speed),
        ttl,
    )


def rain(stream_factory, max_streams=10, delay=0.005):
    active = set()
    done = set()
    spawn = lambda n: (stream_factory() for _ in range(n))

    while True:
        active.update(spawn(max_streams - len(active)))
        for stream in active:
            try:
                yield next(stream)
            except StopIteration:
                done.add(stream)
        active.difference_update(done)
        time.sleep(delay)


def main():
    print("\x1b[?25l\x1b[s", end="")

    try:
        for drop in rain(random_stream, 100):
            print(drop, end="", flush=True)
            # print(repr(drop), flush=True)

    except KeyboardInterrupt:
        sys.exit()

    print('\x1b[m\x1b[2J\x1b[u\x1b[?25h', end='')


if __name__ == "__main__":
    main()