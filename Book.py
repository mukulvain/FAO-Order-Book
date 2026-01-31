from sortedcontainers import SortedDict


class Book:
    def __init__(self, ticker, is_buy=True):
        self.is_buy = is_buy
        self.queue = SortedDict()
        self.orders = {}
        self.stop_loss_orders = {}
        self.ticker = ticker

    def __repr__(self):
        side = "Buy" if self.is_buy else "Sell"
        return f"<{side} Book: {len(self.orders)} orders>"

    # Fetches the best price of the queue
    def fetch_price(self):
        if not self.queue:
            return 0
        return self.queue.peekitem(-1 if self.is_buy else 0)[0]

    def add(self, order):
        # Adds order to stop loss queue
        if order.is_stop_loss:
            if order.order_number in self.stop_loss_orders:
                del self.stop_loss_orders[order.order_number]
                order.is_stop_loss = False
                if order.is_mkt_order:
                    del self.ticker.repository[order.order_number]
                else:
                    self.ticker.repository[order.order_number].is_stop_loss = False
                    self.add(order)
            else:
                self.stop_loss_orders[order.order_number] = order
        # Adds order to the queue
        else:
            self.orders[order.order_number] = order.limit_price
            if order.limit_price not in self.queue:
                self.queue[order.limit_price] = [order]
            else:
                self.queue[order.limit_price].append(order)

    def delete(self, order_number, is_stop_loss, volume=0):
        if is_stop_loss:
            del self.stop_loss_orders[order_number]
            del self.ticker.repository[order_number]

        # Removes order from queue
        elif order_number in self.orders:
            price = self.orders[order_number]
            target_list = self.queue[price]
            for i, order in enumerate(target_list):
                if order.order_number == order_number:
                    if not volume or order.volume_original == volume:
                        target_list.pop(i)
                        del self.orders[order_number]
                        del self.ticker.repository[order_number]
                    else:
                        target_list[i].volume_original -= volume
                    break
            if not target_list:
                del self.queue[price]

    def _flatten(self, nested_list):
        """Helper to flatten multi-dimensional lists."""
        flat = []
        for item in nested_list:
            if isinstance(item, list):
                flat.extend(self._flatten(item))
            else:
                flat.append(item)
        return flat

    def fetch_data(self, top):
        # Initialize 3D structures: [top_index][algo_index][client_index]
        # Equivalent to np.full((len(top), 2, 3), 0)
        v_orig = [[[0 for _ in range(3)] for _ in range(2)] for _ in range(len(top))]
        v_disc = [[[0 for _ in range(3)] for _ in range(2)] for _ in range(len(top))]

        # Initialize 2D structure for prices: [algo_index][client_index]
        default_price = 0 if self.is_buy else float("inf")
        prices = [[default_price for _ in range(3)] for _ in range(2)]

        keys = list(self.queue.keys())
        if self.is_buy:
            keys.reverse()

        idx = 0
        for key in keys:
            for order in self.queue[key]:
                a_idx = order.algo
                c_idx = order.client - 1

                for i in range(len(top)):
                    if idx < top[i]:
                        v_orig[i][a_idx][c_idx] += order.volume_original
                        v_disc[i][a_idx][c_idx] += min(
                            order.volume_disclosed, order.volume_original
                        )

                if self.is_buy:
                    prices[a_idx][c_idx] = max(order.limit_price, prices[a_idx][c_idx])
                else:
                    prices[a_idx][c_idx] = min(order.limit_price, prices[a_idx][c_idx])

            idx += 1
            if idx >= top[-1]:
                break

        return (self._flatten(v_orig) + self._flatten(v_disc), self._flatten(prices))
