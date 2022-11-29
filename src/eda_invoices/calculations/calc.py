import collections
import datetime

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
        ("local_availability", "Anteil gemeinschaftliche Erzeugung [KWH]"),
        ("local_consumption", "Eigendeckung gemeinschaftliche Erzeugung [KWH]"),
        ("local_generation", "Gesamte gemeinschaftliche Erzeugung [KWH]"),
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
    df = df.groupby(
        by=lambda x: datetime.datetime(year=x.year, month=x.month, day=1)
    ).sum()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def group_by_day(df):
    df = df.groupby(by=lambda x: x.date()).sum()
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def add_prices(df, prices):
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
        if not metering_point_id:
            continue
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


def transform(df, config):
    prices_consumption = pd.DataFrame(
        {("", "CONSUMPTION", "prices"): [10, 50]},
        index=[
            pd.Timestamp("2021-01-01 00:00:00"),
            pd.Timestamp("2021-03-01 00:00:00"),
        ],
    )

    prices_generation = pd.DataFrame(
        {("", "GENERATION", "prices"): [40]},
        index=[
            pd.Timestamp("2020-01-01 13:30:00"),
        ],
    )
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # df = df["2021-03-01":"2021-03-31"]

    df = add_prices(df, prices_consumption)
    df = add_prices(df, prices_generation)

    for (metering_point_id, energy_direction, type_label), _data in df.items():
        if energy_direction == "CONSUMPTION" and type_label == "local_consumption":
            df[metering_point_id, energy_direction, "local_costs"] = (
                df[metering_point_id, energy_direction, "local_consumption"]
                * df["", energy_direction, "prices"]
            )
        elif energy_direction == "GENERATION" and type_label == "local_generation":
            df[metering_point_id, energy_direction, "local_income"] = (
                df[metering_point_id, energy_direction, "local_generation"]
                * df["", energy_direction, "prices"]
            )

    # df = df.drop(("", "CONSUMPTION", "prices"), axis=1)
    # df = df.drop(("", "GENERATION", "prices"), axis=1)

    all_metering_data = split_by_metering_point(df)
    for customer in config["customers"]:
        metering_data = []
        for point in customer.metering_points:
            energy_direction, data = all_metering_data.get(
                point.point_id, (None, pd.DataFrame())
            )
            # data = group_by_month(data)
            data = group_by_day(data)
            # import ipdb; ipdb.set_trace()
            data["local_prices"] = (
                data["local_consumption"] / data["local_costs"]
            ).fillna(0)
            # data = data["2021-03-01":"2021-03-31"]

            metering_data.append((point, energy_direction, data))

        print(customer)
        print(metering_data)
        yield customer, metering_data


def calc_totals(metering_data):
    # TODO: calculate total pricing data
    return None


def prepare_invoices(config, df, **extra_kwargs):
    starts_at: datetime.date = (df.index[0]).date()
    stops_at: datetime.date = (df.index[-1]).date()

    for customer, metering_data in transform(df, config):
        total_pricing_data = calc_totals(metering_data)

        yield "invoice.html", {
            "sender": config["sender"],
            "customer": customer,
            "starts_at": starts_at,
            "stops_at": stops_at,
            "metering_data": metering_data,
            "total_pricing_data": total_pricing_data,
        } | extra_kwargs
