class Order:
    __slots__ = (
        "record",
        "segment",
        "order_number",
        "order_time",
        "order_time_seconds",
        "is_buy",
        "activity_type",
        "identifier",
        "volume_disclosed",
        "volume_original",
        "limit_price",
        "trigger_price",
        "is_mkt_order",
        "is_stop_loss",
        "is_ioc",
        "spread_comb",
        "algo",
        "client",
        "limit_price_indicator",
    )

    _ACTIVITY_MAP = {1: "ENTRY", 3: "CANCEL", 4: "MODIFY"}

    def __init__(
        self,
        record,
        segment,
        order_number,
        order_time,
        buy_sell_indicator,
        activity_type,
        identifier,
        volume_disclosed,
        volume_original,
        limit_price,
        trigger_price,
        mkt_flag,
        on_stop_flag,
        io_flag,
        spread_comb,
        algo,
        client,
        limit_price_indicator,
    ):
        self.record = record
        self.segment = segment

        self.order_number = order_number
        self.order_time = order_time

        # HOT-PATH OPTIMIZATIONS
        self.order_time_seconds = (order_time / 65536) % 86400
        self.is_buy = buy_sell_indicator == "B"
        self.activity_type = self._ACTIVITY_MAP[activity_type]

        self.identifier = identifier

        self.volume_original = volume_original
        self.volume_disclosed = volume_disclosed or volume_original

        self.limit_price = limit_price
        self.trigger_price = trigger_price

        self.is_mkt_order = mkt_flag == "Y"
        self.is_stop_loss = on_stop_flag == "Y"
        self.is_ioc = io_flag == "Y"

        self.spread_comb = spread_comb
        self.algo = algo & 1
        self.client = client
        self.limit_price_indicator = limit_price_indicator

    def __repr__(self):
        return (
            f"Order(num={self.order_number}, "
            f"id={self.identifier}, price={self.limit_price})"
        )
