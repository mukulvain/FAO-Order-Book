from Book import Book

DATA_POINTS = [1, 5]


class Identifier:
    def __init__(self, description):
        self.description = description
        self.buy_book = Book(self, True)
        self.sell_book = Book(self, False)
        self.repository = {}

    def write_snapshot(self, date, writer, period):
        if self.buy_book.queue and self.sell_book.queue:
            bid_vols, bid_prices = self.buy_book.fetch_data(DATA_POINTS)
            best_bid = self.buy_book.fetch_price()
            ask_vols, ask_prices = self.sell_book.fetch_data(DATA_POINTS)
            best_ask = self.sell_book.fetch_price()
            spread = best_ask - best_bid

            row = (
                bid_vols
                + [best_bid]
                + bid_prices
                + ask_vols
                + [best_ask]
                + ask_prices
                + [spread, period]
            )

            cleaned_row = []
            for val in row:
                if val == float("inf") or val == float("-inf"):
                    cleaned_row.append(0)
                else:
                    cleaned_row.append(int(val))

            final_row = (
                cleaned_row
                + [date]
                + [
                    self.description[:10],
                    self.description[10:16],
                    self.description[16:25],
                    self.description[25:33],
                    self.description[33:35],
                ]
            )
            writer.writerow(final_row)


class Data:
    def __init__(self):
        self.identifiers = {}

    def get_ticker(self, ticker) -> Identifier:
        if ticker.identifier not in self.identifiers:
            self.identifiers[ticker.identifier] = Identifier(ticker.identifier)
        return self.identifiers[ticker.identifier]

    def write_snapshot(self, date, writer, period):
        for identifier in self.identifiers.values():
            identifier.write_snapshot(date, writer, period)
