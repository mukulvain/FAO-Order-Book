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


def add_order(ticker, order):
    if order.is_buy:
        ticker.buy_book.add(order)
    else:
        ticker.sell_book.add(order)


def delete_order(ticker, order):
    if order.is_buy:
        ticker.buy_book.delete(order.order_number, order.is_stop_loss)
    else:
        ticker.sell_book.delete(order.order_number, order.is_stop_loss)


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
        converted_time = (trade.trade_time / 65536) % 86400
        trade_ticker = get_ticker(trade)

        while order and order.order_time < trade.trade_time:
            min_time = min(converted_time, threshold)
            while order and (order.order_time / 65536) % 86400 < min_time:
                prev_order = order
                order_ticker = get_ticker(order)
                order_number = order.order_number
                if order_number in order_ticker.repository:
                    prev_order = order_ticker.repository[order_number]

                    if order.activity_type == "CANCEL":
                        delete_order(order_ticker, prev_order)
                        order = get_order(order_reader)
                        continue

                    elif order.activity_type == "MODIFY":
                        delete_order(order_ticker, prev_order)

                if not order.is_stop_loss and (order.is_mkt_order or order.is_ioc):
                    order = get_order(order_reader)
                    continue

                # Adds order
                add_order(order_ticker, order)
                order_ticker.repository[order_number] = order
                order = get_order(order_reader)

            if min_time != converted_time:
                print("Writing snapshot at time:", min_time)
                data.write_snapshot(date, writer, period)
                period += 1
                threshold += INTERVAL

        volume = trade.trade_quantity
        buyer = trade.buy_order_number
        seller = trade.sell_order_number
        trade_ticker.buy_book.delete(buyer, False, volume)
        trade_ticker.sell_book.delete(seller, False, volume)

end = time.time()
elapsed_time = end - start
print("Processing Complete:", date)
print(f"Elapsed time: {elapsed_time:.6f} seconds")
