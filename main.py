import datetime as dt
import json
from time import sleep

from pybahn import PyBahn
from pybahn.structs import Date


def mean_time(timedelta_values):
    result = sum(timedelta_values, dt.timedelta(seconds=0)) / len(timedelta_values)
    return result - dt.timedelta(microseconds=result.microseconds)


def fetch_journeys():
    pybahn_date = Date()
    pybahn_date.set_date(12, 1)
    pybahn_date.set_time(9, 0)

    station_names = [
        "Braunschweig Hbf",
        "Dresden Hbf",
        "Frankfurt (Main) Hbf",
        "Köln Hbf",
        "Karlsruhe Hbf",
        "Paderborn Hbf",
        "Potsdam Hbf"
    ]

    bahn = PyBahn()
    station_ids = list(map(
        lambda name: bahn.station(name).lid,
        station_names
    ))

    durations = []
    prices = []
    for to_station in station_ids:
        duration_row = []
        price_row = []
        for from_station in station_ids:
            if from_station == to_station:
                duration_row.append(dt.timedelta(seconds=0))
                price_row.append(0.00)
                continue

            journeys = bahn.journeys(from_station, to_station, pybahn_date)
            duration_row.append(min(dt.timedelta(seconds=j.journey_time_in_seconds) for j in journeys))
            price_row.append(min(float((j.preis or '99.99').removesuffix(' EUR')) for j in journeys))

            # reduce number of requests to the API
            sleep(2)

        duration_row = duration_row + [mean_time(duration_row)]
        durations.append(list(map(str, duration_row)))

        prices.append(price_row + [sum(price_row)])

    with open('journeys.json', 'w') as journeys_file:
        json.dump(dict(
            date=pybahn_date.get(),
            durations=durations,
            prices=prices,
            station_names=station_names
        ), journeys_file)


def print_tables():
    with open('journeys.json', 'r') as journeys_file:
        journeys = json.load(journeys_file)

    print(journeys["date"])
    print()

    def print_row(row):
        print(' '.join(f"{value:>20{'.4' if isinstance(value, float) else ''}}" for value in row))

    station_names = journeys["station_names"]
    print_row(['Zeit'] + station_names + ['Durchschnitt'])
    for i, durations_row in enumerate(journeys["durations"]):
        print_row([station_names[i]] + durations_row)

    print()

    print_row(['Preis'] + station_names + ['Summe'])
    for i, prices_row in enumerate(journeys["prices"]):
        print_row([station_names[i]] + prices_row)


def main():
    try:
        print_tables()
    except FileNotFoundError:
        fetch_journeys()
        print_tables()

if __name__ == "__main__":
    main()
