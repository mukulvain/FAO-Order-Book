from sortedcontainers import SortedDict


class Book:
    __slots__ = (
        "is_buy",
        "queue",
        "orders",
        "stop_loss_orders",
        "ticker",
    )

    def __init__(self, ticker, is_buy=True):
        self.is_buy = is_buy
        self.queue = SortedDict()
        self.orders = {}
        self.stop_loss_orders = {}
        self.ticker = ticker

    def __repr__(self):
        side = "Buy" if self.is_buy else "Sell"
        return f"<{side} Book: {len(self.orders)} orders>"

    def fetch_price(self):
        if not self.queue:
            return 0
        return self.queue.peekitem(-1 if self.is_buy else 0)[0]

    def add(self, order):
        if order.is_stop_loss:
            sl = self.stop_loss_orders
            repo = self.ticker.repository
            if order.order_number in sl:
                del sl[order.order_number]
                order.is_stop_loss = False
                if order.is_mkt_order:
                    del repo[order.order_number]
                else:
                    repo[order.order_number].is_stop_loss = False
                    self.add(order)
            else:
                sl[order.order_number] = order
            return

        orders = self.orders
        queue = self.queue

        price = order.limit_price
        orders[order.order_number] = price

        level = queue.get(price)
        if level is None:
            queue[price] = [order]
        else:
            level.append(order)

    def delete(self, order_number, is_stop_loss, volume=0):
        repo = self.ticker.repository

        if is_stop_loss:
            del self.stop_loss_orders[order_number]
            del repo[order_number]
            return

        orders = self.orders
        price = orders.get(order_number)
        if price is None:
            return

        level = self.queue[price]
        for i, order in enumerate(level):
            if order.order_number == order_number:
                if not volume or order.volume_original == volume:
                    level.pop(i)
                    del orders[order_number]
                    del repo[order_number]
                else:
                    order.volume_original -= volume
                break

        if not level:
            del self.queue[price]

    def fetch_data(self, top):
        # top: e.g. [1, 5]
        n_levels = top[-1]

        # Preallocate flat arrays (NO nested lists)
        size = len(top) * 2 * 3
        v_orig = [0] * size
        v_disc = [0] * size

        prices = [0 if self.is_buy else float("inf")] * 6

        is_buy = self.is_buy
        queue = self.queue

        idx = 0
        price_iter = reversed(queue.items()) if is_buy else queue.items()

        for price, level in price_iter:
            for order in level:
                a = order.algo
                c = order.client - 1
                base = a * 3 + c

                vo = order.volume_original
                vd = order.volume_disclosed
                vd = vd if vd < vo else vo

                for i, t in enumerate(top):
                    if idx < t:
                        offset = i * 6 + base
                        v_orig[offset] += vo
                        v_disc[offset] += vd

                p_idx = base
                if is_buy:
                    if price > prices[p_idx]:
                        prices[p_idx] = price
                else:
                    if price < prices[p_idx]:
                        prices[p_idx] = price

            idx += 1
            if idx >= n_levels:
                break

        return v_orig + v_disc, prices
