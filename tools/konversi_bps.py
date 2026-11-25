"""
Konversi tabel BPS Kabupaten Jember
"Banyaknya Curah Hujan Menurut Kecamatan, Stasiun Pengukur, dan Bulan"
menjadi data/iklim_jember.csv (format yang dibaca app.py).

Langkah pembersihan:
- baris stasiun tanpa angka (mis. Tamanan = "KABUPATEN BONDOWOSO") dilewati;
- baris stasiun yang tercatat dua kali dengan angka identik dihitung sekali;
- curah hujan kecamatan = rata-rata semua stasiun di kecamatan itu, per bulan.
Nilai asli BPS tidak diubah (termasuk nilai ekstrem); BPS menulis satuan "mm2", yang dimaksud mm.

Pakai:  python tools/konversi_bps.py
"""
import csv
import glob
import os
import re

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASUK = os.path.join(AKAR, "data", "bps", "bps_jember_curah_hujan_*.csv")
KELUAR = os.path.join(AKAR, "data", "iklim_jember.csv")
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def baca_tabel(path):
    """Hasil: {kecamatan: [[12 nilai], ...per stasiun]} dalam urutan tabel."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        baris = list(csv.reader(f))
    data, kec, terlewat = {}, None, []
    for r in baris:
        if len(r) < 17 or not r[0].strip() and not r[4].strip():
            continue
        if r[0].strip().isdigit():
            kec = r[1].strip()
        if kec is None or not r[4].strip():
            continue
        try:
            nilai = [float(x) for x in r[5:17]]
        except ValueError:
            terlewat.append(f"{kec}/{r[4].strip()}")
            continue
        stasiun = data.setdefault(kec, {})
        stasiun.setdefault((r[4].strip(), tuple(nilai)), nilai)   # duplikat identik -> sekali
    return {k: list(v.values()) for k, v in data.items()}, terlewat


def main():
    hasil = []
    for path in sorted(glob.glob(MASUK)):
        tahun = re.search(r"(\d{4})", os.path.basename(path)).group(1)
        data, terlewat = baca_tabel(path)
        sumber = (f"BPS Kabupaten Jember, Banyaknya Curah Hujan Menurut Kecamatan, Stasiun Pengukur, "
                  f"dan Bulan, {tahun} (jemberkab.bps.go.id; diakses 25-11-2026). Rata-rata stasiun per kecamatan.")
        for kec, stasiun in data.items():
            for i, nama in enumerate(BULAN):
                rata = sum(s[i] for s in stasiun) / len(stasiun)
                hasil.append({"tahun": tahun, "wilayah": kec, "bulan": nama,
                              "curah_hujan_mm": round(rata, 1), "jumlah_stasiun": len(stasiun),
                              "status_data": "RESMI (BPS)", "sumber": sumber})
        print(f"{tahun}: {len(data)} kecamatan, {sum(map(len, data.values()))} stasiun; dilewati: {terlewat}")
    with open(KELUAR, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hasil[0]))
        w.writeheader()
        w.writerows(hasil)
    print(f"{len(hasil)} baris -> {KELUAR}")


if __name__ == "__main__":
    main()
