# TembakauGacor (Flask + Pycairo)

Simulasi interaktif pertumbuhan daun tembakau berdasarkan curah hujan, dalam 5 fase.
Backend Flask merender gambar dengan **Pycairo**; browser menampilkan gambar,
slider curah hujan, pilihan data BPS (tahun, kecamatan, bulan), dan pilihan fase.

## Menjalankan
```bash
pip install -r requirements.txt     # Linux: sudo apt install libcairo2-dev pkg-config python3-dev dulu
python app.py                       # buka http://127.0.0.1:5000
```
Windows: `pip install pycairo` biasanya sudah membawa cairo (wheel). Jika gagal, pakai WSL/Conda.

## Fase (asumsi)
1 Persemaian, 2 Pindah tanam, 3 Vegetatif, 4 Pembungaan dan pemangkasan, 5 Pemasakan dan panen daun.
Rentang hari dan ciri tiap fase ada di `graphics/growth.py` (`FASE`).

## Teknik Grafika Komputer
| Teknik | Lokasi |
|---|---|
| Hierarchical modeling / Scene graph | `graphics/scene.py` (`Node`); pohon Lahan > Langit, Tanah, Akar, Tanaman > Ruas > Cabang > Daun / Bunga, Cuaca |
| Procedural modeling | L-system `A -> F[+L]F[-L]A` (`graphics/lsystem.py`, `graphics/tanaman.py`); akar rekursif, awan, bukit, retakan tanah, hujan acak dengan seed (`graphics/lingkungan.py`) |
| Transformasi 2D | `translate/rotate/scale` di `Node.render` |
| Color blending / compositing | gradien, alpha kelembapan tanah, `OPERATOR_MULTIPLY` tint stres (`Cuaca`) |
| Clipping dan masking | `ctx.clip` retakan tanah; `push_group` + `ctx.mask` untuk awan |
| Pycairo | seluruh gambar: `ImageSurface`, `Context`, `LinearGradient`, `RadialGradient`, kurva Bezier |

## Data
Model hanya memakai **curah hujan bulanan (mm/bulan)**; variabel suhu sudah dihapus.

- `data/bps/bps_jember_curah_hujan_2023.csv`, `..._2025.csv`: tabel asli BPS Kabupaten Jember
  "Banyaknya Curah Hujan Menurut Kecamatan, Stasiun Pengukur, dan Bulan" (jemberkab.bps.go.id, diakses 25-11-2026).
  BPS menulis satuan "mm2"; yang dimaksud mm.
- `data/iklim_jember.csv`: hasil `python tools/konversi_bps.py` (dibaca aplikasi). Kolom:
  `tahun,wilayah,bulan,curah_hujan_mm,jumlah_stasiun,status_data,sumber`; 31 kecamatan x 12 bulan per tahun,
  nilai = rata-rata stasiun di kecamatan itu. Stasiun Tamanan (tanpa angka, "KABUPATEN BONDOWOSO") dilewati;
  baris stasiun dobel (Kencong 2025) dihitung sekali. Nilai asli tidak diubah.
- Catatan mutu data: 2025 stasiun "Ajung" (Kec. Kalisat) Januari 1.207 mm sangat tinggi dibanding sekitarnya;
  2023 beberapa stasiun berangka sama persis untuk Okt-Des (Puger, Grenden, Balung, dll.). Sebutkan di laporan.
- Tambah tahun lain: unduh tabel BPS yang sama sebagai CSV ke `data/bps/bps_jember_curah_hujan_<tahun>.csv`,
  lalu jalankan ulang `python tools/konversi_bps.py`.
- `data/iklim_contoh.csv`: data SINTETIS lama, tidak lagi dipakai aplikasi.

## Asumsi model (bukan data resmi)
Kisaran optimum hujan (60-180 mm/bulan), ambang batas (0-450 mm), rentang hari tiap fase,
serta sensitivitas per fase ada di `graphics/growth.py`. Ganti dengan nilai dari literatur budidaya
tembakau dan kutip di daftar pustaka.

## Struktur
```
app.py           route Flask (/, /render.png, /api/info, /api/fase, /api/data)
graphics/        scene.py, lsystem.py, growth.py, tanaman.py, lingkungan.py, renderer.py, util.py
tools/           konversi_bps.py (tabel BPS -> data/iklim_jember.csv)
templates/ static/ data/ (data/bps = tabel asli BPS)
```
