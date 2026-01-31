class Order:
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
        self.activities = {1: "ENTRY", 3: "CANCEL", 4: "MODIFY"}

        # Standard Identifiers
        self.record = record
        self.segment = segment

        # Order Details
        self.order_number = order_number
        self.order_time = order_time
        self.is_buy = buy_sell_indicator == "B"
        self.activity_type = self.activities[activity_type]

        # Instrument Details
        self.identifier = identifier

        # Specifics
        self.volume_disclosed = (
            volume_disclosed if volume_disclosed else volume_original
        )
        self.volume_original = volume_original
        self.limit_price = limit_price
        self.trigger_price = trigger_price
        self.is_mkt_order = mkt_flag == "Y"
        self.is_stop_loss = on_stop_flag == "Y"
        self.is_ioc = io_flag == "Y"

        # Other Data
        self.spread_comb = spread_comb
        self.algo = algo % 2
        self.client = client
        self.limit_price_indicator = limit_price_indicator

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}(num={self.order_number}, id={self.identifier}, price={self.limit_price})"
