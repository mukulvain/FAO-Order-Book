import csv

from Structs import DATA_POINTS


def write_header(filename, period=True):
    clients = ["C", "P", "R"]
    is_algo = ["A", "NA"]
    is_buy = ["Bid", "Ask"]
    volumes = ["ActQ", "DiscQ"]
    header_list = []
    for buy in is_buy:
        for volume in volumes:
            for point in DATA_POINTS:
                for algo in is_algo:
                    for client in clients:
                        header_list.append(
                            client + algo + "_" + buy + "_" + str(point) + volume
                        )
        header_list.append("best_" + buy)
        for algo in is_algo:
            for client in clients:
                header_list.append(client + algo + "_best_" + buy)
    header_list += [
        "spread",
        "period",
        "date",
        "symbol",
        "instrument",
        "expiry",
        "strike",
        "option_type",
    ]
    with open(filename, mode="w", newline="") as file:
        csv.DictWriter(file, delimiter=",", fieldnames=header_list).writeheader()
