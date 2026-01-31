import csv

import numpy as np

from Book import Book

DATA_POINTS = [1, 5]


class BaseNode:
    def __init__(self, description):
        self.description = description
        self.children = {}

    def __repr__(self):
        return f"{self.__class__.__name__}({self.description})"

    def _get_child(self, key, child_class):
        if key not in self.children:
            desc = f"{self.description}-{key}"
            self.children[key] = child_class(desc)
        return self.children[key]

    def write_snapshot(self, date, writer, period):
        for child in self.children.values():
            child.write_snapshot(date, writer, period)


class OptionType:
    def __init__(self, description):
        self.description = description
        self.buy_book = Book(self, True)
        self.sell_book = Book(self, False)
        self.repository = {}

    def __repr__(self):
        return f"OptionType({self.description})"

    def write_snapshot(self, date, writer, period):
        if bool(self.buy_book.queue) and bool(self.sell_book.queue):
            bid_volumes, bid_prices = self.buy_book.fetch_data(DATA_POINTS)
            best_bid = self.buy_book.fetch_price()
            ask_volumes, ask_prices = self.sell_book.fetch_data(DATA_POINTS)
            best_ask = self.sell_book.fetch_price()
            spread = best_ask - best_bid
            element = [spread, period]
            row = np.hstack(
                (
                    bid_volumes,
                    [best_bid],
                    bid_prices,
                    ask_volumes,
                    [best_ask],
                    ask_prices,
                    element,
                )
            )
            row = np.where(np.isinf(row), 0, row)
            row = row.astype(int)
            row = np.hstack((row, [date] + self.description.split("-")))

            writer.writerow(row)


class StrikeNode(BaseNode):
    def get_option_type(self, opt_type) -> OptionType:
        return self._get_child(opt_type, OptionType)


class ExpiryNode(BaseNode):
    def get_strike_node(self, strike_price) -> StrikeNode:
        return self._get_child(strike_price, StrikeNode)


class Instrument(BaseNode):
    def get_expiry_node(self, expiry_date) -> ExpiryNode:
        return self._get_child(expiry_date, ExpiryNode)


class Symbol(BaseNode):
    def get_instrument(self, instrument) -> Instrument:
        return self._get_child(instrument, Instrument)


class DataTree:
    def __init__(self):
        self.symbols = {}

    def get_ticker(self, ticker) -> OptionType:
        if ticker.symbol not in self.symbols:
            self.symbols[ticker.symbol] = Symbol(ticker.symbol)

        symbol_node = self.symbols[ticker.symbol]
        instrument = symbol_node.get_instrument(ticker.instrument)
        expiry_node = instrument.get_expiry_node(ticker.expiry_date)
        strike_node = expiry_node.get_strike_node(ticker.strike_price)
        option_type = strike_node.get_option_type(ticker.option_type)

        return option_type

    def write_snapshot(self, date, filename, period):
        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            for symbol in self.symbols.values():
                symbol.write_snapshot(date, writer, period)
