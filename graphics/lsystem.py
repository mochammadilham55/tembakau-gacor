"""
PROCEDURAL MODELING: L-system untuk tembakau
============================================
Tembakau punya daun berseling (kiri-kanan) di sepanjang batang. Ini persis
diwakili aturan penulisan ulang berikut:

    Aksioma : A
    Aturan  : A -> F[+L]F[-L]A

    F : ruas batang   L : daun   + : belok kiri   - : belok kanan
    [ : simpan posisi ] : kembali   A : titik tumbuh   M : bunga (malai)

Tiap iterasi menambah 2 ruas dan 2 daun (satu kiri, satu kanan).
Jumlah iterasi ditentukan oleh fase pertumbuhan.
"""
ATURAN = {"A": "F[+L]F[-L]A"}


def ekspansi(aksioma, aturan, iterasi):
    s = aksioma
    for _ in range(iterasi):
        s = "".join(aturan.get(ch, ch) for ch in s)
    return s


def string_tembakau(iterasi, ada_bunga):
    s = ekspansi("A", ATURAN, iterasi)
    return s.replace("A", "M" if ada_bunga else "")
