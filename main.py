import csv
import sys
import time

from reader import get_order, get_trade, line_reader
from Structs import Data
from writer import write_header

# Input Parameters
date = sys.argv[1]
num = int(sys.argv[2])
INTERVAL = int(sys.argv[3])

# File Names
orders_file = f"{date}/FAO_Orders_{date}_{num:02}.DAT.gz"
trades_file = f"{date}/FAO_Trades_{date}_{num:02}.DAT.gz"
output_file = f"LOB/{date}/LOB_{date}_{num:02}.csv"

write_header(output_file)
order_reader = line_reader(orders_file)
trade_reader = line_reader(trades_file)

MARKET_OPENS = 33300  # 09:15:00 in seconds since midnight

trade = None
threshold = MARKET_OPENS
period = 0

start = time.time()
data = Data()
get_ticker = data.get_ticker
order = get_order(order_reader)

with open(output_file, mode="a", newline="") as file:
    writer = csv.writer(file)

    while True:
        trade = get_trade(trade_reader)
        if trade is None:
            data.write_snapshot(date, writer, period)
            break
        trade_time = trade.trade_time_seconds
        trade_ticker = get_ticker(trade)

        while order and order.order_time_seconds <= trade_time:
            min_time = threshold if threshold < trade_time else trade_time

            while order and order.order_time_seconds <= min_time:

                order_ticker = get_ticker(order)
                order_number = order.order_number
                repo = order_ticker.repository
                prev_order = repo.get(order_number)

                if prev_order is not None:
                    if order.activity_type == "CANCEL":
                        if prev_order.is_buy:
                            order_ticker.buy_book.delete(
                                prev_order.order_number, prev_order.is_stop_loss
                            )
                        else:
                            order_ticker.sell_book.delete(
                                prev_order.order_number, prev_order.is_stop_loss
                            )
                        order = get_order(order_reader)
                        continue

                    elif order.activity_type == "MODIFY":
                        if prev_order.is_buy:
                            order_ticker.buy_book.delete(
                                prev_order.order_number, prev_order.is_stop_loss
                            )
                        else:
                            order_ticker.sell_book.delete(
                                prev_order.order_number, prev_order.is_stop_loss
                            )

                if not order.is_stop_loss and (order.is_mkt_order or order.is_ioc):
                    order = get_order(order_reader)
                    continue

                if order.is_buy:
                    order_ticker.buy_book.add(order)
                else:
                    order_ticker.sell_book.add(order)
                repo[order_number] = order
                order = get_order(order_reader)

            if min_time != trade_time:
                data.write_snapshot(date, writer, period)
                period += 1
                threshold += INTERVAL

        volume = trade.trade_quantity
        trade_ticker.buy_book.delete(trade.buy_order_number, False, volume)
        trade_ticker.sell_book.delete(trade.sell_order_number, False, volume)

end = time.time()
elapsed_time = end - start
print("Processing Complete:", date)
print(f"Elapsed time: {elapsed_time:.6f} seconds")
