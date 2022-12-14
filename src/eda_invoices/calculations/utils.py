def read_file(f):
    for line in f:
        yield line.rstrip("\n")


def split_lines(lines):
    for line in lines:
        columns = line.split(",")
        yield columns
