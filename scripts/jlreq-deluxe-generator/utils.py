import logging


logger = logging.getLogger(__name__)


FIXED_SCALE = 1 << 20
FIXED_UNIT = 1.0 / FIXED_SCALE
FIXED_HALF = 0.5 * FIXED_UNIT


def from_fixed(x: int) -> float:
    """float from fixed word"""
    return x * FIXED_UNIT


def to_fixed(x: float) -> int:
    """float to fixed word"""
    return int(round(x * FIXED_SCALE))


def f_round(v: float) -> float:
    return from_fixed(to_fixed(v))


def f_near(x: float, y: float) -> bool:
    return abs(x - y) <= 2.0 * FIXED_UNIT


def to_fixed_str(v: float) -> str:
    v = f_round(v)
    us = str(v + FIXED_HALF)
    ls = str(v - FIXED_HALF)
    up = us.find(".")
    lp = us.find(".")
    if us[:up] != ls[:lp]:
        return f"{v:.1f}"
    while us[up] == ls[up]:
        up += 1
    return format(v, f".{up - lp}f").rstrip("0")


def b2u(b):
    """bytes to unsigned int"""
    v = 0
    for c in b:
        v = (v << 8) | c
    return v


def b2i(b):
    """bytes to signed int"""
    m = 1 << (len(b) * 8)
    v = b2u(b)
    if v >= (m >> 1):
        v -= m
    return v


def to_f(b):
    return b2i(b) * FIXED_UNIT


def unpack_str(b: bytes) -> bytes:
    return b[1 : 1 + b[0]]


def pack_str(n: int, b: bytes) -> bytes:
    c = len(b)
    b = bytes([c]) + b
    return b.ljust(n, b"\x00")[:n]
