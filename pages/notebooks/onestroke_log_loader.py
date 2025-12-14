import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # OneStroke Log Loading

    https://marimo.app/ai
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## File Upload

    https://docs.marimo.io/api/inputs/file/#marimo.ui.file
    """)
    return


@app.cell
def _(mo):
    file_area = mo.ui.file(kind="area")
    file_area
    return (file_area,)


@app.cell
def _(file_area, mo):
    mo.stop(not file_area.value, mo.md("Upload the log file."))

    mo.vstack([
        file_area.value,
        file_area.name()
    ])

    return


@app.cell
def _(TAG_COLUMNS, TARGET_TAGS, csv, defaultdict, file_area, io, mo, pd):
    mo.stop(not file_area.value, mo.md("Upload the log file."))

    file_bytes = file_area.contents()
    text = io.StringIO(file_bytes.decode("utf-8"))
    reader = csv.reader(text)

    grouped = defaultdict(list) 
    for row in reader:
        if not row:
            continue
        tag = row[0]
        if tag in TARGET_TAGS:
            grouped[tag].append(row)

    dfs = {}
    for tag, rows in grouped.items():
        df = pd.DataFrame(rows)

        if tag in TAG_COLUMNS:
            df.columns = TAG_COLUMNS[tag][:df.shape[1]]

        dfs[tag] = df

    return (dfs,)


@app.cell
def _(dfs):
    dfs["TRP"]
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import io
    import csv
    from collections import defaultdict

    TAG_COLUMNS = {
        "ACT": ["tag", "timestamp", "value", "datetime"],
        "DBG": ["tag", "timestamp", "info", "datetime_tz"],
        "AMD": ["tag", "timestamp", "ax", "ay", "az",
                "qx", "qy", "qz", "qw", "counter", "status"],
        "SCY": ["tag", "timestamp", "event", "value"],
        "TRP": ["tag", "timestamp", "type", "end_ts", "count",
                "v1", "v2", "lat", "lon", "score", "a", "b", "c", "flag"],
    }

    TARGET_TAGS = ["ACT", "SCY", "TRP"]

    return TAG_COLUMNS, TARGET_TAGS, csv, defaultdict, io, mo, pd


if __name__ == "__main__":
    app.run()
