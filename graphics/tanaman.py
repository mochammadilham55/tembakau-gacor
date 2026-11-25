"""
Tanaman tembakau: bentuk Pycairo + penerjemah string L-system -> scene graph.
Hierarki: Tanaman > Ruas > Cabang > Daun, dan Ruas > Bunga di pucuk.
"""
import math
import random

import cairo

from .lsystem import string_tembakau
from .scene import Node
from .util import clamp, mix, rgb255

HIJAU_B, HIJAU_A, KUNING = rgb255(66, 126, 50), rgb255(124, 186, 80), rgb255(214, 196, 92)
COKLAT = rgb255(176, 150, 72)


class Ruas(Node):
    def __init__(self, panjang, w0, w1, warna, rot):
        super().__init__("Ruas", rot=rot, tip=(0, -panjang))
        self.p, self.w0, self.w1, self.warna = panjang, w0, w1, warna

    def draw(self, ctx):
        ctx.move_to(-self.w0 / 2, 0)
        ctx.line_to(-self.w1 / 2, -self.p)
        ctx.line_to(self.w1 / 2, -self.p)
        ctx.line_to(self.w0 / 2, 0)
        ctx.close_path()
        ctx.set_source_rgb(*self.warna)
        ctx.fill()


class Daun(Node):
    def __init__(self, panjang, lengkung, kuning):
        super().__init__("Daun")
        self.L, self.b, self.k = panjang, lengkung, kuning

    def draw(self, ctx):
        L, b = self.L, self.b
        w = L * 0.34
        ctx.move_to(0, 0)
        ctx.curve_to(w + b * .3, -L * .22, w * .95 + b * .8, -L * .68, b * 1.2, -L)
        ctx.curve_to(-w * .8 + b * .8, -L * .66, -w * .85 + b * .3, -L * .2, 0, 0)
        g = cairo.LinearGradient(0, 0, 0, -L)
        g.add_color_stop_rgb(0, *mix(HIJAU_B, KUNING, self.k))
        g.add_color_stop_rgb(1, *mix(HIJAU_A, KUNING, self.k * 0.8))
        ctx.set_source(g)
        ctx.fill_preserve()
        ctx.set_source_rgba(0, 0.1, 0, 0.22)
        ctx.set_line_width(1)
        ctx.stroke()
        ctx.set_source_rgba(0.95, 1, 0.85, 0.7)              # tulang daun utama
        ctx.set_line_width(max(1.0, L / 55))
        ctx.move_to(0, 0)
        ctx.curve_to(b * .3, -L * .4, b * .8, -L * .75, b * 1.2, -L)
        ctx.stroke()
        if L > 40:                                           # tulang daun samping
            ctx.set_source_rgba(0.95, 1, 0.85, 0.35)
            ctx.set_line_width(1)
            for t in (.25, .45, .65, .82):
                yy, xx = -L * t, b * 1.2 * t * t
                for sg in (-1, 1):
                    ctx.move_to(xx, yy)
                    ctx.line_to(xx + sg * w * .7 * (1 - t * .5), yy - L * .09)
                    ctx.stroke()


class Bunga(Node):
    """Malai bunga: cabang kurva Bezier dengan bunga kecil merah muda."""
    def __init__(self, skala, seed):
        super().__init__("Bunga")
        self.s, self.seed = skala, seed

    def draw(self, ctx):
        r, s, pts = random.Random(self.seed), self.s, []
        ctx.set_source_rgb(*rgb255(70, 120, 50))
        ctx.set_line_width(3 * s)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for i in range(9):
            ang = -math.pi / 2 + (i - 4) * .30
            ln = (40 + r.uniform(0, 22)) * s
            x, y = math.cos(ang) * ln, math.sin(ang) * ln
            ctx.move_to(0, 0)
            ctx.curve_to(x * .3, y * .5, x * .8, y * .8, x, y)
            ctx.stroke()
            pts.append((x, y))
        for x, y in pts:
            for k in range(4):
                fx, fy = x + r.uniform(-9, 9) * s, y + r.uniform(-9, 6) * s
                for p in range(5):
                    a = p * 2 * math.pi / 5 + k
                    ctx.arc(fx + math.cos(a) * 4.4 * s, fy + math.sin(a) * 4.4 * s, 3.9 * s, 0, 2 * math.pi)
                    ctx.set_source_rgb(*rgb255(240, 150, 176))
                    ctx.fill()
                ctx.arc(fx, fy, 2.2 * s, 0, 2 * math.pi)
                ctx.set_source_rgb(*rgb255(255, 230, 120))
                ctx.fill()


def bangun_tanaman(k, cfg, seed):
    """Menerjemahkan string L-system menjadi pohon Node (turtle interpretation)."""
    rng = random.Random(seed)
    vigor, stres, wilt = k["vigor"], k["stres"], k["wilt"]
    s = string_tembakau(cfg["iter"], cfg["bunga"] > 0)
    n_f = max(1, s.count("F"))
    tinggi = cfg["Ht"] * (0.75 + 0.25 * vigor)
    seg = tinggi / n_f
    warna_batang = mix(rgb255(70, 118, 48), COKLAT, 0.5 * stres)

    root = Node("Tanaman", sx=cfg["skala"], sy=cfg["skala"])
    cur, stack, side, idx, leaf_i = root, [], 1, 0, 0
    for ch in s:
        u = idx / max(1, n_f - 1)
        if ch == "F":
            lebar = cfg["tebal"] * (1 - 0.5 * u)
            n = Ruas(seg * rng.uniform(0.95, 1.05), lebar * 1.1, lebar, warna_batang, rng.uniform(-0.03, 0.03) * (1 + 2 * stres))
            cur.add(n)
            cur = n
            idx += 1
        elif ch in "+-":
            side = 1 if ch == "+" else -1
            n = Node("Cabang", rot=side * (1.25 - 0.62 * u + wilt * 0.35) * rng.uniform(0.95, 1.05))
            cur.add(n)
            cur = n
        elif ch == "L":
            uu = (idx - 1) / max(1, n_f - 1)
            L = cfg["Lmax"] * (.45 + .55 * math.sin(math.pi * min(1, .2 + .8 * uu) * .9)) * (1 - .3 * uu)
            L *= (0.6 + 0.4 * vigor) * rng.uniform(0.93, 1.07)
            kb = cfg["kuning_bawah"]
            alami = max(0.0, (kb - leaf_i) / kb) if kb else 0.0        # daun bawah menguning saat pemasakan
            kuning = clamp(0.75 * stres + alami * 0.85, 0, 1)
            lengkung = side * L * (.30 - .14 * uu + wilt * .15)
            cur.add(Daun(L, lengkung, kuning))
            leaf_i += 1
        elif ch == "[":
            stack.append((cur, side))
        elif ch == "]":
            cur, side = stack.pop()
        elif ch == "M":
            cur.add(Bunga(cfg["bunga"] * (0.6 + 0.4 * vigor), seed + 7))
    return root
