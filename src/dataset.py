"""Pembacaan CSV dan aturan kualitas korpus berita Indonesia 2017."""

import re

import polars as pl


DATASET_URL = "https://www.kaggle.com/datasets/aashari/indonesian-news-articles-published-at-2017"
BUSINESS_KEY = ["source", "published_at", "title_key", "content"]
ANALYSIS_COLUMNS = [
    "row_id", "published_at", "published_date", "month", "weekday", "hour",
    "has_time", "source", "source_domain", "source_is_imputed", "url",
    "title", "title_key", "content", "word_count", "char_count",
    "is_length_outlier",
]
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


def compact_text(column):
    text = pl.col(column).str.replace_all(r"\s+", " ").str.strip_chars()
    return pl.when(text.str.len_chars() > 0).then(text).otherwise(None)


def published_datetime(column="published_raw"):
    """Format eksplisit; tanggal yang gagal parse tetap null untuk audit."""
    value = compact_text(column)
    # Offset eksplisit dikonversi ke WIB; waktu tanpa offset dipertahankan.
    aware = [
        value.str.to_datetime(format=fmt, strict=False, time_unit="us")
        .dt.convert_time_zone("Asia/Jakarta").dt.replace_time_zone(None)
        for fmt in (
            "%+", "%Y-%m-%d %H:%M:%S%.f%#z", "%Y-%m-%d %H:%M:%S%.f %#z",
        )
    ]
    local = value.str.replace_all(r"(?i)\s+WIB$", "")
    naive = [
        local.str.to_datetime(format=fmt, strict=False, time_unit="us")
        for fmt in (
            "%Y-%m-%d %H:%M:%S%.f", "%Y-%m-%dT%H:%M:%S%.f",
            "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y",
            "%d-%m-%Y %H:%M:%S", "%d-%m-%Y", "%Y/%m/%d", "%Y%m%d",
        )
    ]
    return pl.coalesce(*aware, *naive)


def normalise_news(raw):
    """Simpan kolom raw dan flags sehingga keputusan cleaning dapat ditelusuri."""
    title = compact_text("title_raw")
    content = (
        pl.col("content_raw")
        .str.replace_all(r"(?is)<script\b[^>]*>.*?</script>", " ")
        .str.replace_all(r"(?is)<style\b[^>]*>.*?</style>", " ")
        .str.replace_all(r"<[^>]+>", " ")
        .str.replace_all("&nbsp;", " ")
        .str.replace_all("&amp;", "&")
        .str.replace_all("&quot;", '"')
        .str.replace_all("&#39;", "'")
        .str.replace_all(r"\s+", " ").str.strip_chars()
    )
    stage = raw.with_columns(
        published_datetime().alias("published_at"),
        title.alias("title"),
        pl.when(content.str.len_chars() > 0).then(content).otherwise(None).alias("content"),
        compact_text("source_raw").alias("source_text"),
        compact_text("url_raw").alias("url_text"),
        pl.col("published_raw").str.contains(r"(?:T|\s)\d{1,2}:\d{2}")
        .fill_null(False).alias("has_time"),
    )
    domain_pattern = r"(?i)^(?:https?://)?(?:www\.)?([a-z0-9][a-z0-9.-]*\.[a-z]{2,})(?:[/:?#]|$)"
    stage = stage.with_columns(
        pl.coalesce(
            pl.col("url_text"),
            pl.when(pl.col("source_text").str.contains(r"(?i)^https?://"))
            .then(pl.col("source_text")),
        ).alias("url"),
        pl.col("source_text").str.extract(domain_pattern, 1)
        .str.to_lowercase().alias("source_host"),
    ).with_columns(
        pl.col("url").str.to_lowercase().str.extract(domain_pattern, 1).alias("url_host")
    )
    source_value = pl.coalesce(
        pl.col("source_host"), pl.col("source_text").str.to_lowercase(), pl.col("url_host")
    )
    stage = stage.with_columns(
        source_value.is_null().alias("source_is_imputed"),
        source_value.fill_null("tidak diketahui").alias("source"),
        pl.coalesce(pl.col("url_host"), pl.col("source_host"))
        .fill_null("tidak diketahui").alias("source_domain"),
        pl.col("title").str.to_lowercase().alias("title_key"),
        pl.col("content").str.count_matches(r"\S+").fill_null(0).alias("word_count"),
        pl.col("content").str.len_chars().fill_null(0).alias("char_count"),
        pl.col("published_at").dt.date().alias("published_date"),
        pl.col("published_at").dt.truncate("1mo").dt.date().alias("month"),
        pl.col("published_at").dt.weekday().alias("weekday"),
        pl.when(pl.col("has_time")).then(pl.col("published_at").dt.hour())
        .otherwise(None).alias("hour"),
    )
    violations = {
        "tanggal_kosong_atau_gagal_parse": pl.col("published_at").is_null(),
        "di_luar_2017": (pl.col("published_at").dt.year() != 2017).fill_null(False),
        "judul_kosong": pl.col("title").is_null(),
        "isi_kosong": pl.col("content").is_null(),
    }
    return stage.with_columns(
        pl.concat_str(
            [pl.when(flag).then(pl.lit(reason)).otherwise(pl.lit(""))
             for reason, flag in violations.items()],
            separator="|",
        ).str.replace_all(r"\|+", "|").str.strip_chars("|").alias("rejection_reason")
    )


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
