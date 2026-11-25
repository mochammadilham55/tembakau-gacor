from .util import clamp

MAX_HUJAN = 5000.0

ASUMSI = {
    "hujan_optimum": (60.0, 180.0),
    "hujan_batas": (0.0, 450.0),
}

FASE = [
    {"nama": "Persemaian", "hari": "0-40 hari sebar", "ciri": "Bibit kecil dengan beberapa helai daun",
     "iter": 2, "Ht": 28, "Lmax": 36, "bunga": 0.0, "kuning_bawah": 0, "tebal": 3, "skala": 2.0, "akar": 0.18, "rentan": 1.0, "wilt0": 0.0},
    {"nama": "Pindah tanam", "hari": "0-14 hari setelah tanam", "ciri": "Bibit baru di lahan, daun masih kecil dan mudah layu",
     "iter": 3, "Ht": 46, "Lmax": 54, "bunga": 0.0, "kuning_bawah": 0, "tebal": 4, "skala": 1.6, "akar": 0.3, "rentan": 1.4, "wilt0": 0.5},
    {"nama": "Vegetatif", "hari": "15-45 hari setelah tanam", "ciri": "Batang meninggi, daun makin banyak dan lebar",
     "iter": 8, "Ht": 175, "Lmax": 92, "bunga": 0.0, "kuning_bawah": 0, "tebal": 6, "skala": 1.0, "akar": 0.65, "rentan": 1.0, "wilt0": 0.0},
    {"nama": "Pembungaan dan pemangkasan", "hari": "45-65 hari setelah tanam", "ciri": "Bunga muncul di pucuk, lalu pucuk dipangkas",
     "iter": 12, "Ht": 262, "Lmax": 110, "bunga": 0.9, "kuning_bawah": 0, "tebal": 7, "skala": 1.0, "akar": 0.9, "rentan": 1.1, "wilt0": 0.0},
    {"nama": "Pemasakan dan panen daun", "hari": "65-110 hari setelah tanam", "ciri": "Daun bawah menguning dan siap dipetik bertahap",
     "iter": 12, "Ht": 255, "Lmax": 106, "bunga": 0.0, "kuning_bawah": 6, "tebal": 7, "skala": 1.0, "akar": 1.0, "rentan": 1.2, "wilt0": 0.1},
]


def trapesium(x, a, b, c, d):
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
    hujan = clamp(float(hujan), 0, MAX_HUJAN)
    f_air = trapesium(hujan, A["hujan_batas"][0], A["hujan_optimum"][0], A["hujan_optimum"][1], A["hujan_batas"][1])
    dasar = 0.1 + 0.9 * f_air
    vigor = clamp(dasar ** cfg["rentan"], 0.0, 1.0)

    stres_kering = (1 - vigor) if hujan < A["hujan_optimum"][0] else 0.0
    stres_basah = (1 - vigor) if hujan > A["hujan_optimum"][1] else 0.0
    catatan = []
    lo, hi = A["hujan_optimum"]
    if hujan < lo:
        catatan.append(f"Curah hujan {hujan:.0f} mm/bulan di bawah kisaran optimum ({lo:.0f}-{hi:.0f}): skenario kekurangan air menurut model.")
    elif hujan > hi:
        catatan.append(f"Curah hujan {hujan:.0f} mm/bulan di atas kisaran optimum ({lo:.0f}-{hi:.0f}): skenario kelebihan air menurut model.")
    if not catatan:
        catatan.append("Kondisi berada di kisaran optimum (menurut asumsi model).")
    if fase == 1 and vigor < 0.6:
        catatan.append("Fase pindah tanam rentan: bibit mudah layu bila kondisi kurang ideal (asumsi).")
    if fase == 4 and hujan > A["hujan_optimum"][1]:
        catatan.append("Pada pemasakan daun, hujan berlebih dapat memengaruhi pemasakan; mutu daun tidak dihitung.")

    mutu = "Baik" if vigor >= 0.75 else "Sedang" if vigor >= 0.45 else "Rendah"
    return {
        "fase": fase, "nama": cfg["nama"], "hari": cfg["hari"], "ciri": cfg["ciri"],
        "faktor_air": round(f_air, 3),
        "vigor": round(vigor, 3), "stres_kering": round(stres_kering, 3), "stres_basah": round(stres_basah, 3), "stres": round(1 - vigor, 3),
        "indeks_kondisi": int(round(100 * vigor)),
        "jumlah_daun": 2 * cfg["iter"], "mutu": mutu, "kategori_simulasi": mutu,
        "wilt": round(clamp(cfg["wilt0"] + 0.9 * (1 - vigor), 0, 1), 3),
        "catatan": catatan,
    }
