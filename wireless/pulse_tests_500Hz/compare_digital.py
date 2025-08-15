# compare_digital.py
# Very simple join by nearest time bucket (same HH:MM:SS.mmm string).
# This is coarse because Pi and Xiao timestamps differ; treat as a smoke test.

import csv
from collections import defaultdict

SENT = "sent_digital.csv"
BLE  = "ble_digital.csv"
OUT  = "digital_compare.csv"

def load_csv(path):
    rows = []
    with open(path) as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows

def main():
    sent = load_csv(SENT)    # columns: time,pin_bcm,channel,state
    ble  = load_csv(BLE)     # columns: time,channel,state

    # Index by time string + channel
    sent_idx = defaultdict(list)
    for s in sent:
        sent_idx[(s["time"], s["channel"])].append(s["state"])

    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time","channel","pi_state","xiao_state","match"])
        for b in ble:
            key = (b["time"], b["channel"])
            pi_states = sent_idx.get(key, [])
            # If multiple, just take the last one (or mark "n/a")
            pi_state = pi_states[-1] if pi_states else "n/a"
            match = (pi_state == b["state"])
            w.writerow([b["time"], b["channel"], pi_state, b["state"], match])

    print(f"[compare_digital] Wrote {OUT}")

if __name__ == "__main__":
    main()
