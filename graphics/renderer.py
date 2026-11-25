import io
from functools import lru_cache

import cairo

from .growth import FASE, hitung_kondisi
from .lingkungan import CX, GY, H, W, Akar, Cuaca, Langit, Tanah
from .scene import Node
from .tanaman import bangun_tanaman


def bangun_scene(fase, hujan, seed):
    k = hitung_kondisi(fase, hujan)
    cfg = FASE[k["fase"]]
    lahan = Node("Lahan")
    lahan.add(Langit(hujan, seed))
    lahan.add(Tanah(hujan, seed))
    lahan.add(Akar(cfg["akar"], k["vigor"], seed))
    tan = bangun_tanaman(k, cfg, seed)
    tan.x, tan.y = CX, GY + 8
    if cfg["nama"] == "Persemaian":
        pot = Node("Polibag", x=CX, y=GY + 2)
        pot.draw = lambda ctx: (ctx.rectangle(-34, -6, 68, 22), ctx.set_source_rgb(0.27, 0.27, 0.3), ctx.fill())
        lahan.add(pot)
    lahan.add(tan)
    lahan.add(Cuaca(k["stres"], hujan, seed))
    return lahan, k


@lru_cache(maxsize=16)
def render_png(fase, hujan, seed=1):
    lahan, _ = bangun_scene(fase, hujan, seed)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    lahan.render(ctx)
    buf = io.BytesIO()
    surf.write_to_png(buf)
    return buf.getvalue()


def info_scene(fase, hujan, seed=1):
    lahan, k = bangun_scene(fase, hujan, seed)
    return k, lahan.count(), lahan.to_dict(max_depth=32)
