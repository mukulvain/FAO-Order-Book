class Trade:
    __slots__ = (
        "record",
        "segment",
        "trade_number",
        "trade_time",
        "trade_time_seconds",
        "identifier",
        "trade_price",
        "trade_quantity",
        "buy_order_number",
        "buy_algo",
        "buy_client",
        "sell_order_number",
        "sell_algo",
        "sell_client_identity",
    )

    def __init__(
        self,
        record,
        segment,
        trade_number,
        trade_time,
        identifier,
        trade_price,
        trade_quantity,
        buy_order_number,
        buy_algo,
        buy_client,
        sell_order_number,
        sell_algo,
        sell_client,
    ):
        self.record = record
        self.segment = segment

        self.trade_number = trade_number
        self.trade_time = trade_time
        self.trade_time_seconds = (trade_time / 65536) % 86400

        self.identifier = identifier

        self.trade_price = trade_price
        self.trade_quantity = trade_quantity

        self.buy_order_number = buy_order_number
        self.buy_algo = buy_algo & 1
        self.buy_client = buy_client

        self.sell_order_number = sell_order_number
        self.sell_algo = sell_algo & 1
        self.sell_client_identity = sell_client

    def __repr__(self):
        return (
            f"Trade(num={self.trade_number}, "
            f"id={self.identifier}, "
            f"price={self.trade_price}, "
            f"qty={self.trade_quantity})"
        )
