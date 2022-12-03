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
        ("local_quantity", "Eigendeckung gemeinschaftliche Erzeugung [KWH]"),
        ("local_quantity", "Gesamte gemeinschaftliche Erzeugung [KWH]"),
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


def split_df(df):
    # select one metering point
    df_left = df.iloc[:, 3:]
    df = df.iloc[:, :3].copy()
    return df, df_left


def clean_data(filename):
    data = read_file(filename)
    data = split_lines(data)
    data = filter_rows(data)
    data = list(data)
    return data


def split_by_metering_point(df):
    available_metering_points = collections.OrderedDict(
        (x[0], (None, pd.DataFrame(index=pd.to_datetime([]))))
        for x in df.columns.values.tolist()
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


def transform(df, config, prices):
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    all_metering_data = split_by_metering_point(df)
    for customer in config.customers:
        metering_data = []
        for point in customer.metering_points:
            energy_direction, data = all_metering_data.get(
                point.point_id, (None, pd.DataFrame())
            )

            active_tariff = pd.DataFrame(index=pd.to_datetime([]))
            selected_tariff = point.active_tariff or customer.default_tariff
            if selected_tariff in prices:
                active_tariff = prices[selected_tariff]
            data = pd.merge_asof(
                data,
                active_tariff,
                left_index=True,
                right_index=True,
                direction="backward",
            )

            data["local_costs"] = data["local_quantity"] * data["tariff"]
            data = group_by_month(data)
            # data = group_by_day(data)

            data["local_prices_agg"] = (
                data["local_costs"] / data["local_quantity"]
            ).fillna(0)
            # data = data["2021-03-01":"2021-03-04"]

            metering_data.append((point, energy_direction, data))

        print(customer)
        print(metering_data)
        yield customer, metering_data


def calc_totals(metering_data):
    # TODO: calculate total pricing data
    return None


def prices_from_config(config):
    prices = {}
    for tariff in config.tariffs:
        df = pd.DataFrame(
            {"tariff": [p.price for p in tariff.prices]},
            index=[pd.Timestamp(p.date) for p in tariff.prices],
        )
        df.sort_index()
        prices[tariff.name] = df

    return prices


def prepare_invoice_data(config, data, **extra_kwargs):
    df = to_df(data)
    prices = prices_from_config(config)

    starts_at: datetime.date = (df.index[0]).date()
    stops_at: datetime.date = (df.index[-1]).date()

    for customer, metering_data in transform(df, config, prices):
        yield {
            "sender": config.sender,
            "customer": customer,
            "starts_at": starts_at,
            "stops_at": stops_at,
            "metering_data": metering_data,
        } | extra_kwargs
