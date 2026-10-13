# Data Tugas 1

## Dataset yang Dipilih

Dataset yang digunakan adalah **Indonesian News Articles Published at 2017**, yang diterbitkan oleh Andi Ashari (`aashari`) di Kaggle. Dataset ini berisi artikel berita berbahasa Indonesia dari situs berita Indonesia dan digunakan untuk eksplorasi serta analisis pola publikasi berita.

| Item | Isi |
|---|---|
| Nama dataset | Indonesian News Articles Published at 2017 |
| Penyedia dataset | Andi Ashari (`aashari`) |
| Sumber unduhan | [Kaggle — Indonesian News Articles Published at 2017](https://www.kaggle.com/datasets/aashari/indonesian-news-articles-published-at-2017) |
| Lisensi/ketentuan pakai | CC0: Public Domain, berdasarkan [metadata BigScience](https://huggingface.co/datasets/bigscience-data/roots_id_indonesian_news_articles_2017). Sumber dataset tetap dicantumkan sebagai atribusi. |
| Format | CSV |
| Nama file | `mq_news.csv` |
| Lokasi data mentah | `data/raw/mq_news.csv` |
| Ukuran sementara | Sekitar 1,37 GB menurut catatan pemilihan dataset sebelumnya; ukuran CSV lokal setelah ekstraksi belum diverifikasi. |
| Jumlah baris | Belum dihitung dari file lokal; akan dicatat pada notebook profiling. |
| Periode data | Artikel yang diterbitkan pada 2017, sesuai deskripsi dataset; tanggal paling awal dan paling akhir perlu diperiksa pada profiling. |
| Unit analisis | Satu baris mewakili satu artikel berita. |
| Cakupan | Artikel berita berbahasa Indonesia dari situs berita Indonesia. |

Ukuran dan jumlah baris aktual harus diperiksa dari `mq_news.csv` setelah ekstraksi. Syarat tugas adalah **ukuran minimal 500 MB atau lebih dari 1.000.000 baris**. Angka ukuran sementara di atas bukan hasil pengukuran file lokal dan jumlah baris belum dinyatakan memenuhi batas tugas.

## Informasi yang Tersedia

Deskripsi sumber menyebutkan informasi berikut. Nama kolom, tipe data, dan kelengkapan setiap atribut harus dikonfirmasi dari header CSV pada `notebooks/01_data_profiling.ipynb`.

| Informasi | Keterangan |
|---|---|
| Tanggal publikasi | Waktu atau tanggal artikel diterbitkan. |
| Judul | Judul artikel berita. |
| Isi artikel | Teks artikel berita. |
| Sumber | Sumber artikel berita. |

Rujukan deskripsi dan lisensi: [metadata dataset dalam katalog BigScience](https://github.com/bigscience-workshop/data_tooling/issues/351). File yang digunakan dalam tugas tetap CSV dari Kaggle.

## Cara Memperoleh Data

1. Buka [halaman dataset di Kaggle](https://www.kaggle.com/datasets/aashari/indonesian-news-articles-published-at-2017).
2. Masuk ke akun Kaggle apabila diminta, lalu klik **Download**.
3. Ekstrak arsip hasil unduhan.
4. Letakkan file `mq_news.csv` di `data/raw/` sehingga lokasi akhirnya adalah `data/raw/mq_news.csv`.
5. Pertahankan isi CSV asli. Lakukan pembersihan melalui notebook dan simpan hasilnya di `data/processed/`.
6. Catat ukuran file, jumlah baris, nama kolom, rentang tanggal, serta checksum SHA-256 pada tahap profiling untuk dokumentasi dan pemeriksaan reproduktivitas.

## Mengarahkan Notebook ke Dataset

Jika notebook dijalankan dari folder `notebooks/`, gunakan:

```python
DATA_PATH = "../data/raw/mq_news.csv"
```

Jika direktori kerja Jupyter berada di akar repository, gunakan:

```python
DATA_PATH = "data/raw/mq_news.csv"
```

Path relatif mengikuti direktori kerja saat notebook dijalankan.

## Aturan Penyimpanan

- `data/raw/mq_news.csv` merupakan data asli dan tidak boleh ditimpa oleh hasil cleaning.
- Jangan commit dataset mentah atau hasil olahan berukuran besar ke GitHub.
- Folder `data/raw/` dan `data/processed/` sudah diabaikan oleh `.gitignore`; berkas data tetap disimpan secara lokal.
- Simpan hasil transformasi yang dapat direproduksi pada `data/processed/`.
- Cantumkan sumber dan petunjuk unduh dalam README ini agar dataset dapat diperoleh kembali.

## AI Disclosure Statement

ChatGPT membantu penyusunan dokumentasi dataset ini. Identitas dataset mengacu pada riwayat pemilihan dataset, sedangkan deskripsi dan informasi lisensi diperiksa melalui metadata sumber yang ditautkan. File CSV lokal belum diakses; ukuran aktual, jumlah baris, header kolom, rentang tanggal, dan checksum masih perlu diverifikasi pada tahap profiling.
