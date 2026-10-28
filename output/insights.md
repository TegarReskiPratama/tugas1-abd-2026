# Insight Analisis Berita Indonesia 2017

Artikel bersih: 455,360. Input SHA-256: `ba3c4d94dc63a31d19d102127fbb993e80d097959600bb3cc2aca33a2f4fcea6`.

1. **Tren waktu:** 2017-08 mempunyai volume tertinggi 46,745 artikel (10.27% korpus), sedangkan 2017-09 terendah 25,177. Bulan volume tertinggi mencatat 1507.90 artikel/hari kalender. Perbedaan ini belum menjelaskan penyebab perubahan; periksa kontribusi sumber dan cakupan pengumpulan sebelum mengaitkannya dengan peristiwa (grafik 1, 7 dan 9).

2. **Distribusi dan anomali:** rata-rata panjang 272.35 kata melebihi median 246.00; P99 804.00 kata. Sebanyak 20,799 artikel (4.57%) ditandai IQR dan tetap disertakan. Median melengkapi rata-rata agar ringkasan panjang tidak hanya dipengaruhi ekor distribusi; flag tidak otomatis berarti salah (grafik 2 dan 10).

3. **Korelasi kunci:** Pearson r volume harian dengan rata-rata panjang artikel adalah -0.089 (negatif; 365 hari berartikel). Nilainya dekat nol, sehingga volume harian saja tidak menunjukkan hubungan linear yang kuat dengan panjang artikel. Koefisien ini menunjukkan asosiasi linear pada tingkat hari; tidak membuktikan bahwa beban publikasi mengubah panjang artikel. Periksa perubahan komposisi sumber sebelum membuat keputusan kapasitas (grafik 3 dan 6).

4. **Perilaku segmen:** 6 sumber tercatat. tribunnews.com terbesar (28.40%), dan lima sumber teratas 97.03% korpus. Rata-rata panjang per sumber berkisar 248.90 kata (liputan6.com) sampai 297.33 (kompas.com). Analisis gabungan perlu didampingi hasil per sumber untuk mengurangi dominasi sumber dengan volume besar (grafik 4, 6 dan 9).

5. **Rekomendasi praktis:** jadikan rata-rata hari kerja 1445.87 artikel/hari dan akhir pekan 756.51 sebagai baseline historis kapasitas pengolahan, dengan pemantauan khusus Rabu (1518.33/hari). Audit sampel dari 20,799 flag outlier, pantau coverage setiap sumber, dan validasi baseline menggunakan data terbaru sebelum penjadwalan operasional. Pola arsip 2017 tidak cukup untuk menetapkan jadwal saat ini (grafik 2, 6 dan 8).

6. **Pola musiman mingguan:** Rabu mempunyai rata-rata tertinggi (1518.33 artikel/hari kalender). Senin–Jumat 1445.87, dibanding Sabtu–Minggu 756.51. Denominator memperhitungkan perbedaan jumlah kejadian hari, termasuk hari kosong dalam arsip. Pola mingguan ini tidak membuktikan musim antartahun (grafik 5 dan 8).

7. **Pola jam:** Jam tercatat dengan artikel terbanyak adalah 15.00 (33,759 artikel; 7.41% dari 455,360 artikel dengan informasi jam). Sebanyak 0 artikel tanpa jam dikeluarkan dari heatmap. Waktu tanpa offset masih bergantung pada asumsi WIB (grafik 5).

8. **Kualitas data:** 455,678 artikel mentah menghasilkan 455,360 artikel bersih (99.93% dipertahankan), setelah mengarantina 52 dan menghapus 266 salinan duplikat. Jumlah baris direkonsiliasi; checksum hasil M2 cocok. Angka ini merangkum metadata cleaning, bukan proses cleaning baru di M3.

9. **Cakupan kalender:** artikel tersedia pada 365 dari 365 hari (100.00%), dengan 0 hari kosong. Coverage tanggal lengkap tidak menjamin seluruh artikel tiap media terkumpul; tetap periksa coverage per sumber (grafik 1 dan 9).

## Visualisasi Interaktif

- [1. Jumlah Artikel Harian dan Rata-rata 7 Hari](figures/01_daily_trend.html)
- [2. Distribusi Jumlah Kata per Artikel](figures/02_article_length_distribution.html)
- [3. Korelasi Metrik Harian (365 hari berartikel)](figures/03_daily_correlation.html)
- [4. Komposisi Sumber Artikel Terbesar](figures/04_source_composition.html)
- [5. Siklus Hari × Jam (455,360 artikel dengan jam)](figures/05_weekday_hour_heatmap.html)
- [6. Volume, Panjang Teks, dan Outlier Menurut Sumber](figures/06_source_multidimensional.html)
- [7. Jumlah Artikel per Bulan](figures/07_monthly_volume.html)
- [8. Intensitas Artikel Menurut Hari dalam Minggu](figures/08_weekday_pattern.html)
- [9. Volume Bulanan Lima Sumber Terbesar](figures/09_source_monthly_trend.html)
- [10. Rata-rata dan Median Panjang Artikel per Bulan](figures/10_monthly_article_length.html)

HTML dihasilkan secara lokal saat notebook dijalankan dan tidak disimpan di Git. Output Plotly tersimpan di notebook; buka di Jupyter untuk interaksi.

## Batas Interpretasi

Unit analisis adalah artikel dalam arsip, bukan peristiwa atau sensus publikasi Indonesia. Korelasi menggunakan agregat hari, bersifat deskriptif, dan tidak menyimpulkan sebab-akibat. Tidak tersedia koordinat terverifikasi. Timestamp tanpa offset diasumsikan WIB. Median/persentil memakai seluruh korpus bersih, sedangkan ambang IQR berasal dari artikel valid sebelum deduplikasi. Baseline 2017 perlu divalidasi sebelum diterapkan saat ini.
