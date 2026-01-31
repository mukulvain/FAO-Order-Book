class Trade:
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

        # Standard Identifiers
        self.record = record
        self.segment = segment
        self.trade_number = trade_number
        self.trade_time = trade_time

        # Instrument Details
        self.identifier = identifier

        # Trade Details
        self.trade_price = trade_price
        self.trade_quantity = trade_quantity

        # Buy Side Details
        self.buy_order_number = buy_order_number
        self.buy_algo = buy_algo % 2
        self.buy_client = buy_client

        # Sell Side Details
        self.sell_order_number = sell_order_number
        self.sell_algo = sell_algo % 2
        self.sell_client_identity = sell_client

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}(num={self.trade_number}, id={self.identifier}, price={self.trade_price}, qty={self.trade_quantity})"
