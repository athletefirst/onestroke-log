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
def _(io, os, zipfile):
    def extract_text_stream(file_area):
        file = file_area.value[0]
        filename = file.name
        ext = os.path.splitext(filename)[1].lower()

        file_bytes = file_area.contents()

        if ext == ".zip":
            # zip file
            zip_file = zipfile.ZipFile(io.BytesIO(file_bytes))
            txt_files = [name for name in zip_file.namelist() if name.endswith(".txt")]
            if not txt_files:
                return ""
            else:
                first_txt = txt_files[0]
                with zip_file.open(first_txt) as f:
                    content = f.read().decode("utf-8", errors="replace")
                return io.StringIO(content)
        else:
            # txt file
            content = file_bytes.decode("utf-8", errors="replace")
            return io.StringIO(content)
    return (extract_text_stream,)


@app.cell
def _(file_area, mo, os):
    mo.stop(not file_area.value, mo.md("Upload the log file."))

    file = file_area.value[0]
    filename = file.name
    ext = os.path.splitext(filename)[1].lower()

    mo.vstack([
        file_area.value,
        file_area.name(),
        ext
    ])
    return


@app.cell
def _(
    TAG_COLUMNS,
    TAG_DTYPES,
    TARGET_TAGS,
    clean_for_dtypes,
    csv,
    defaultdict,
    extract_text_stream,
    file_area,
    mo,
    np,
    pd,
):
    mo.stop(not file_area.value, mo.md("Upload the log file."))

    text = extract_text_stream(file_area)
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

        if tag in TAG_DTYPES:
            df = clean_for_dtypes(df, TAG_DTYPES[tag])
            # df = df.astype(TAG_DTYPES[tag])

        dfs[tag] = df
    return dfs, timestamps_ns


@app.cell
def _(dfs, mo, timestamps_ns):
    mo.vstack([
        timestamps_ns.min(),
        timestamps_ns.max(),
       int( (timestamps_ns.max()-timestamps_ns.min())/1000000000/60 ),
        dfs["TRP"]
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
    acy_df = dfs["SCY"]
    amplitude_window = acy_df[(acy_df['timestamp'] >= start_time) & (acy_df['timestamp'] <= end_time)]
    # status_window = status_df[(status_df['Time_ns'] >= start_time) & (status_df['Time_ns'] <= end_time)]

    plt.figure(figsize=(10, 6))
    plt.plot(accel_window['timestamp'], accel_window['accelX'], label='accelX', color='tab:red')
    plt.plot(accel_window['timestamp'], accel_window['accelY'], label='accelY', color='tab:green')
    plt.plot(accel_window['timestamp'], accel_window['accelZ'], label='accelZ', color='tab:blue')
    plt.plot(amplitude_window['timestamp'], amplitude_window['maxAmplitude'], label='maxAmplitude', color='tab:gray')
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
    import marimo as mo
    import pandas as pd
    import os
    import io
    import csv
    import zipfile
    from collections import defaultdict
    import numpy as np
    import matplotlib.pyplot as plt

    # FutureWarning: Downcasting behavior in replace is deprecated
    # and will be removed in a future version. To retain the old
    # behavior, explicitly call result.infer_objects(copy=False).
    # To opt-in to the future behavior,
    # set pd.set_option('future.no_silent_downcasting', True)
    pd.set_option('future.no_silent_downcasting', True)

    def clean_for_dtypes(df, dtypes):
        for col, dtype in dtypes.items():
            if col not in df.columns:
                continue

            df[col] = df[col].replace("", np.nan)

            # --- float ---
            if dtype.startswith("float"):
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # --- int ---
            elif dtype.startswith("int"):
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

            # --- bool ---
            elif dtype == "bool":
                df[col] = df[col].map({"true": True, "false": False, True: True, False: False})

            # --- string ---
            elif dtype == "string":
                df[col] = df[col].astype("string")

        return df

    TAG_DTYPES = {
        "ACT": {
            "tag": "string", "timestamp": "int64",
            "schemaVersionName": "string",
            "appVersionName": "string",
            "appVersionCode": "int64",
            "activityId": "string",
            "startTimeMillis": "int64",
            "activityName": "string",
            "userName": "string",
        },
        "DBG": {
            "tag": "string", "timestamp": "int64",
            "dbgTag": "string",
            "strings": "string",
        },
        "AMD": {
            "tag": "string", "timestamp": "int64",
            "accelX": "float64",
            "accelY": "float64",
            "accelZ": "float64",
            "qw": "float64",
            "qx": "float64",
            "qy": "float64",
            "qz": "float64",
            "aCounter": "int64",
            "qCounter": "int64",
        },
        "SCY": {
            "tag": "string", "timestamp": "int64",
            "phasePosition": "string",
            "maxAmplitude": "float64",
        },
        "TRP": {
            "tag": "string", "timestamp": "int64",
            "trackPoint": "string",
            "trackPointTimestamp": "int64",
            "strokes": "int32",
            "leftRightBalance": "float64",
            "distance": "float64",
            "latitude": "float64",
            "longitude": "float64",
            "speed": "float64",
            "heartRate": "int32",
            "cadence": "int32",
            "power": "int32",
            "active": "bool",
        },
    }

    TAG_COLUMNS = {
        tag: list(dtypes.keys())
        for tag, dtypes in TAG_DTYPES.items()
    }

    TARGET_TAGS = ["ACT", "AMD", "SCY", "TRP",]
    return (
        TAG_COLUMNS,
        TAG_DTYPES,
        TARGET_TAGS,
        clean_for_dtypes,
        csv,
        defaultdict,
        io,
        mo,
        np,
        os,
        pd,
        plt,
        zipfile,
    )


if __name__ == "__main__":
    app.run()
