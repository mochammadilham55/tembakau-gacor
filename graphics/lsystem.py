ATURAN = {"A": "F[+L]F[-L]A"}


def ekspansi(aksioma, aturan, iterasi):
    s = aksioma
    for _ in range(iterasi):
        s = "".join(aturan.get(ch, ch) for ch in s)
    return s


def string_tembakau(iterasi, ada_bunga):
    s = ekspansi("A", ATURAN, iterasi)
    return s.replace("A", "M" if ada_bunga else "")
