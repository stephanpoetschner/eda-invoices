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


def to_df(data):
    HEADER_COUNT = 3

    df = pd.DataFrame(data)

    # strip TOTALS
    df = df.iloc[:, :-3]

    # split headers and data
    headers, df = df[:HEADER_COUNT], df[HEADER_COUNT:]

    df[0] = pd.to_datetime(df[0])
    df = df.set_index(0)
    df = df.apply(pd.to_numeric)
    return df, headers


def group_by_day(df):
    df = df.groupby(df.index.date).sum()
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
    df, headers = to_df(data)

    headers = headers.iloc[:, 1:]  # strip first column from headers
    df = group_by_day(df)
    return headers, df


def split_by_metering_point(headers, df):
    df_left = df
    headers_left = headers
    while not headers_left.empty:
        next_data_type = headers_left.iloc[1, 0]
        if next_data_type == "CONSUMPTION":
            headers, headers_left = split_df(headers_left)
            metering_id = set(headers.iloc[0, :])
            assert len(metering_id) == 1
            metering_id = metering_id.pop()

            assert set(headers.iloc[1, :]) == {"CONSUMPTION"}

            df, df_left = split_df(df_left)
            df.columns = [
                "total_consumption",
                "internal_available",
                "internal_consumption",
            ]

            yield metering_id, df
        elif next_data_type in ["GENERATION", ""]:
            # ignore generation columns for now
            headers_left = headers_left.iloc[:, 1:]
