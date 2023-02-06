def read_file(f, n=None):
    for x, line in enumerate(f):
        if n is not None and x >= n:
            break
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        yield line.rstrip("\r\n").rstrip("\n")


def split_lines(lines):
    for line in lines:
        columns = line.split(",")
        yield columns
