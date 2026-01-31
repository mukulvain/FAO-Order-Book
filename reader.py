import gzip

from Order import Order
from Trade import Trade


class AlphaNumeric:
    __slots__ = ("length",)

    def __init__(self, length):
        self.length = length


class Numeric:
    __slots__ = ("length",)

    def __init__(self, length):
        self.length = length


ORDER_SCHEMA = [
    AlphaNumeric(2),
    AlphaNumeric(4),
    Numeric(16),
    Numeric(14),
    AlphaNumeric(1),
    Numeric(1),
    AlphaNumeric(35),
    Numeric(8),
    Numeric(8),
    Numeric(8),
    Numeric(8),
    AlphaNumeric(1),
    AlphaNumeric(1),
    AlphaNumeric(1),
    AlphaNumeric(1),
    Numeric(1),
    Numeric(1),
    AlphaNumeric(1),
]

TRADE_SCHEMA = [
    AlphaNumeric(2),
    AlphaNumeric(4),
    Numeric(17),
    Numeric(14),
    AlphaNumeric(35),
    Numeric(8),
    Numeric(8),
    Numeric(16),
    Numeric(1),
    Numeric(1),
    Numeric(16),
    Numeric(1),
    Numeric(1),
]


def _build_slices(schema):
    slices = []
    ptr = 0
    for field in schema:
        start = ptr
        end = ptr + field.length
        slices.append((start, end, field))
        ptr = end
    return slices


ORDER_SLICES = _build_slices(ORDER_SCHEMA)
TRADE_SLICES = _build_slices(TRADE_SCHEMA)


def to_order(line: bytes) -> Order:
    args = []
    for start, end, field in ORDER_SLICES:
        chunk = line[start:end]
        if isinstance(field, Numeric):
            args.append(int(chunk))
        else:
            args.append(chunk.decode("ascii"))
    return Order(*args)


def to_trade(line: bytes) -> Trade:
    args = []
    for start, end, field in TRADE_SLICES:
        chunk = line[start:end]
        if isinstance(field, Numeric):
            args.append(int(chunk))
        else:
            args.append(chunk.decode("ascii"))
    return Trade(*args)


def line_reader(file_path):
    with gzip.open(file_path, "rb") as file:
        for line in file:
            yield line.rstrip(b"\n")


def get_trade(trade_reader):
    try:
        return to_trade(next(trade_reader))
    except StopIteration:
        return None


def get_order(order_reader):
    try:
        return to_order(next(order_reader))
    except StopIteration:
        return None
