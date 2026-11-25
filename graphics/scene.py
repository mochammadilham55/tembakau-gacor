

class Node:
    def __init__(self, name, x=0.0, y=0.0, rot=0.0, sx=1.0, sy=1.0, tip=(0.0, 0.0)):
        self.name = name
        self.x, self.y = x, y
        self.rot = rot
        self.sx, self.sy = sx, sy
        self.tip = tip
        self.children = []

    def add(self, child):
        self.children.append(child)
        return child

    def draw(self, ctx):
        pass

    def render(self, ctx):
        ctx.save()
        ctx.translate(self.x, self.y)
        ctx.rotate(self.rot)
        ctx.scale(self.sx, self.sy)
        self.draw(ctx)
        if self.children:
            ctx.translate(*self.tip)
            for child in self.children:
                child.render(ctx)
        ctx.restore()

    def count(self):
        return 1 + sum(c.count() for c in self.children)

    def to_dict(self, max_depth=4, _level=0):
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
