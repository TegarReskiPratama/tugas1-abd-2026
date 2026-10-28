# Data Tugas 1

## Dataset yang Dipilih

**Indonesian News Articles Published at 2017** dari Andi Ashari (`aashari`) digunakan untuk analisis temporal publikasi dan karakteristik teks artikel berita berbahasa Indonesia.

| Item | Isi |
|---|---|
| Dataset | Indonesian News Articles Published at 2017 |
| Penyedia | Andi Ashari (`aashari`) |
| Sumber unduhan | [Kaggle](https://www.kaggle.com/datasets/aashari/indonesian-news-articles-published-at-2017) |
| Lisensi metadata | CC0: Public Domain menurut [katalog BigScience](https://github.com/bigscience-workshop/data_tooling/issues/351). Artikel tetap diatribusikan ke sumbernya; lisensi katalog tidak otomatis memastikan hak setiap konten media asli. |
| Format dan file | CSV UTF-8, `mq_news.csv` |
| Lokasi input | `data/raw/mq_news.csv` atau `data/raw/Dataset Indonesian News Articles Published at 2017/mq_news.csv` |
| Unit analisis | Satu baris CSV = satu artikel berita; artikel multibaris tetap satu record |
| Cakupan dan periode | Artikel berbahasa Indonesia; data bersih mencakup 1 Januari–31 Desember 2017 dan memiliki artikel pada seluruh 365 hari |
| Skala aktual | CSV asli 1.371.437.745 byte (sekitar 1,37 GB), 455.678 record artikel; memenuhi syarat ukuran >= 500 MB |
| Bukti skala aktual | Notebook 01 menyimpan `raw_size_bytes`, `rows_raw`, `size_requirement_met`, dan SHA-256 pada `output/profiling_summary.json` |
| Hasil cleaning | 455.360 artikel bersih, 52 artikel dikarantina karena isi kosong, dan 266 salinan duplikat dihapus |
| Syarat tugas | CSV setelah ekstraksi >= 500.000.000 byte **atau** jumlah record > 1.000.000; notebook berhenti bila keduanya tidak terpenuhi |

Metadata hasil Milestone 1 dan 2 yang telah tersedia diperiksa terhadap ukuran CSV serta checksum CSV dan Parquet. Notebook Milestone 3 dijalankan pada seluruh 455.360 artikel bersih dalam perubahan ini; notebook 01 dan 02 tidak dijalankan ulang. Ukuran Parquet bisa jauh lebih kecil karena kompresi; penilaian skala tetap menggunakan CSV asli. Jumlah record berada di bawah satu juta, tetapi ukuran CSV telah memenuhi syarat tugas.

SHA-256 CSV asli: `32f0839ab07ada289c23bfff3508c8753037ef6d345e848c3c59558db531a953`. SHA-256 Parquet bersih: `ba3c4d94dc63a31d19d102127fbb993e80d097959600bb3cc2aca33a2f4fcea6`.

## Informasi dan Skema Analisis

Metadata sumber menyebut tanggal publikasi, judul, isi, dan sumber. Header asli dicatat saat eksekusi; pipeline mengenali variasi umum tanpa mengasumsikan nama kolom yang belum dilihat. Jika lebih dari satu header cocok dengan atribut yang sama, notebook berhenti dan meminta pilihan eksplisit melalui `COLUMN_OVERRIDES`.

| Kolom kanonis Parquet awal | Kolom CSV yang dikenali, antara lain | Aturan |
|---|---|---|
| `row_id` | Dibuat dari urutan record CSV | Untuk menelusuri baris ke input asli |
| `published_raw` | `date`, `published_date`, `publish_date`, `published_at`, `timestamp`, `tanggal` | Wajib; nilai asli dipertahankan sebelum parsing |
| `title_raw` | `title`, `judul`, `headline` | Wajib |
| `content_raw` | `content`, `content_html`, `article`, `text`, `body`, `isi` | Wajib; input aktual memakai `content_html` |
| `source_raw` | `source`, `sumber`, `publisher`, `media` | Sumber atau URL harus tersedia sebagai kolom input |
| `url_raw` | `url`, `link`, `article_url`, `news_url` | Opsional jika kolom sumber tersedia |

Kolom tambahan di CSV tidak digunakan untuk analisis, tetapi nama/tipe aslinya dicatat dan CSV asli tetap ada. Missing markers yang dibaca sebagai null: string kosong, `NULL`, `null`, `None`, dan `NaN`. Spasi saja ditangani saat normalisasi. Reader tidak melewati CSV rusak atau mengganti encoding secara diam-diam.

Kolom hasil cleaning mencakup timestamp/tanggal, bulan, hari ISO 1–7, jam nullable, flag ketersediaan jam, label/domain sumber, flag sumber imputasi, judul, isi, jumlah kata/karakter, serta flag outlier. Teks raw tersedia pada `dataset_raw.parquet` dan `dataset_normalised.parquet`.

## Cara Memperoleh Data

1. Buka [halaman Kaggle dataset](https://www.kaggle.com/datasets/aashari/indonesian-news-articles-published-at-2017).
2. Login jika diminta, klik **Download**, lalu unduh dataset lengkap.
3. Ekstrak ZIP dengan aplikasi arsip; jangan menggunakan preview atau sampel file.
4. Letakkan `mq_news.csv` di `data/raw/` atau pertahankan folder hasil ekstraksi `data/raw/Dataset Indonesian News Articles Published at 2017/`. Notebook 01 mendukung kedua lokasi; jika keduanya tersedia, lokasi dalam folder dataset diprioritaskan.
5. Buka JupyterLab dari akar repository dan jalankan notebook 01, 02, lalu 03. Path otomatis bekerja dari akar atau `notebooks/`.
6. Periksa metadata dan hasil; laporkan ukuran/jumlah baris/checksum dari hasil eksekusi sendiri.

Alternatif CLI setelah [Kaggle API](https://github.com/Kaggle/kaggle-api) terpasang dan autentikasi akun dikonfigurasi:

```bash
kaggle datasets download -d aashari/indonesian-news-articles-published-at-2017 -p data/raw
```

Ekstrak arsip yang dihasilkan ke `data/raw/`. File `mq_news.csv` boleh berada langsung di folder tersebut atau di subfolder `Dataset Indonesian News Articles Published at 2017/`. Simpan credential Kaggle di luar repository. Kaggle API hanya alat unduhan opsional dan tidak dibutuhkan untuk mengeksekusi notebook setelah CSV tersedia.

### Lokasi pada Windows yang Digunakan

Lokasi pengguna adalah `D:\KULIAH\ S1\SEMESTER\7\Analisis Big Data\tugas1-abd-2026\data\raw\Dataset Indonesian News Articles Published at 2017\mq_news.csv`. Buka PowerShell dari akar repository `tugas1-abd-2026` dan mount akar tersebut ke `/home/jovyan/work` pada container. Notebook memakai path relatif di dalam proyek; tidak perlu memindahkan CSV atau memakai path `D:` di dalam Linux container. Path sumber yang benar-benar dipilih dicatat pada metadata profiling.

## Tanggal dan Kualitas Data

Parser menerima ISO, timestamp dengan detik/pecahan detik, tanggal `YYYY-MM-DD`, `YYYY/MM/DD`, `YYYYMMDD`, serta format day-first `DD/MM/YYYY` dan `DD-MM-YYYY` yang didukung secara eksplisit di `src/dataset.py`. Sufiks WIB dapat diproses. Format yang tidak cocok menjadi null dan dikarantina bersama nilai raw; tidak ada tebakan month-first otomatis. Offset eksplisit dikonversi ke Asia/Jakarta, sedangkan timestamp tanpa offset diasumsikan WIB untuk analisis jam. Tanggal tanpa jam tidak dianggap observasi pukul 00.00.

Cleaning mempertahankan teks asli yang bukan HTML, mengarantina judul/isi kosong dan tanggal tidak valid/di luar 2017, menormalisasi label/domain sumber, serta menghapus salinan berdasarkan kunci `(source, published_at, title_key, content)`. Artikel panjang tetap disimpan dengan flag IQR. Jika lebih dari 5% input masuk karantina, format/pemetaan harus diperiksa sebelum lanjut.

Keterbatasan: coverage pengumpulan dapat berbeda antarhari/sumber; artikel tidak sama dengan peristiwa; artikel dan label sumber tidak menjamin representasi seluruh media Indonesia. Tidak ada koordinat terverifikasi untuk analisis spasial.

## Aturan Penyimpanan dan Reproduktivitas

- Pertahankan CSV asli; cleaning tidak menimpa input.
- Jangan commit CSV mentah, arsip, Parquet, credential, atau HTML besar.
- `data/raw/`, `data/processed/`, dan `output/figures/` diabaikan oleh Git kecuali `.gitkeep`.
- Notebook 01 menghasilkan checksum CSV dan Parquet awal; notebook 02 memverifikasi input dan mencatat checksum hasil bersih; notebook 03 memverifikasi checksum hasil tersebut sebelum EDA.
- Ringkasan JSON dan tabel agregasi EDA kecil di `output/` ditambahkan secara eksplisit sebagai bukti hasil, sesuai perintah README utama.
- Notebook 03 menyimpan 10 grafik dengan output MIME Plotly interaktif dan 9 insight. HTML pada `output/figures/` dibuat ulang saat notebook dijalankan dan tetap diabaikan Git.

## AI Disclosure Statement

ChatGPT/Codex membantu adaptasi template UMM-GURU, implementasi EDA, dokumentasi, dan pemeriksaan hasil. Dalam perubahan ini ukuran serta checksum CSV dan artefak Milestone 1/2 diperiksa, lalu notebook Milestone 3 dijalankan pada seluruh data bersih. Sepuluh visualisasi dan sembilan insight dihitung dari hasil eksekusi. Deskripsi serta lisensi metadata mengacu pada sumber yang ditautkan. Mahasiswa tetap bertanggung jawab memahami kode, asumsi, dan hasil analisis; Docker belum dibangun atau diuji dalam perubahan ini.
