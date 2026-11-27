from .util import clamp

MAX_HUJAN = 5000.0

ASUMSI = {
    "eto_mm_hari": 4.0,
    "hari_bulan": 30,
    "ambang_hujan_basah": 180.0,
    "batas_hujan_basah": 450.0,
    "ky_musim_fao": 0.9,
}

FASE = [
    {"nama": "Persemaian", "hari": "0-40 hari sebar", "ciri": "Bibit kecil dengan beberapa helai daun",
     "iter": 2, "Ht": 28, "Lmax": 36, "bunga": 0.0, "kuning_bawah": 0, "tebal": 3, "skala": 2.0, "akar": 0.18, "kc": 0.35, "wilt0": 0.0},
    {"nama": "Pindah tanam", "hari": "0-14 hari setelah tanam", "ciri": "Bibit baru di lahan, daun masih kecil dan mudah layu",
     "iter": 3, "Ht": 46, "Lmax": 54, "bunga": 0.0, "kuning_bawah": 0, "tebal": 4, "skala": 1.6, "akar": 0.3, "kc": 0.35, "wilt0": 0.5},
    {"nama": "Vegetatif", "hari": "15-45 hari setelah tanam", "ciri": "Batang meninggi, daun makin banyak dan lebar",
     "iter": 8, "Ht": 175, "Lmax": 92, "bunga": 0.0, "kuning_bawah": 0, "tebal": 6, "skala": 1.0, "akar": 0.65, "kc": 0.75, "wilt0": 0.0},
    {"nama": "Pembungaan dan pemangkasan", "hari": "45-65 hari setelah tanam", "ciri": "Bunga muncul di pucuk, lalu pucuk dipangkas",
     "iter": 12, "Ht": 262, "Lmax": 110, "bunga": 0.9, "kuning_bawah": 0, "tebal": 7, "skala": 1.0, "akar": 0.9, "kc": 1.1, "wilt0": 0.0},
    {"nama": "Pemasakan dan panen daun", "hari": "65-110 hari setelah tanam", "ciri": "Daun bawah menguning dan siap dipetik bertahap",
     "iter": 12, "Ht": 255, "Lmax": 106, "bunga": 0.0, "kuning_bawah": 6, "tebal": 7, "skala": 1.0, "akar": 1.0, "kc": 0.9, "wilt0": 0.1},
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
    eto = A["eto_mm_hari"] * A["hari_bulan"]
    etc = cfg["kc"] * eto
    f_air = clamp(hujan / etc, 0.0, 1.0)
    stres_kering = 1.0 - f_air
    lo = A["ambang_hujan_basah"]
    hi = A["batas_hujan_basah"]
    stres_basah = clamp((hujan - lo) / (hi - lo), 0.0, 1.0)
    vigor = 1.0 - max(stres_kering, stres_basah)
    catatan = [
        f"Kc FAO {cfg['kc']:.2f}; ETc skenario {etc:.0f} mm per 30 hari (ET0 asumsi {A['eto_mm_hari']:.1f} mm/hari)."
    ]
    if stres_kering > 0:
        catatan.append("Hujan kurang dari kebutuhan air skenario; bukan pengukuran stres aktual.")
    elif stres_basah > 0:
        catatan.append("Hujan tinggi: tekanan basah visual berdasarkan ambang asumsi, bukan model drainase.")
    else:
        catatan.append("Tidak ada tekanan air pada skenario ini; bukan jaminan kondisi tanaman aktual.")
    if fase == 1 and vigor < 0.6:
        catatan.append("Kelayuan pindah tanam merupakan parameter visual.")
    if fase == 4 and stres_basah > 0:
        catatan.append("Pada pemasakan daun, hujan berlebih dapat memengaruhi pemasakan; mutu daun tidak dihitung.")

    mutu = "Baik" if vigor >= 0.75 else "Sedang" if vigor >= 0.45 else "Rendah"
    return {
        "fase": fase, "nama": cfg["nama"], "hari": cfg["hari"], "ciri": cfg["ciri"],
        "faktor_air": round(f_air, 3), "kc": cfg["kc"],
        "eto_skenario_mm": eto, "etc_skenario_mm": round(etc, 2),
        "model_air": "fao_kc_skenario_bulanan",
        "vigor": round(vigor, 3), "stres_kering": round(stres_kering, 3), "stres_basah": round(stres_basah, 3), "stres": round(1 - vigor, 3),
        "indeks_kondisi": int(round(100 * vigor)),
        "jumlah_daun": 2 * cfg["iter"], "mutu": mutu, "kategori_simulasi": mutu,
        "wilt": round(clamp(cfg["wilt0"] + 0.9 * (1 - vigor), 0, 1), 3),
        "catatan": catatan,
    }
