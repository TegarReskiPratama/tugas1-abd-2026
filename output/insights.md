# Insight Analisis Berita Indonesia 2017

Artikel bersih: 455,360. Input SHA-256: `ba3c4d94dc63a31d19d102127fbb993e80d097959600bb3cc2aca33a2f4fcea6`.

1. Volume bulanan: 2017-08 tertinggi dengan 46,745 artikel (10.27% korpus), sedangkan 2017-09 terendah dengan 25,177. Rata-rata pada bulan tertinggi adalah 1507.90 artikel/hari kalender (grafik 2).

2. Pola hari: Rabu mempunyai rata-rata tertinggi (1518.33 artikel/hari kalender). Rata-rata Senin–Jumat 1445.87, dibanding Sabtu–Minggu 756.51. Perhitungan memperhitungkan jumlah hari masing-masing (grafik 3).

3. Konsentrasi sumber: 6 label sumber tercatat. Lima label teratas menyumbang 97.03% artikel; sumber terbesar tribunnews.com menyumbang 28.40%. Komposisi ini membatasi generalisasi terhadap sumber lain (grafik 4 dan 7).

4. Jam tercatat dengan artikel terbanyak adalah 15.00 (33,759 artikel; 7.41% dari 455,360 artikel dengan informasi jam). Sebanyak 0 artikel tanpa jam dikeluarkan dari heatmap. Lihat grafik 5.

5. Panjang teks: rata-rata 272.35 kata, median 246.00, dan persentil 99 804.00. Sebanyak 20,799 artikel (4.57%) ditandai outlier IQR dan tetap dianalisis menggunakan panjang asli (grafik 6 dan 8).

6. Kualitas data: 455,678 artikel mentah menghasilkan 455,360 artikel bersih (99.93% dipertahankan), setelah mengarantina 52 artikel dan menghapus 266 salinan duplikat. Jumlah baris telah direkonsiliasi dan seluruh validasi SQL lulus (notebook 02).

7. Cakupan waktu: arsip memiliki artikel pada 365 dari 365 hari (100.00%). Ada 0 hari tanpa artikel dalam dataset. Hari kosong dapat mencerminkan keterbatasan pengumpulan; penyebabnya perlu sumber tambahan (grafik 1).

## Visualisasi Interaktif

- [1. Jumlah Artikel Harian dan Rata-rata 7 Hari](figures/01_daily_trend.html)
- [2. Jumlah Artikel per Bulan](figures/02_monthly_volume.html)
- [3. Intensitas Artikel Menurut Hari dalam Minggu](figures/03_weekday_pattern.html)
- [4. Sepuluh Sumber dengan Artikel Terbanyak](figures/04_source_composition.html)
- [5. Hari × Jam Publikasi (455,360 artikel dengan jam)](figures/05_weekday_hour_heatmap.html)
- [6. Distribusi Jumlah Kata per Artikel](figures/06_article_length_distribution.html)
- [7. Volume Bulanan Lima Sumber Terbesar](figures/07_source_monthly_trend.html)
- [8. Rata-rata dan Median Panjang Artikel per Bulan](figures/08_monthly_article_length.html)

## Batas Interpretasi

Unit analisis adalah artikel, bukan peristiwa unik. Dataset merupakan arsip pengumpulan, bukan sensus seluruh publikasi Indonesia. Tidak ada inferensi kausal. Timestamp tanpa offset diasumsikan mengikuti jam WIB; jam yang tidak tersedia tidak diimputasi. Median dan persentil menghitung seluruh korpus, sementara IQR berasal dari artikel valid sebelum deduplikasi.
