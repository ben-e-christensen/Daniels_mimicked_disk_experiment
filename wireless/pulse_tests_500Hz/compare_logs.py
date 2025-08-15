# compare_logs.py

import csv
from datetime import datetime
from pathlib import Path

SEND_FILE = "sent_analog.csv"
BLE_FILE = "ble_readings.csv"
OUT_CSV = "comparison_results.csv"
OUT_HTML = "comparison_report.html"
MAX_MATCH_WINDOW_MS = 10  # match within ±10 ms

def load_sent():
    sent = []
    with open(SEND_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            sent.append({
                "timestamp": row["timestamp"],
                "channel": row["channel"],
                "voltage": float(row["voltage"]),
                "norm": float(row["norm"]),
                "send_ms": int(row["send_ms"]),
            })
    return sent

def load_ble():
    ble = []
    with open(BLE_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            ble.append({
                "timestamp": row["host_timestamp"],
                "channel": row["channel"],
                "voltage": float(row["voltage"]),
                "time_ms": int(row["time_ms"]),
            })
    return ble

def compare_logs(sent, ble):
    results = []

    for s in sent:
        closest = None
        best_diff = MAX_MATCH_WINDOW_MS + 1

        for b in ble:
            if b["channel"] != s["channel"]:
                continue
            diff = abs(b["time_ms"] - s["send_ms"])
            if diff < best_diff:
                closest = b
                best_diff = diff

        if closest:
            err = round(abs(s["voltage"] - closest["voltage"]), 4)
            delay = closest["time_ms"] - s["send_ms"]
            results.append({
                "channel": s["channel"],
                "send_time": s["send_ms"],
                "recv_time": closest["time_ms"],
                "delay_ms": delay,
                "sent_voltage": round(s["voltage"], 3),
                "recv_voltage": round(closest["voltage"], 3),
                "error_v": err,
                "sent_timestamp": s["timestamp"],
                "recv_timestamp": closest["timestamp"]
            })

    return results

def write_csv(results):
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

def write_html(results):
    html = """<html><head>
    <style>
    table { font-family: monospace; border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #444; padding: 4px 6px; text-align: center; }
    tr:hover { background-color: #eee; }
    </style></head><body><h2>Analog Signal Comparison</h2><table>
    <tr><th>Channel</th><th>Send ms</th><th>Recv ms</th><th>Δt (ms)</th><th>Sent V</th><th>Recv V</th><th>Error (V)</th><th>Send Time</th><th>Recv Time</th></tr>
    """
    for r in results:
        html += f"<tr><td>{r['channel']}</td><td>{r['send_time']}</td><td>{r['recv_time']}</td><td>{r['delay_ms']}</td>"
        html += f"<td>{r['sent_voltage']}</td><td>{r['recv_voltage']}</td><td>{r['error_v']}</td>"
        html += f"<td>{r['sent_timestamp']}</td><td>{r['recv_timestamp']}</td></tr>\n"
    html += "</table></body></html>"

    Path(OUT_HTML).write_text(html)
    print(f"[compare_logs] Wrote HTML: {OUT_HTML}")

if __name__ == "__main__":
    sent = load_sent()
    ble = load_ble()
    results = compare_logs(sent, ble)
    if results:
        write_csv(results)
        write_html(results)
        print(f"[compare_logs] ✅ Compared {len(results)} matched signals")
    else:
        print("[compare_logs] ❌ No matches found.")
