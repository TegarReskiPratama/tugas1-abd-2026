"""Periksa bukti tersimpan Milestone 3 tanpa dataset besar atau eksekusi notebook."""

import csv
from datetime import date, timedelta
import json
import math
from pathlib import Path
import statistics
import sys


ROOT = Path(__file__).resolve().parents[1]
PLOTLY_MIME = "application/vnd.plotly.v1+json"
VALIDATION_KEYS = {
    "daily_total_matches", "monthly_total_matches", "source_total_matches",
    "histogram_total_matches", "weekday_total_matches", "monthly_length_total_matches",
    "hourly_total_matches", "calendar_complete", "rolling_mean_matches", "html_files_exist",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def read_table(name):
    with (ROOT / "output" / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def number(row, column):
    value = float(row[column])
    require(math.isfinite(value), f"Nilai {column} tidak finite: {row[column]!r}")
    return value


def count(row, column="artikel"):
    value = number(row, column)
    require(value >= 0 and value.is_integer(), f"Jumlah {column} tidak valid: {value}")
    return int(value)


def close(actual, expected, label):
    require(math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9),
            f"{label}: {actual} berbeda dari hasil hitung ulang {expected}")


def total_matches(rows, total, name):
    require(sum(count(row) for row in rows) == total,
            f"Total artikel {name} tidak cocok dengan {total:,}")


def main():
    summary = read_json("output/eda_summary.json")
    cleaning = read_json("output/cleaning_summary.json")
    total = summary["rows_analysed"]
    require(isinstance(total, int) and total > 0, "rows_analysed harus integer positif")
    require(total == cleaning["rows_clean"], "Jumlah EDA berbeda dari hasil cleaning")
    require(summary["clean_parquet_sha256"] == cleaning["clean_parquet_sha256"],
            "Checksum EDA berbeda dari hasil cleaning")
    require(cleaning["rows_raw"] == total + cleaning["rows_rejected"]
            + cleaning["duplicates_removed"], "Rekonsiliasi baris cleaning gagal")
    validation = summary["validation"]
    require(VALIDATION_KEYS <= validation.keys(), "Ringkasan validasi EDA belum lengkap")
    require(all(value is True for value in validation.values()),
            f"Ada validasi EDA yang tidak lulus: {validation}")
    require(len(summary["insights"]) == 9
            and all(isinstance(item, str) and item.strip() for item in summary["insights"]),
            "Ringkasan harus memuat tepat 9 insight berisi teks")

    notebook = read_json("notebooks/03_eda_and_insights.ipynb")
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    require(code_cells, "Notebook tidak memiliki code cell")
    figures = []
    previous_execution = 0
    for index, cell in enumerate(code_cells, 1):
        execution = cell.get("execution_count")
        require(isinstance(execution, int) and execution > previous_execution,
                f"Code cell {index} belum dieksekusi berurutan")
        previous_execution = execution
        for output in cell.get("outputs", []):
            require(output.get("output_type") != "error",
                    f"Code cell {index} menyimpan error: {output.get('ename')}")
            if PLOTLY_MIME in output.get("data", {}):
                figure = output["data"][PLOTLY_MIME]
                require(isinstance(figure.get("data"), list) and figure["data"],
                        f"Grafik pada code cell {index} tidak memiliki trace")
                figures.append(figure)
    visualisations = summary["visualisations"]
    require(len(figures) == len(visualisations) == 10,
            "Notebook dan ringkasan harus memuat tepat 10 grafik interaktif Plotly")
    require(len({item["file"] for item in visualisations}) == 10,
            "Nama file visualisasi harus unik")
    for figure, item in zip(figures, visualisations):
        require(figure["layout"]["title"]["text"] == item["title"],
                f"Judul output Plotly tidak cocok dengan ringkasan: {item['file']}")

    daily = read_table("eda_daily.csv")
    expected_dates = [date(2017, 1, 1) + timedelta(days=index) for index in range(365)]
    dates = [date.fromisoformat(row["tanggal"][:10]) for row in daily]
    require(dates == expected_dates,
            "Kalender harian harus berisi 365 tanggal unik berurutan pada tahun 2017")
    total_matches(daily, total, "harian")
    observed_days = 0
    for index, (row, day) in enumerate(zip(daily, dates)):
        require(count(row, "weekday") == day.isoweekday(),
                f"Hari dalam minggu tidak sesuai tanggal {day}")
        require(row["bulan"][:10] == day.replace(day=1).isoformat(),
                f"Bulan tidak sesuai tanggal {day}")
        require(row["ada_artikel"].lower() in {"true", "false"},
                f"Flag ada_artikel tidak valid pada {day}")
        observed = row["ada_artikel"].lower() == "true"
        require(observed == (count(row) > 0), f"Flag ada_artikel keliru pada {day}")
        observed_days += observed
        window = daily[max(0, index - 6):index + 1]
        close(number(row, "ma7"), statistics.mean(count(item) for item in window),
              f"Moving average {day}")
        require(count(row, "window_days") == len(window),
                f"Ukuran window keliru pada {day}")
    require(summary["calendar_days"] == 365
            and summary["days_with_articles"] == observed_days,
            "Cakupan kalender ringkasan berbeda dari tabel harian")

    tables = {
        "bulanan": read_table("eda_monthly.csv"),
        "sumber": read_table("eda_sources.csv"),
        "histogram": read_table("eda_length_histogram.csv"),
        "hari dalam minggu": read_table("eda_weekday.csv"),
        "panjang bulanan": read_table("eda_monthly_length.csv"),
    }
    for name, rows in tables.items():
        total_matches(rows, total, name)
    for name in ("bulanan", "panjang bulanan"):
        rows = tables[name]
        require(len(rows) == 12 and {row["bulan"][:7] for row in rows}
                == {f"2017-{month:02d}" for month in range(1, 13)},
                f"Tabel {name} harus memuat 12 bulan unik tahun 2017")
        for row in rows:
            group = [item for item in daily if item["tanggal"][:7] == row["bulan"][:7]]
            require(count(row) == sum(count(item) for item in group),
                    f"Volume {name} berbeda dari harian pada {row['bulan']}")
            if name == "bulanan":
                require(count(row, "hari_kalender") == len(group),
                        f"Jumlah hari kalender keliru pada {row['bulan']}")
                close(number(row, "rata_per_hari"), count(row) / len(group),
                      f"Intensitas bulanan {row['bulan']}")
    weekdays = tables["hari dalam minggu"]
    require(len(weekdays) == 7 and {count(row, "weekday") for row in weekdays} == set(range(1, 8)),
            "Tabel hari harus memuat tujuh hari unik")
    for row in weekdays:
        group = [item for item in daily if count(item, "weekday") == count(row, "weekday")]
        require(count(row) == sum(count(item) for item in group)
                and count(row, "hari_kalender") == len(group),
                f"Agregasi hari {row['weekday']} tidak cocok dengan kalender")
        close(number(row, "rata_per_hari"), count(row) / len(group),
              f"Intensitas hari {row['weekday']}")

    hourly = read_table("eda_hourly.csv")
    require(sum(count(row) for row in hourly) == summary["known_time_rows"]
            and summary["known_time_rows"] + cleaning["date_only_rows"] == total,
            "Jumlah artikel dengan/tanpa jam tidak cocok")
    require(all(1 <= count(row, "weekday") <= 7 and 0 <= count(row, "jam") <= 23
                for row in hourly), "Tabel jam memiliki hari atau jam tidak valid")
    top_sources = sorted(tables["sumber"], key=lambda row: (-count(row), row["sumber"]))[:5]
    source_monthly = read_table("eda_source_monthly.csv")
    for source in top_sources:
        rows = [row for row in source_monthly if row["sumber"] == source["sumber"]]
        require(len(rows) == 12 and len({row["bulan"][:7] for row in rows}) == 12,
                f"Tren sumber {source['sumber']} tidak memiliki 12 bulan unik")
        total_matches(rows, count(source), f"tren sumber {source['sumber']}")

    eligible = [row for row in daily if count(row) > 0
                and all(row[column] for column in ("mean_words", "outlier_percent"))]
    require(len(eligible) >= 2, "Hari berartikel tidak cukup untuk menghitung korelasi")
    correlation = statistics.correlation([count(row) for row in eligible],
                                         [number(row, "mean_words") for row in eligible])
    require(summary["correlation_days"] == len(eligible)
            and summary["correlation_unit"] == "day with articles",
            "Unit atau jumlah hari korelasi berbeda dari tabel harian")
    close(summary["daily_volume_length_pearson_r"], correlation,
          "Pearson volume harian dengan rata-rata panjang")
    matrix = read_table("eda_daily_correlation.csv")
    length_row = next((row for row in matrix if row["variabel"] == "mean_words"), None)
    require(length_row is not None, "CSV korelasi tidak memiliki baris mean_words")
    close(number(length_row, "artikel"), correlation, "Korelasi pada CSV matriks")
    print(f"Validasi bukti M3 lulus: {total:,} artikel, 365 hari, 10 grafik, 9 insight; "
          f"Pearson r={correlation:.6f}. Notebook tidak dieksekusi ulang.")


if __name__ == "__main__":
    try:
        main()
    except KeyError as error:
        print(f"Validasi bukti M3 gagal: kolom/kunci wajib tidak ditemukan: {error}",
              file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError, TypeError) as error:
        print(f"Validasi bukti M3 gagal: {error}", file=sys.stderr)
        sys.exit(1)
