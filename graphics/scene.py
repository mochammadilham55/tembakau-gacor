"""
HIERARCHICAL MODELING / SCENE GRAPH
===================================
Setiap objek visual adalah sebuah Node. Node punya transformasi LOKAL
(translasi, rotasi, skala) relatif terhadap induknya, dan boleh punya anak.

Saat digambar, transformasi induk otomatis diwariskan ke anak:

    M_dunia(anak) = M_dunia(induk) * M_lokal(anak)

Di Pycairo ini dikerjakan dengan ctx.save() / ctx.translate() / ctx.rotate() /
ctx.scale() / ctx.restore(), sehingga memutar satu cabang otomatis
memutar semua daun dan malai di atasnya.
"""


class Node:
    def __init__(self, name, x=0.0, y=0.0, rot=0.0, sx=1.0, sy=1.0, tip=(0.0, 0.0)):
        self.name = name
        self.x, self.y = x, y            # translasi lokal
        self.rot = rot                   # rotasi lokal (radian)
        self.sx, self.sy = sx, sy        # skala lokal
        self.tip = tip                   # titik tempat anak-anak dipasang (mis. ujung ruas)
        self.children = []

    def add(self, child):
        self.children.append(child)
        return child

    def draw(self, ctx):
        """Menggambar bentuk milik node ini (diisi oleh subclass). Default: tidak ada."""

    def render(self, ctx):
        ctx.save()
        ctx.translate(self.x, self.y)
        ctx.rotate(self.rot)
        ctx.scale(self.sx, self.sy)
        self.draw(ctx)
        if self.children:
            ctx.translate(*self.tip)     # anak dipasang di ujung node ini
            for child in self.children:
                child.render(ctx)
        ctx.restore()

    # ---------- ringkasan struktur (untuk diagram/penjelasan) ----------
    def count(self):
        return 1 + sum(c.count() for c in self.children)

    def to_dict(self, max_depth=4, _level=0):
        """Ringkasan pohon. Anak dengan nama sama digabung (diberi jumlah 'kali')."""
        d = {"nama": self.name, "jumlah_node": self.count()}
        if _level < max_depth and self.children:
            groups = {}
            for c in self.children:
                groups.setdefault(c.name, []).append(c)
            d["anak"] = []
            for name, items in groups.items():
                e = items[0].to_dict(max_depth, _level + 1)
                e["kali"] = len(items)
                d["anak"].append(e)
        return d
