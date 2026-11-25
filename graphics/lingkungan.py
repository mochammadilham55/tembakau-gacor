"""
Latar: langit, tanah (penampang), akar, cuaca. Semua prosedural (seed) dan
memakai teknik Pycairo: gradient, clipping, masking, alpha, OPERATOR_MULTIPLY.
"""
import math
import random

import cairo

from .scene import Node
from .util import clamp, mix, rgb255

W, H, GY = 960, 640, 430          # lebar, tinggi gambar, garis permukaan tanah
CX = W // 2


class Langit(Node):
    def __init__(self, hujan, seed):
        super().__init__("Langit")
        self.seed = seed
        self.awan = clamp(hujan / 400.0, 0, 1)
        self.panas = clamp((70 - hujan) / 70.0, 0, 1)    # bulan kering: langit cerah & terik

    def draw(self, ctx):
        rng = random.Random(self.seed + 11)
        atas = mix(rgb255(92, 168, 232), rgb255(98, 108, 120), self.awan * 0.9)
        bawah = mix(rgb255(206, 234, 249), rgb255(170, 178, 186), self.awan * 0.9)
        bawah = mix(bawah, rgb255(250, 226, 170), self.panas * 0.5 * (1 - self.awan))
        g = cairo.LinearGradient(0, 0, 0, GY)
        g.add_color_stop_rgb(0, *atas)
        g.add_color_stop_rgb(1, *bawah)
        ctx.rectangle(0, 0, W, GY + 4)
        ctx.set_source(g)
        ctx.fill()
        a = 0.95 * (1 - 0.85 * self.awan)                      # matahari (radial gradient)
        sun = mix(rgb255(255, 248, 210), rgb255(255, 190, 90), self.panas)
        rg = cairo.RadialGradient(830, 80, 6, 830, 80, 170)
        rg.add_color_stop_rgba(0, *sun, a)
        rg.add_color_stop_rgba(0.25, *sun, a * 0.45)
        rg.add_color_stop_rgba(1, *sun, 0)
        ctx.set_source(rg)
        ctx.arc(830, 80, 170, 0, 2 * math.pi)
        ctx.fill()
        warna_awan = mix(rgb255(255, 255, 255), rgb255(120, 128, 138), self.awan)
        for _ in range(2 + int(6 * self.awan)):                 # awan: MASK gradien
            cx, cy = rng.uniform(-30, W + 30), rng.uniform(25, GY - 190)
            s = rng.uniform(0.7, 1.4) * (0.8 + 0.6 * self.awan)
            ctx.push_group()
            for _ in range(7):
                ctx.arc(cx + rng.uniform(-60, 60) * s, cy + rng.uniform(-12, 12) * s, rng.uniform(18, 36) * s, 0, 2 * math.pi)
                ctx.set_source_rgb(*warna_awan)
                ctx.fill()
            ctx.pop_group_to_source()
            m = cairo.LinearGradient(0, cy - 38 * s, 0, cy + 38 * s)
            m.add_color_stop_rgba(0, 0, 0, 0, 0.95)
            m.add_color_stop_rgba(1, 0, 0, 0, 0.25)
            ctx.mask(m)
        f = [rng.uniform(0.004, 0.011) for _ in range(3)]
        ph = [rng.uniform(0, 6.28) for _ in range(3)]
        for i, (col, tinggi, base) in enumerate(((rgb255(124, 178, 150), 60, 30), (rgb255(96, 158, 100), 34, 12))):
            ctx.move_to(0, GY + 4)
            for x in range(0, W + 8, 8):
                y = GY - base - tinggi * (0.5 + 0.5 * math.sin(f[i] * x * (1 + i) + ph[i])) - 5 * math.sin(f[2] * 3 * x + ph[2])
                ctx.line_to(x, y)
            ctx.line_to(W, GY + 4)
            ctx.close_path()
            ctx.set_source_rgba(*mix(col, rgb255(160, 170, 175), self.awan * 0.5), 0.96)
            ctx.fill()
        rum = cairo.LinearGradient(0, GY - 16, 0, GY + 6)
        rum.add_color_stop_rgb(0, *rgb255(120, 172, 84))
        rum.add_color_stop_rgb(1, *rgb255(70, 110, 50))
        ctx.rectangle(0, GY - 12, W, 20)
        ctx.set_source(rum)
        ctx.fill()


class Tanah(Node):
    """Penampang tanah berlapis. Kelembapan = overlay alpha biru; retakan bila kering."""
    def __init__(self, hujan, seed):
        super().__init__("Tanah")
        self.hujan, self.seed = hujan, seed

    def draw(self, ctx):
        rng = random.Random(self.seed + 23)
        kering = clamp((70 - self.hujan) / 70.0, 0, 1)
        basah = clamp(self.hujan / 300.0, 0, 1)
        lapis = [(GY + 6, GY + 90, rgb255(88, 62, 40)), (GY + 90, GY + 150, rgb255(124, 90, 58)), (GY + 150, H, rgb255(158, 122, 82))]
        for a, b, col in lapis:
            col = mix(mix(col, rgb255(200, 170, 120), kering * 0.45), (0, 0, 0), basah * 0.18)
            ctx.rectangle(0, a, W, b - a)
            ctx.set_source_rgb(*col)
            ctx.fill()
            for _ in range(110):
                ctx.arc(rng.uniform(0, W), rng.uniform(a, b), rng.uniform(.8, 2.3), 0, 2 * math.pi)
                ctx.set_source_rgba(0, 0, 0, .13) if rng.random() < .5 else ctx.set_source_rgba(1, 1, 1, .07)
                ctx.fill()
        if kering > 0.05:
            ctx.save()
            ctx.rectangle(0, GY + 6, W, 150)               # CLIPPING retakan ke lapisan atas
            ctx.clip()
            ctx.set_source_rgba(0.08, 0.05, 0.03, 0.55 * kering)
            ctx.set_line_width(1.6)
            for _ in range(int(8 + 18 * kering)):
                x, y, ang = rng.uniform(0, W), GY + 8, rng.uniform(1.0, 2.1)
                ctx.move_to(x, y)
                for _ in range(rng.randint(4, 9)):
                    ang += rng.uniform(-0.5, 0.5)
                    x += math.cos(ang) * 11
                    y += abs(math.sin(ang)) * 11
                    ctx.line_to(x, y)
                ctx.stroke()
            ctx.restore()
        # Genangan hanya ilustrasi skenario hujan ekstrem, bukan estimasi hidrologi.
        genang = clamp((self.hujan - 450) / 300, 0, 1)
        if genang > 0:
            ctx.set_source_rgba(.30, .55, .75, .65 * genang)
            ctx.rectangle(0, GY + 2, W, 8)
            ctx.fill()
        wet = cairo.LinearGradient(0, GY + 6, 0, GY + 170)  # alpha blending: kelembapan
        wet.add_color_stop_rgba(0, 0.25, 0.5, 0.85, 0.5 * basah)
        wet.add_color_stop_rgba(1, 0.25, 0.5, 0.85, 0)
        ctx.rectangle(0, GY + 6, W, 164)
        ctx.set_source(wet)
        ctx.fill()


class Akar(Node):
    """Akar tunggang + akar lateral: percabangan rekursif prosedural."""
    def __init__(self, besar, vigor, seed):
        super().__init__("Akar", x=CX, y=GY + 8)
        self.besar, self.vigor, self.seed = besar, vigor, seed

    def _cabang(self, ctx, rng, x, y, ang, pj, lebar, depth):
        if depth == 0 or pj < 5:
            return
        n, px, py = 4, x, y
        for i in range(n):
            ang += rng.uniform(-.3, .3) + (math.pi / 2 - ang) * .08
            nx, ny = px + math.cos(ang) * pj / n, py + math.sin(ang) * pj / n
            if ny > H - 8 - (GY + 8) or abs(nx) > W / 2 - 8:
                return
            ctx.set_line_width(max(.7, lebar * (1 - i / (n * 1.6))))
            ctx.set_source_rgba(.93, .85, .68, .95)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(px, py)
            ctx.line_to(nx, ny)
            ctx.stroke()
            if i >= 1 and rng.random() < .7:
                self._cabang(ctx, rng, nx, ny, ang + rng.choice((-1, 1)) * rng.uniform(.5, 1.0), pj * .55, lebar * .6, depth - 1)
            px, py = nx, ny

    def draw(self, ctx):
        rng = random.Random(self.seed + 31)
        sc = self.besar * (0.6 + 0.4 * self.vigor)
        self._cabang(ctx, rng, 0, 0, math.pi / 2, 110 * sc + 24, 4.2 * sc + 1.2, 4)
        for _ in range(int(3 + 8 * sc)):
            self._cabang(ctx, rng, rng.uniform(-8, 8), 2, math.pi / 2 + rng.choice((-1, 1)) * rng.uniform(.9, 1.35),
                         60 * sc + 18, 2.4 * sc + .8, 4)


class Cuaca(Node):
    """Lapisan atas: hujan, tint tekanan (MULTIPLY), vinyet."""
    def __init__(self, stres, hujan, seed):
        super().__init__("Cuaca")
        self.stres, self.hujan, self.seed = stres, hujan, seed

    def draw(self, ctx):
        rng = random.Random(self.seed + 37)
        hi = clamp((self.hujan - 240) / 260.0, 0, 1)
        if hi > 0:
            ctx.set_source_rgba(0.85, 0.9, 0.97, 0.35 + 0.3 * hi)
            ctx.set_line_width(1.1)
            for _ in range(int(120 + 650 * hi)):
                x, y = rng.uniform(-40, W), rng.uniform(-20, GY + 4)
                p = rng.uniform(10, 24)
                ctx.move_to(x, y)
                ctx.line_to(x - p * .25, y + p)
            ctx.stroke()
        if self.stres > 0.02:
            ctx.save()
            ctx.set_operator(cairo.OPERATOR_MULTIPLY)
            ctx.set_source_rgba(0.95, 0.82, 0.55, clamp(self.stres * 0.45, 0, 0.45))
            ctx.rectangle(0, 0, W, GY + 6)
            ctx.fill()
            ctx.restore()
        v = cairo.RadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, W * 0.7)
        v.add_color_stop_rgba(0, 0, 0, 0, 0)
        v.add_color_stop_rgba(1, 0, 0, 0, 0.3)
        ctx.rectangle(0, 0, W, H)
        ctx.set_source(v)
        ctx.fill()
