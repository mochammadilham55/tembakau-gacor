

def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def lerp(a, b, t):
    return a + (b - a) * t


def rgb255(r, g, b):
    return (r / 255.0, g / 255.0, b / 255.0)


def mix(c1, c2, t):
    t = clamp(t, 0.0, 1.0)
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))
