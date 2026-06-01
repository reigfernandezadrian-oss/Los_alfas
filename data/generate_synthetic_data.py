import json
import random
from datetime import datetime, timedelta

def next_weekday(d):
    d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d

def generate_entries(symbol, last_entry, years=4):
    entries = []
    date = datetime.strptime(last_entry["('Date', '')"], "%Y-%m-%d")
    close = last_entry[[k for k in last_entry if 'Close' in k][0]]
    for _ in range(252 * years):
        date = next_weekday(date)
        pct_change = random.gauss(0.0003, 0.015)
        close = round(close * (1 + pct_change), 2)
        high = round(close * (1 + abs(random.gauss(0.002, 0.01))), 2)
        low = round(close * (1 - abs(random.gauss(0.002, 0.01))), 2)
        open_ = round((high + low) / 2, 2)
        volume = int(random.gauss(1_500_000, 400_000))
        entry = {
            "('Date', '')": date.strftime("%Y-%m-%d"),
            f"('Close', '{symbol}')": close,
            f"('High', '{symbol}')": high,
            f"('Low', '{symbol}')": low,
            f"('Open', '{symbol}')": open_,
            f"('Volume', '{symbol}')": volume
        }
        entries.append(entry)
    return entries

def extend_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for symbol, arr in data.items():
        last_entry = arr[-1]
        new_entries = generate_entries(symbol, last_entry, years=5-1)
        arr.extend(new_entries)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    extend_json('data/json_sp500.json')
    extend_json('data/json_ibex35.json')
