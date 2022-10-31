import click
import pandas as pd


def read_file(filename):
    with open(filename) as f:
        for line in f:
            yield line.rstrip('\n')


def split_lines(lines):
    for line in lines:
        columns = line.split(",")
        yield columns


def filter_rows(rows):
    yield_data_row = False
    for columns in rows:
        # select the lines to keep
        if columns and columns[0] in ["MeteringpointID", "Energy direction", "Metercode"]:
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


def get_data(filename):
    data = read_file(filename)
    data = split_lines(data)
    data = filter_rows(data)
    data = list(data)
    df, headers = to_df(data)

    headers = headers.iloc[:, 1:]  # strip first column from headers
    df = group_by_day(df)

    df_left = df
    headers_left = headers
    import ipdb; ipdb.set_trace()
    while not df_left.empty:
        next_data_type = headers_left.iloc[1, 1]
        if next_data_type == 'CONSUMPTION':
            headers, headers_left = split_df(headers_left)
            assert len(set(headers.iloc[0,:])) == 1
            assert set(headers.iloc[1,:]) == {'CONSUMPTION'}

            df, df_left = split_df(df_left)
            df.columns = ['total_consumption', 'internal_available', 'internal_consumption']

            yield df, headers
        elif next_data_type == 'GENERATION':
            # ignore generation columns for now
            ...


@click.command()
@click.argument('filename', type=click.Path(exists=True))
def cmd(filename):
    print(list(get_data(filename)))


if __name__ == '__main__':
    cmd()
