import collections

import pandas as pd

from eda_invoices.calculations.utils import read_file
from eda_invoices.calculations.utils import split_lines


def filter_rows(rows):
    yield_data_row = False
    for columns in rows:
        # select the lines to keep
        if columns and columns[0] in [
            "MeteringpointID",
            "Energy direction",
            "Metercode",
        ]:
            yield columns
        # find last line, before data rows begin
        elif columns and columns[0] in ["Spaltensumme"]:
            yield_data_row = True
        elif yield_data_row:
            yield columns


def to_df(data, header_row_count=3):
    df = pd.DataFrame(data)
    df = df.set_index(0)

    for label, description in (
        (
            "total_consumption",
            "Gesamtverbrauch lt. Messung (bei Teilnahme gem. Erzeugung) [KWH]",
        ),
        ("local_availability", "Eigendeckung gemeinschaftliche Erzeugung [KWH]"),
        ("local_consumption", "Anteil gemeinschaftliche Erzeugung [KWH]"),
    ):
        df.loc["Metercode"] = df.loc["Metercode"].replace(description, label)

    items = []
    for x in range(header_row_count):
        items += [df.iloc[x].values.tolist()]
    df.columns = list(zip(*items))

    # split headers and data
    df = df[header_row_count:]

    # re-index on datetime
    # use `infer_datetime_format=True` if format is unknown, instead of `format=...`
    df.index = pd.to_datetime(df.index, format="%d.%m.%Y %H:%M:%S")
    df = df.sort_index()

    # strip TOTALS
    selected_columns = [x[0] for x in df.columns.values.tolist()]
    selected_columns = [True if x == "TOTAL" else False for x in selected_columns]
    df = df.drop(df.columns[selected_columns], axis=1)

    # convert all table cells to type numeric
    df = df.apply(pd.to_numeric)
    return df


def group_by_month(df):
    df = df.groupby(by=[df.index.month, df.index.year]).sum()
    return df


def add_prices(df, prices):
    df = df.sort_index()
    df = pd.merge_asof(
        df, prices, left_index=True, right_index=True, direction="backward"
    )
    return df


def split_df(df):
    # select one metering point
    df_left = df.iloc[:, 3:]
    df = df.iloc[:, :3].copy()
    return df, df_left


def parse_raw_data(filename):
    data = read_file(filename)
    data = split_lines(data)
    data = filter_rows(data)
    data = list(data)
    df = to_df(data)

    return df


def split_by_metering_point(df):
    available_metering_points = collections.OrderedDict(
        (x[0], (None, pd.DataFrame())) for x in df.columns.values.tolist()
    )
    for (metering_point_id, energy_direction, _type_label), column in df.items():
        key = metering_point_id
        existing_direction, df = available_metering_points[key]

        if existing_direction:
            assert energy_direction == existing_direction

        # strip metering_point_id and energy direction from column.name
        column.name = column.name[-1]

        available_metering_points[key] = (
            energy_direction,
            pd.concat([df, column], axis=1),
        )

    return available_metering_points
