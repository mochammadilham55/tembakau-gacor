# Dasar dan batas ilmiah model air

Data BPS adalah curah hujan bulanan, bukan kelembapan tanah atau evapotranspirasi aktual. FAO Crop Water Needs, tabel 8, memberi Kc tembakau awal 0,35; perkembangan 0,75; pertengahan 1,10; akhir 0,90. Pemetaan ke lima fase aplikasi adalah 0,35 (persemaian, ekstrapolasi visual), 0,35 (pindah tanam), 0,75 (vegetatif), 1,10 (pembungaan), 0,90 (pemasakan). Pemetaan fase belum dikalibrasi untuk Na-Oogst.

ET0 skenario = 4 mm/hari x 30 hari = 120 mm. Ini asumsi, bukan ET0 terukur Jember. ETc = Kc x ET0. Kebutuhan skenario masing-masing 42, 42, 90, 132, 108 mm per 30 hari. Seluruh hujan diasumsikan tersedia sebagai pendekatan kasar; irigasi, limpasan, simpanan tanah, distribusi hujan dan drainase tidak dihitung. Faktor air = clamp(hujan/ETc, 0, 1); stres kering visual = 1 - faktor air.

Stres basah visual = clamp((hujan - 180)/(450 - 180), 0, 1). Kedua ambang masih heuristik dan tidak boleh diartikan sebagai ambang genangan ilmiah. Vigor visual = 1 - max(stres kering, stres basah). Indeks, kategori, warna, kelayuan, umur, ukuran piksel dan jumlah daun masih parameter visual, bukan hasil kalibrasi. Ky FAO total musim 0,9 dicatat sebagai referensi, tidak digunakan untuk menghitung stres bulanan karena Ky menghubungkan defisit ET dengan hasil panen, bukan stres fisiologis. Penelitian Jember 2021 mendukung hubungan hujan dan produksi, tidak memberikan koefisien stres tanaman.

## Referensi
- FAO Crop Water Needs, tabel 8: https://www.fao.org/4/s2022e/s2022e07.htm
- FAO Irrigation Scheduling, tabel 12: https://www.fao.org/4/x5647e/x5647e0e.htm
- Setyoningrum dkk. (2021): https://doi.org/10.25047/agropross.2021.203
- Kandidat referensi morfologi lokal: https://garuda.kemdiktisaintek.go.id/documents/detail/4975076
- Kandidat respons kekeringan: https://doi.org/10.1007/s10725-025-01318-2

Validasi berikutnya memerlukan ET0 lokal, hujan efektif, data tanah dan pengamatan tanaman independen. Referensi kandidat morfologi dan kekeringan belum digunakan sebagai dasar angka.
