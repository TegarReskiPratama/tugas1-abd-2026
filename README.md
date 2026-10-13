# Tugas 1: Eksplorasi dan Analisis Dataset Besar Indonesia

**Tegar Reski Pratama — NIM 202310370311215**  
Mata kuliah Analisis Big Data, Informatika, Universitas Muhammadiyah Malang.

Proyek ini menganalisis pola waktu publikasi dan karakteristik teks pada **Indonesian News Articles Published at 2017** dari Kaggle. Struktur, nama notebook, milestone, dan aturan teknis mengikuti [template UMM-GURU](https://github.com/UMM-GURU/tugas1-abd-2026).

**Status penyiapan:** tiga notebook telah diisi, tetapi belum dijalankan dalam perubahan ini sesuai permintaan. Pemeriksaan yang dilakukan hanya validasi statis. Ukuran lokal, jumlah artikel, hasil cleaning, grafik, dan insight numerik akan diverifikasi/dihasilkan ketika notebook dijalankan. Docker image juga belum dibangun dalam perubahan ini.

## Milestone

| Tahap | Target | Implementasi dan bukti setelah dijalankan |
|---|---|---|
| Milestone 1 | Pertemuan 3 | Dokumentasi `data/README.md`, notebook `01_data_profiling.ipynb`, pemeriksaan CSV >= 500 MB atau > 1 juta baris, SHA-256, profil Polars dan DuckDB, salinan Parquet |
| Milestone 2 | Pertemuan 5 | Notebook `02_data_cleaning.ipynb`, cleaning Polars, `SUMMARIZE` sebelum/sesudah, karantina, deduplikasi, flag IQR, dan validasi SQL |
| Milestone 3 | Pertemuan 8 | Notebook `03_eda_and_insights.ipynb`, analisis temporal, 8 grafik interaktif Plotly, dan 7 insight yang dihitung dari seluruh korpus |
| Final | Pertemuan 10 | Dockerfile, dependency yang dipatok, dokumentasi, pemeriksaan hasil, serta riwayat commit tiap milestone |

## Pertanyaan Analisis

1. Bagaimana volume artikel berubah per hari dan bulan selama 2017?
2. Apakah intensitas artikel berbeda menurut hari dan jam publikasi?
3. Seberapa terkonsentrasi artikel pada sumber tertentu?
4. Bagaimana distribusi dan perubahan panjang artikel?
5. Berapa banyak artikel dikarantina, terduplikasi, dan ditandai outlier?

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
│   ├── figures/                         # 8 berkas HTML interaktif setelah run
│   ├── profiling_summary.json
│   ├── cleaning_summary.json
│   ├── eda_summary.json
│   └── insights.md
├── src/
│   ├── __init__.py
│   ├── common.py
│   └── dataset.py
├── scripts/validate_notebooks.py
├── .dockerignore
├── Dockerfile
├── requirements.txt
└── README.md
```

Berkas pada `output/` selain `.gitkeep` dihasilkan saat eksekusi. CSV asli, Parquet, dan HTML besar tidak disertakan dalam commit. Notebook mengadaptasi dua template yang diberikan pengguna; logika dataset yang digunakan berpusat di `src/dataset.py`.

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
| 03 | Tabel EDA, `eda_summary.json`, `insights.md`, dan 8 HTML pada `output/figures/` |

Delapan visualisasi: tren harian + moving average, volume bulanan, intensitas per hari minggu, komposisi sumber, heatmap hari × jam, distribusi jumlah kata, tren lima sumber terbesar, serta rata-rata/median panjang artikel per bulan. HTML menyertakan Plotly JavaScript agar dapat dibuka tanpa koneksi internet. Notebook menampilkan grafik yang sama.

Tujuh insight mencakup volume bulan, pola hari, konsentrasi sumber, jam publikasi atau keterbatasannya, panjang teks/outlier, kualitas data, dan cakupan kalender. Seluruh angka dihitung dari data hasil eksekusi; tidak ada hasil numerik yang dikarang atau diambil dari sampel. Grafik jam diberi anotasi jika data hanya memuat tanggal.

Jika SHA-256 berbeda, ulangi notebook sebelumnya agar data dan metadata konsisten. Jika header ambigu, cell awal notebook 01 mencetak kandidat; pilih nama kolom yang benar dalam `COLUMN_OVERRIDES`. Jika tanggal gagal parse, periksa contoh di `news_rejected.parquet` dan tambahkan format yang terverifikasi ke `published_datetime` sebelum menjalankan ulang 02.

## Pemeriksaan Statis dan Riwayat Commit

```bash
python scripts/validate_notebooks.py
```

Validator memeriksa JSON/schema notebook, sintaks semua code cell dan modul, import lokal, serta placeholder. **Validator tidak mengeksekusi notebook atau membaca dataset.** Tambahkan `--require-unexecuted` jika ingin memastikan seluruh execution count/output masih kosong. GitHub Actions juga hanya menjalankan validasi statis.

Perubahan dikelompokkan dalam tiga commit berurutan: profiling dan dokumentasi dataset (M1), cleaning serta validasi kualitas (M2), kemudian EDA/insight dan environment akhir (M3). Commit tersebut mencatat tahapan penyiapan kode; tidak mengklaim bahwa milestone sudah dijalankan pada tanggal pertemuan.

Setelah menjalankan dan memeriksa hasil secara lokal, simpan notebook dengan output dan tambahkan laporan kecil sebagai bukti hasil:

```bash
git add notebooks/
git add -f output/profiling_summary.json output/cleaning_summary.json output/eda_summary.json output/insights.md
git commit -m "results: verify profiling cleaning and EDA on complete dataset"
git push origin main
```

## Integritas Akademik dan Penggunaan AI

Template berasal dari UMM-GURU dan digunakan dengan atribusi di atas. Penggunaan AI tidak menggantikan tanggung jawab mahasiswa untuk menjelaskan setiap bagian kode, menjalankan ulang, memeriksa hasil, dan memahami keterbatasan analisis. Ikuti ketentuan integritas akademik pada template dan spesifikasi mata kuliah.

## AI Disclosure Statement

- **Alat:** ChatGPT / Codex.
- **Bantuan:** adaptasi template, implementasi profiling/cleaning/EDA, dokumentasi, konfigurasi environment, serta pemeriksaan statis.
- **Verifikasi dalam perubahan ini:** pemeriksaan struktur template, sumber metadata dataset dan dokumentasi resmi, validitas JSON, sintaks Python, import lokal, serta kondisi seluruh notebook belum dieksekusi.
- **Verifikasi hasil yang masih diperlukan oleh mahasiswa:** unduh CSV lengkap, jalankan notebook berurutan, periksa syarat ukuran, aturan kualitas, grafik, insight, dan kemampuan build/run Docker.

## Referensi Teknis

- [Template tugas UMM-GURU](https://github.com/UMM-GURU/tugas1-abd-2026)
- [Dataset Kaggle — Andi Ashari](https://www.kaggle.com/datasets/aashari/indonesian-news-articles-published-at-2017)
- [Metadata dataset BigScience](https://github.com/bigscience-workshop/data_tooling/issues/351)
- [Polars: lazy CSV scan](https://docs.pola.rs/api/python/version/1/reference/api/polars.scan_csv.html)
- [Polars: sink Parquet](https://docs.pola.rs/api/python/version/1/reference/api/polars.LazyFrame.sink_parquet.html)
- [DuckDB: SUMMARIZE](https://duckdb.org/docs/stable/guides/meta/summarize.html)
- [Plotly: interactive HTML export](https://plotly.com/python/interactive-html-export/)
