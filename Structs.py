from Book import Book

DATA_POINTS = [1, 5]


class Identifier:
    __slots__ = ("description", "buy_book", "sell_book", "repository")

    def __init__(self, description):
        self.description = description
        self.buy_book = Book(self, True)
        self.sell_book = Book(self, False)
        self.repository = {}

    def write_snapshot(self, date, writer, period):
        buy_book = self.buy_book
        sell_book = self.sell_book

        if not buy_book.queue or not sell_book.queue:
            return

        bid_vols, bid_prices = buy_book.fetch_data(DATA_POINTS)
        ask_vols, ask_prices = sell_book.fetch_data(DATA_POINTS)

        best_bid = buy_book.fetch_price()
        best_ask = sell_book.fetch_price()

        spread = best_ask - best_bid

        row = []
        row.extend(bid_vols)
        row.extend(ask_vols)
        row.append(best_bid)
        row.extend(bid_prices)
        row.append(best_ask)
        row.extend(ask_prices)
        row.append(spread)
        row.append(period)

        cleaned = [
            0 if v == float("inf") or v == float("-inf") else int(v) for v in row
        ]
        desc = self.description
        cleaned.extend(
            (
                date,
                desc[:10],
                desc[10:16],
                desc[16:25],
                desc[25:33],
                desc[33:35],
            )
        )

        writer.writerow(cleaned)


class Data:
    __slots__ = ("identifiers",)

    def __init__(self):
        self.identifiers = {}

    def get_ticker(self, ticker):
        key = ticker.identifier
        d = self.identifiers
        if key not in d:
            d[key] = Identifier(key)
        return d[key]

    def write_snapshot(self, date, writer, period):
        for identifier in self.identifiers.values():
            identifier.write_snapshot(date, writer, period)
