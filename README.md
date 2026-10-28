# Tugas 1: Eksplorasi dan Analisis Dataset Besar Indonesia

**Tegar Reski Pratama — NIM 202310370311215**  
Mata kuliah Analisis Big Data, Informatika, Universitas Muhammadiyah Malang.

Proyek ini menganalisis pola waktu publikasi dan karakteristik teks pada **Indonesian News Articles Published at 2017** dari Kaggle. Struktur, nama notebook, milestone, dan aturan teknis mengikuti [template UMM-GURU](https://github.com/UMM-GURU/tugas1-abd-2026).

**Status Milestone 3:** notebook mengikuti empat bagian template yang diberikan, telah dijalankan pada seluruh **455.360 artikel bersih**, dan menyimpan **10 grafik Plotly interaktif serta 9 insight berbasis data**. Artefak Milestone 1 dan 2 yang sudah tersedia diperiksa melalui metadata dan checksum; kedua notebook tersebut tidak dijalankan ulang dalam perubahan ini. CSV asli berukuran **1.371.437.745 byte** dan memuat **455.678 artikel**, sehingga memenuhi syarat ukuran dataset. Docker image belum dibangun atau diuji dalam perubahan ini.

## Milestone

| Tahap | Target | Implementasi dan bukti |
|---|---|---|
| Milestone 1 | Pertemuan 3 | Dokumentasi `data/README.md`, notebook `01_data_profiling.ipynb`, pemeriksaan CSV >= 500 MB atau > 1 juta baris, SHA-256, profil Polars dan DuckDB, salinan Parquet |
| Milestone 2 | Pertemuan 5 | Notebook `02_data_cleaning.ipynb`, cleaning Polars, `SUMMARIZE` sebelum/sesudah, karantina, deduplikasi, flag IQR, dan validasi SQL |
| Milestone 3 | Pertemuan 8 | Notebook `03_eda_and_insights.ipynb` dengan output eksekusi, analisis temporal/windowing, 10 grafik interaktif Plotly, 9 insight, tabel EDA, dan ringkasan hasil |
| Final | Pertemuan 10 | Dockerfile, dependency yang dipatok, dokumentasi, pemeriksaan hasil, serta riwayat commit tiap milestone |

## Pertanyaan Analisis

1. Bagaimana volume artikel berubah per hari dan bulan selama 2017?
2. Apakah intensitas artikel berbeda menurut hari dan jam publikasi?
3. Seberapa terkonsentrasi artikel pada sumber tertentu?
4. Bagaimana distribusi dan perubahan panjang artikel?
5. Berapa banyak artikel dikarantina, terduplikasi, dan ditandai outlier?
6. Bagaimana hubungan volume harian, rata-rata panjang artikel, dan proporsi outlier, serta perbedaan karakteristik antarsumber?

Unit analisis adalah satu artikel, bukan satu peristiwa. Analisis menggambarkan arsip yang terkumpul dan tidak menganggap dataset sebagai sensus seluruh berita Indonesia. Dataset tidak menyediakan koordinat yang terverifikasi, sehingga pendekatan yang dipilih adalah **analisis temporal**.

## Struktur Repository

```text
.
├── .github/workflows/lint_check.yml
├── data/
│   ├── README.md
│   ├── raw/mq_news.csv                   # unduh sendiri; tidak masuk Git
│   └── processed/                       # dihasilkan notebook; tidak masuk Git
├── notebooks/
│   ├── 01_data_profiling.ipynb
│   ├── 02_data_cleaning.ipynb
│   └── 03_eda_and_insights.ipynb
├── output/
│   ├── figures/                         # 10 HTML interaktif; dibuat ulang saat run
│   ├── profiling_summary.json
│   ├── cleaning_summary.json
│   ├── eda_summary.json
│   ├── eda_*.csv                        # tabel agregasi kecil hasil EDA
│   └── insights.md
├── src/
│   ├── __init__.py
│   ├── common.py
│   └── dataset.py
├── scripts/
│   ├── validate_notebooks.py
│   └── validate_milestone3.py
├── .dockerignore
├── Dockerfile
├── requirements.txt
└── README.md
```

Berkas pada `output/` selain `.gitkeep` dihasilkan saat eksekusi. Notebook dengan output grafik interaktif, ringkasan JSON, tabel agregasi EDA kecil, dan laporan insight disertakan sebagai bukti hasil. CSV asli, Parquet, dan HTML besar tidak disertakan dalam commit. Notebook mengadaptasi template yang diberikan pengguna; logika dataset yang digunakan berpusat di `src/dataset.py`.

## Dataset dan Penanganan Data

Sumber dan petunjuk unduh lengkap tersedia di [data/README.md](data/README.md). Unduh **CSV lengkap** `mq_news.csv`, ekstrak, lalu simpan di `data/raw/mq_news.csv`. Syarat skala dinilai dari ukuran CSV setelah ekstraksi atau jumlah record CSV sebenarnya; bukan ukuran ZIP, jumlah baris fisik teks, atau ukuran Parquet terkompresi.

Notebook 01 membaca CSV dengan `scan_csv`, memeriksa skala, mencatat header/checksum, dan memakai `sink_parquet` untuk salinan kolom analisis. Notebook 02 memakai lazy expressions Polars dan menyimpan tahap normalisasi agar transformasi teks tidak diulang pada setiap agregasi. DuckDB membaca Parquet langsung dan dibatasi 2 GB secara default; spill sementara berada di `data/processed/_duckdb_tmp/`. Agregasi kecil saja yang dikonversi menjadi pandas untuk Plotly. Deduplikasi global tetap membutuhkan memori untuk status kunci artikel.

| Masalah kualitas | Keputusan |
|---|---|
| Null, string kosong, dan spasi saja | Tanggal/judul/isi wajib; baris tidak valid masuk karantina dengan alasan. Sumber dapat dipulihkan dari domain URL, lalu diberi label `tidak diketahui` jika tetap kosong. |
| Tanggal gagal parse atau di luar 2017 | Karantina. Jika lebih dari 5% input ditolak, pipeline berhenti agar format tanggal/pemetaan diperiksa. |
| Teks HTML dan spasi berulang | Normalisasi teks; raw tetap tersedia pada tahap normalisasi. Tanda baca dan teks asli yang bukan HTML dipertahankan. |
| Duplikat | Kunci `(source, published_at, title_key, content)`; pertahankan baris pertama sesuai urutan CSV. Artikel dengan judul sama dan isi berbeda tetap ada. |
| Outlier | IQR jumlah kata pada artikel valid sebelum deduplikasi. Artikel tetap dipertahankan dan diberi flag; tidak ada pemotongan teks atau winsorization. |
| Timestamp tanpa jam | Tidak diubah menjadi observasi jam 00.00; dikeluarkan dari heatmap jam. |
| Offset waktu eksplisit | Dikonversi ke Asia/Jakarta; waktu tanpa offset dipertahankan dan diasumsikan WIB untuk analisis jam. Asumsi ini perlu dikonfirmasi dari sumber. |

Validasi SQL memastikan tanggal/judul/isi/sumber valid, jumlah kata positif, jam 0–23 jika tersedia, `row_id` dan kunci artikel unik, serta rekonsiliasi jumlah baris. Raw = karantina + duplikat valid + bersih. SHA-256 menghubungkan input dan hasil antar-notebook.

## Menjalankan dengan Docker

Clone repository kemudian buka terminal di akar proyek:

```bash
git clone https://github.com/TegarReskiPratama/tugas1-abd-2026.git
cd tugas1-abd-2026
docker build -t tugas1-bigdata .
```

**Windows PowerShell** (sesuai komputer pengguna):

```powershell
docker run --rm -p 127.0.0.1:8888:8888 --mount "type=bind,source=$($PWD.Path),target=/home/jovyan/work" tugas1-bigdata
```

**Linux/macOS/Git Bash**:

```bash
docker run --rm -p 127.0.0.1:8888:8888 --mount "type=bind,source=$(pwd),target=/home/jovyan/work" tugas1-bigdata
```

Buka `http://localhost:8888/lab`, lalu masukkan token dari log container. Gunakan mount agar dataset dan hasil analisis tersimpan pada folder proyek. Dataset dikecualikan dari build context melalui `.dockerignore`, sehingga CSV besar tidak ikut tersalin ke image.

Docker dan CI memakai Python 3.12; dependency langsung pada `requirements.txt` dipatok versinya. Siapkan ruang disk sekitar 8 GB untuk CSV, tahap Parquet, dan hasil, serta memori Docker yang cukup untuk deduplikasi. Batas DuckDB dapat diubah melalui environment `DUCKDB_MEMORY_LIMIT` pada container.

## Menjalankan Tanpa Docker

Gunakan Python 3.12. Dari akar repository, pada Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyter lab
```

Pada Linux/macOS:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m jupyter lab
```

Pilih kernel Python dari environment tersebut. Jika notebook dibuka menggunakan environment lain, pasang kernel dengan `python -m ipykernel install --user --name abd-2026 --display-name "Python ABD 2026"` dari environment proyek, lalu pilih **Python ABD 2026**.

## Urutan Eksekusi dan Hasil

Jalankan **01 → 02 → 03**, setiap cell dari atas ke bawah, dengan kernel baru untuk setiap notebook. Path otomatis mengenali akar repository ketika direktori kerja berada di akar atau `notebooks/`.

| Notebook | Hasil utama |
|---|---|
| 01 | `dataset_raw.parquet`, `profiling_summary.json`, `profile_raw.csv`, `nulls_raw.csv` |
| 02 | `dataset_normalised.parquet`, `news_rejected.parquet`, `news_duplicates.parquet`, `dataset_bersih.parquet`, `cleaning_summary.json`, profil sebelum/sesudah, dan alasan karantina |
| 03 | Tabel EDA, `eda_summary.json`, `insights.md`, 10 output grafik interaktif pada notebook, dan 10 HTML pada `output/figures/` |

Notebook Milestone 3 mempertahankan empat bagian template: **inisialisasi dan data bersih**, **analisis temporal dan window functions**, **visualisasi interaktif**, dan **rumusan insight**. Analisis temporal memakai kalender lengkap 2017 dan rata-rata bergerak tujuh hari melalui window function DuckDB. Kalender lengkap memastikan hari tanpa artikel tetap masuk perhitungan intensitas.

Enam visualisasi inti memenuhi kategori template, lalu empat grafik tambahan memperinci pola waktu:

| No. | Visualisasi | Hasil HTML lokal |
|---|---|---|
| 1 | Tren harian dan moving average tujuh hari, dengan range slider | `01_daily_trend.html` |
| 2 | Histogram jumlah kata dan ekor distribusi | `02_article_length_distribution.html` |
| 3 | Heatmap korelasi volume harian, rata-rata jumlah kata, dan persentase outlier | `03_daily_correlation.html` |
| 4 | Komposisi artikel menurut sumber | `04_source_composition.html` |
| 5 | Heatmap hari × jam, dinormalisasi terhadap jumlah hari kalender | `05_weekday_hour_heatmap.html` |
| 6 | Bubble chart antarsumber: volume, rata-rata jumlah kata, dan persentase outlier | `06_source_multidimensional.html` |
| 7 | Volume publikasi bulanan | `07_monthly_volume.html` |
| 8 | Rata-rata artikel per hari dalam minggu | `08_weekday_pattern.html` |
| 9 | Tren bulanan lima sumber terbesar | `09_source_monthly_trend.html` |
| 10 | Rata-rata dan median panjang artikel per bulan | `10_monthly_article_length.html` |

HTML disimpan di `output/figures/` dan menyertakan Plotly JavaScript agar dapat dibuka tanpa koneksi internet setelah dibuat. Notebook menyimpan grafik yang sama dalam format MIME Plotly interaktif. Buka notebook di JupyterLab untuk berinteraksi dengan grafik; file HTML dibuat ulang dengan menjalankan notebook.

Sembilan insight mencakup volume bulan, pola hari, konsentrasi sumber, jam publikasi atau keterbatasannya, panjang teks/outlier, kualitas data, cakupan kalender, korelasi harian, dan rekomendasi praktis. Angka dihitung dari seluruh korpus bersih atau agregasinya, tanpa sampling. Korelasi menggambarkan hubungan pada tingkat hari dan tidak membuktikan sebab-akibat atau hubungan pada tingkat artikel. Grafik jam diberi anotasi jika data hanya memuat tanggal.

Jika SHA-256 berbeda, ulangi notebook sebelumnya agar data dan metadata konsisten. Jika header ambigu, cell awal notebook 01 mencetak kandidat; pilih nama kolom yang benar dalam `COLUMN_OVERRIDES`. Jika tanggal gagal parse, periksa contoh di `news_rejected.parquet` dan tambahkan format yang terverifikasi ke `published_datetime` sebelum menjalankan ulang 02.

## Pemeriksaan Statis dan Riwayat Commit

```bash
python scripts/validate_notebooks.py
python scripts/validate_milestone3.py
```

Validator pertama memeriksa JSON/schema notebook, sintaks semua code cell dan modul, import lokal, serta placeholder. Validator Milestone 3 memeriksa bukti eksekusi tersimpan, 10 output Plotly, 9 insight, rekonsiliasi tabel agregasi, dan menghitung ulang moving average serta korelasi dari CSV harian menggunakan pustaka standar Python. **Kedua validator tidak mengeksekusi notebook atau membaca dataset besar.** HTML lokal tidak diperlukan untuk pemeriksaan CI. Eksekusi notebook 03 pada dataset penuh dilakukan terpisah. GitHub Actions dikonfigurasi menjalankan kedua validator; status pemeriksaan remote harus dilihat pada tab Actions setelah push.

Riwayat Git mencatat implementasi profiling, cleaning, dan EDA. Pembaruan Milestone 3 melengkapi kategori visualisasi serta insight sesuai template dan menyimpan bukti eksekusi pada seluruh data bersih. Riwayat commit tidak menyatakan bahwa pekerjaan dilakukan pada tanggal pertemuan tertentu.

Setelah menjalankan dan memeriksa hasil secara lokal, simpan notebook dengan output dan tambahkan laporan kecil sebagai bukti hasil:

```bash
git add notebooks/03_eda_and_insights.ipynb README.md data/README.md output/insights.md
git add -f output/profiling_summary.json output/cleaning_summary.json output/eda_summary.json 'output/eda_*.csv'
git commit -m "feat(milestone-3): complete template EDA and verified insights"
git push origin main
```

## Integritas Akademik dan Penggunaan AI

Template berasal dari UMM-GURU dan digunakan dengan atribusi di atas. Penggunaan AI tidak menggantikan tanggung jawab mahasiswa untuk menjelaskan setiap bagian kode, menjalankan ulang, memeriksa hasil, dan memahami keterbatasan analisis. Ikuti ketentuan integritas akademik pada template dan spesifikasi mata kuliah.

## AI Disclosure Statement

- **Alat:** ChatGPT / Codex.
- **Bantuan:** adaptasi template Milestone 3, implementasi EDA dan visualisasi, perumusan insight dari hasil perhitungan, dokumentasi, serta eksekusi dan pemeriksaan hasil.
- **Verifikasi dalam perubahan ini:** ukuran dan checksum CSV, konsistensi checksum artefak profiling/cleaning yang sudah tersedia, serta eksekusi notebook 03 pada seluruh 455.360 artikel bersih. Notebook dan laporan menyimpan angka hasil perhitungan beserta keterbatasan analisis.
- **Tanggung jawab mahasiswa:** memahami dan memeriksa kode, grafik, insight, serta asumsi analisis; mampu menjalankan ulang pipeline dari CSV asli. Build/run Docker belum diuji dalam perubahan ini.

## Referensi Teknis

- [Template tugas UMM-GURU](https://github.com/UMM-GURU/tugas1-abd-2026)
- [Dataset Kaggle — Andi Ashari](https://www.kaggle.com/datasets/aashari/indonesian-news-articles-published-at-2017)
- [Metadata dataset BigScience](https://github.com/bigscience-workshop/data_tooling/issues/351)
- [Polars: lazy CSV scan](https://docs.pola.rs/api/python/version/1/reference/api/polars.scan_csv.html)
- [Polars: sink Parquet](https://docs.pola.rs/api/python/version/1/reference/api/polars.LazyFrame.sink_parquet.html)
- [DuckDB: SUMMARIZE](https://duckdb.org/docs/stable/guides/meta/summarize.html)
- [Plotly: interactive HTML export](https://plotly.com/python/interactive-html-export/)
