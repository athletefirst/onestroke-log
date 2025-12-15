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
def _(TAG_COLUMNS, TARGET_TAGS, csv, defaultdict, file_area, io, mo, np, pd):
    mo.stop(not file_area.value, mo.md("Upload the log file."))

    file_bytes = file_area.contents()
    text = io.StringIO(file_bytes.decode("utf-8"))
    reader = csv.reader(text)

    timestamps_set = set()
    grouped = defaultdict(list) 
    for row in reader:
        if not row:
            continue
        tag = row[0]
        timestamps_set.add(int(row[1]))
        if tag in TARGET_TAGS:
            grouped[tag].append(row)

    timestamps_ns = np.array(list(timestamps_set), dtype=np.int64)
    timestamps_ns.sort()

    dfs = {}
    for tag, rows in grouped.items():
        df = pd.DataFrame(rows)

        if tag in TAG_COLUMNS:
            df.columns = TAG_COLUMNS[tag][:df.shape[1]]

        dfs[tag] = df
    return dfs, timestamps_ns


@app.cell
def _(dfs, mo, timestamps_ns):
    dfs["AMD"]["timestamp"] = dfs["AMD"]["timestamp"].astype("int")
    dfs["AMD"]["ax"] = dfs["AMD"]["ax"].astype("float")
    dfs["AMD"]["ay"] = dfs["AMD"]["ay"].astype("float")
    dfs["AMD"]["az"] = dfs["AMD"]["az"].astype("float")
    mo.vstack([
        timestamps_ns.min(),
        timestamps_ns.max(),
        (timestamps_ns.max()-timestamps_ns.min())/1000000000/60,
        dfs["AMD"]
    ])
    return


@app.cell
def _(mo, timestamps_ns):
    # UI elements for time axis control
    start_slider = mo.ui.slider(
        start=0,
        stop=int((timestamps_ns.max()-timestamps_ns.min())/1_000_000_000),
        value=0,
        step=1,
        label="Start Time (sec)"
    )
    width_slider = mo.ui.slider(
        start=1,
        stop=60,
        value=30,
        step=1,
        label="Time Window Width (sec)"
    )
    return start_slider, width_slider


@app.cell(hide_code=True)
def _(dfs, mo, plt, start_slider, timestamps_ns, width_slider):
    # Calculate end time based on start and width
    start_time = timestamps_ns.min() + (start_slider.value*1_000_000_000)
    width = width_slider.value*1_000_000_000
    end_time = start_time + width

    # Filter data for the selected time window
    amd_df = dfs["AMD"]
    accel_window = amd_df[(amd_df['timestamp'] >= start_time) & (amd_df['timestamp'] <= end_time)]
    # status_window = status_df[(status_df['Time_ns'] >= start_time) & (status_df['Time_ns'] <= end_time)]

    plt.figure(figsize=(10, 6))
    plt.plot(accel_window['timestamp'], accel_window['ax'], label='ax', color='tab:red')
    plt.plot(accel_window['timestamp'], accel_window['ay'], label='ay', color='tab:green')
    plt.plot(accel_window['timestamp'], accel_window['az'], label='az', color='tab:blue')
    # plt.step(status_window['Time_ns'], status_window['Status'], label='Status', color='tab:orange', where='mid')
    plt.xlabel('Elapsed Time (ns)')
    plt.ylabel('Value')
    plt.title('Acceleration and Status vs Elapsed Time')
    plt.legend()
    plt.tight_layout()

    mo.vstack([
        plt.gca(),
        mo.hstack([start_slider, width_slider])
    ])
    return


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import io
    import csv
    from collections import defaultdict
    import numpy as np
    import matplotlib.pyplot as plt

    TAG_COLUMNS = {
        "ACT": ["tag", "timestamp", "value", "datetime"],
        "DBG": ["tag", "timestamp", "info", "datetime_tz"],
        "AMD": ["tag", "timestamp", "ax", "ay", "az",
                "qx", "qy", "qz", "qw", "counter", "status"],
        "SCY": ["tag", "timestamp", "event", "value"],
        "TRP": ["tag", "timestamp", "type", "end_ts", "count",
                "v1", "v2", "lat", "lon", "score", "a", "b", "c", "flag"],
    }

    TARGET_TAGS = ["ACT", "SCY", "AMD"]
    return TAG_COLUMNS, TARGET_TAGS, csv, defaultdict, io, mo, np, pd, plt


if __name__ == "__main__":
    app.run()
