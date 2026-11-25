"""
MODEL FASE PERTUMBUHAN TEMBAKAU (disederhanakan)
================================================
Model hanya memakai satu variabel cuaca: curah hujan bulanan (mm/bulan).
PENTING: semua angka pada ASUMSI dan FASE (rentang hari, ukuran, ambang hujan) adalah ASUMSI AWAL untuk simulasi, bukan data resmi. Ganti dengan
nilai dari literatur budidaya tembakau (Balitbangtan, jurnal) dan kutip di laporan.
"""
from .util import clamp

ASUMSI = {
    "hujan_optimum": (60.0, 180.0),    # mm/bulan (asumsi)
    "hujan_batas": (0.0, 450.0),       # di luar batas ini faktor air = 0
}

# iter: jumlah iterasi L-system (2 daun per iterasi); Ht/Lmax dalam piksel; skala: pembesaran tampilan
FASE = [
    {"nama": "Persemaian", "hari": "0-40 hari sebar", "ciri": "Bibit kecil dengan beberapa helai daun",
     "iter": 2, "Ht": 28, "Lmax": 36, "bunga": 0.0, "kuning_bawah": 0, "tebal": 3, "skala": 2.0, "akar": 0.18, "rentan": 1.0, "wilt0": 0.0},
    {"nama": "Pindah tanam", "hari": "0-14 hari setelah tanam", "ciri": "Bibit baru di lahan, daun masih kecil dan mudah layu",
     "iter": 3, "Ht": 46, "Lmax": 54, "bunga": 0.0, "kuning_bawah": 0, "tebal": 4, "skala": 1.6, "akar": 0.3, "rentan": 1.4, "wilt0": 0.5},
    {"nama": "Vegetatif", "hari": "15-45 hari setelah tanam", "ciri": "Batang meninggi, daun makin banyak dan lebar",
     "iter": 5, "Ht": 175, "Lmax": 92, "bunga": 0.0, "kuning_bawah": 0, "tebal": 6, "skala": 1.0, "akar": 0.65, "rentan": 1.0, "wilt0": 0.0},
    {"nama": "Pembungaan dan pemangkasan", "hari": "45-65 hari setelah tanam", "ciri": "Bunga muncul di pucuk, lalu pucuk dipangkas",
     "iter": 7, "Ht": 262, "Lmax": 110, "bunga": 0.9, "kuning_bawah": 0, "tebal": 7, "skala": 1.0, "akar": 0.9, "rentan": 1.1, "wilt0": 0.0},
    {"nama": "Pemasakan dan panen daun", "hari": "65-110 hari setelah tanam", "ciri": "Daun bawah menguning dan siap dipetik bertahap",
     "iter": 7, "Ht": 255, "Lmax": 106, "bunga": 0.0, "kuning_bawah": 6, "tebal": 7, "skala": 1.0, "akar": 1.0, "rentan": 1.2, "wilt0": 0.1},
]


def trapesium(x, a, b, c, d):
    """0 di luar [a, d]; naik linear a->b; 1 pada b..c; turun linear c->d."""
    if x <= a or x >= d:
        return 0.0
    if x < b:
        return (x - a) / (b - a)
    if x <= c:
        return 1.0
    return (d - x) / (d - c)


def hitung_kondisi(fase, hujan):
    A = ASUMSI
    fase = int(clamp(fase, 0, len(FASE) - 1))
    cfg = FASE[fase]
    hujan = clamp(float(hujan), 0, 1000)
    f_air = trapesium(hujan, A["hujan_batas"][0], A["hujan_optimum"][0], A["hujan_optimum"][1], A["hujan_batas"][1])
    dasar = 0.1 + 0.9 * f_air
    vigor = clamp(dasar ** cfg["rentan"], 0.0, 1.0)  # fase rentan: dampak stres lebih besar (asumsi)

    catatan = []
    lo, hi = A["hujan_optimum"]
    if hujan < lo:
        catatan.append(f"Curah hujan {hujan:.0f} mm/bulan di bawah kisaran optimum ({lo:.0f}-{hi:.0f}): tanaman kekurangan air.")
    elif hujan > hi:
        catatan.append(f"Curah hujan {hujan:.0f} mm/bulan di atas kisaran optimum ({lo:.0f}-{hi:.0f}): tanah terlalu basah.")
    if not catatan:
        catatan.append("Kondisi berada di kisaran optimum (menurut asumsi model).")
    if fase == 1 and vigor < 0.6:
        catatan.append("Fase pindah tanam rentan: bibit mudah layu bila kondisi kurang ideal (asumsi).")
    if fase == 4 and hujan > A["hujan_optimum"][1]:
        catatan.append("Pada pemasakan daun, hujan berlebih dapat menurunkan mutu daun (asumsi).")

    mutu = "Baik" if vigor >= 0.75 else "Sedang" if vigor >= 0.45 else "Rendah"
    return {
        "fase": fase, "nama": cfg["nama"], "hari": cfg["hari"], "ciri": cfg["ciri"],
        "faktor_air": round(f_air, 3),
        "vigor": round(vigor, 3), "stres": round(1 - vigor, 3),
        "indeks_kondisi": int(round(100 * vigor)),
        "jumlah_daun": 2 * cfg["iter"], "mutu": mutu,
        "wilt": round(clamp(cfg["wilt0"] + 0.9 * (1 - vigor), 0, 1), 3),
        "catatan": catatan,
    }
