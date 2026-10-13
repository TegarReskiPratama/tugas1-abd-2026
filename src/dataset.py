"""Pembacaan CSV dan aturan kualitas korpus berita Indonesia 2017."""


import re


import polars as pl


DATASET_URL = "https://www.kaggle.com/datasets/aashari/indonesian-news-articles-published-at-2017"


ALIASES = {
    "published_raw": (
        "date", "published_date", "publish_date", "published_at", "pub_date",
        "pubdate", "date_published", "datePublished", "published", "datetime",
        "timestamp", "tanggal", "tanggal_publikasi", "created_at", "news_date",
    ),
    "title_raw": ("title", "judul", "headline", "news_title"),
    "content_raw": ("content", "article", "text", "body", "isi", "news_content"),
    "source_raw": ("source", "sumber", "publisher", "media", "news_source"),
    "url_raw": ("url", "link", "article_url", "news_url", "source_url"),
}


def normalise_header(value):
    return re.sub(r"[^a-z0-9]", "", value.strip().lower().lstrip("\ufeff"))


def scan_news_csv(path, column_overrides=None):
    """Semua kolom dibaca sebagai String; CSV rusak tidak dilewati diam-diam."""
    frame = pl.scan_csv(
        path,
        infer_schema_length=0,
        null_values=["", "NULL", "null", "None", "NaN"],
        encoding="utf8",
        try_parse_dates=False,
        ignore_errors=False,
        truncate_ragged_lines=False,
    )
    names = frame.collect_schema().names()
    lookup = {}
    for name in names:
        lookup.setdefault(normalise_header(name), []).append(name)
    mapping = {}
    for target, aliases in ALIASES.items():
        override = (column_overrides or {}).get(target)
        if override is not None:
            if override not in names:
                raise ValueError(f"Kolom override {override!r} tidak ada. Header: {names}")
            mapping[target] = override
            continue
        candidates = []
        for alias in aliases:
            for match in lookup.get(normalise_header(alias), []):
                if match not in candidates:
                    candidates.append(match)
        if len(candidates) > 1:
            raise ValueError(
                f"Lebih dari satu calon kolom {target}: {candidates}. "
                "Pilih salah satu secara eksplisit di COLUMN_OVERRIDES notebook 01."
            )
        mapping[target] = candidates[0] if candidates else None
    required = ["published_raw", "title_raw", "content_raw"]
    missing = [key for key in required if mapping[key] is None]
    if missing or not (mapping["source_raw"] or mapping["url_raw"]):
        raise ValueError(
            f"Header belum cocok: {names}. Kolom wajib belum ditemukan: {missing}. "
            "Dataset juga harus mempunyai sumber atau URL. "
            "Isi COLUMN_OVERRIDES menggunakan header yang tercetak."
        )
    selected = [
        (pl.col(original) if original else pl.lit(None, dtype=pl.String)).alias(target)
        for target, original in mapping.items()
    ]
    canonical = frame.with_row_index("row_id").select("row_id", *selected)
    return frame, canonical, mapping


def missing_summary(frame, columns):
    metrics = frame.select(
        pl.len().alias("rows"),
        *[pl.col(name).is_null().sum().alias(name) for name in columns],
    ).collect(engine="streaming").row(0, named=True)
    rows = metrics.pop("rows")
    return pl.DataFrame([
        {"kolom": name, "jumlah_null": count,
         "persen_null": round(100 * count / rows, 4) if rows else 0.0}
        for name, count in metrics.items()
    ]).sort("jumlah_null", descending=True)
