import csv

from Structs import DATA_POINTS


def write_header(filename):
    clients = ("C", "P", "R")
    algos = ("A", "NA")
    sides = ("Bid", "Ask")
    volumes = ("ActQ", "DiscQ")

    points = tuple(str(p) for p in DATA_POINTS)

    header = []

    # Main depth columns
    header.extend(
        f"{client}{algo}_{side}_{point}{vol}"
        for side in sides
        for vol in volumes
        for point in points
        for algo in algos
        for client in clients
    )

    # Best bid / ask
    for side in sides:
        header.append(f"best_{side}")
        header.extend(
            f"{client}{algo}_best_{side}" for algo in algos for client in clients
        )

    # Metadata
    header.extend(
        (
            "spread",
            "period",
            "date",
            "symbol",
            "instrument",
            "expiry",
            "strike",
            "option_type",
        )
    )

    with open(filename, "w", newline="") as f:
        csv.writer(f).writerow(header)
