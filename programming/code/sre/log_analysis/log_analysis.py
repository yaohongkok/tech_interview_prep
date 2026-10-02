# Question: Log parsing: read an access log, count requests per endpoint,
# find the top N IPs, compute error rate or p95/p99 latency per minute.

import math
import os
import re
import sys
from collections import Counter, defaultdict

# nginx "combined" format with request time (seconds) appended, e.g.
# 10.0.0.1 - - [01/Oct/2026:10:00:01 +0000] "GET /api/users?id=1 HTTP/1.1" 200 512 0.120
LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ '
    r'\[(?P<ts>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) [^"]*" '
    r'(?P<status>\d{3}) \S+ '
    r'(?P<latency>[\d.]+)'
)

# sample log lives next to this script so it works from any working directory
SAMPLE_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_access_log.txt")


def read_log(path):
    """Yield lines one at a time so a multi-GB file never has to fit in memory."""
    with open(path) as f:
        for line in f:
            yield line.rstrip("\n")


def parse_line(line):
    """Return a dict of fields, or None if the line doesn't match."""
    match = LOG_PATTERN.match(line)
    if not match:
        return None
    return {
        "ip": match["ip"],
        # "01/Oct/2026:10:00:01 +0000" -> "01/Oct/2026:10:00" (bucket by minute)
        "minute": match["ts"][:17],
        # strip the query string so /api/users?id=1 and ?id=2 count together
        "endpoint": match["path"].split("?")[0],
        "status": int(match["status"]),
        "latency": float(match["latency"]),
    }


def percentile(values, pct):
    """Nearest-rank percentile: smallest value with >= pct% of data at or below it."""
    ordered = sorted(values)
    rank = math.ceil(pct / 100 * len(ordered))
    return ordered[max(rank, 1) - 1]


# Running aggregates, updated one line at a time by record_entry(). Memory
# grows with the number of distinct endpoints/IPs/minutes, not with the number
# of lines, so the parsed entries never have to be kept around.
#
# Counter is a dict subclass that maps each item to how many times it was
# seen. A missing key reads as 0 instead of raising KeyError, which is why
# `counter[key] += 1` works without initialising the key first.
# most_common(n) returns [(item, count)] sorted by count, highest first;
# with no argument it returns every item.
endpoint_counts = Counter()  # endpoint -> requests
ip_counts = Counter()  # ip -> requests
minute_totals = Counter()  # minute -> requests
minute_errors = Counter()  # minute -> 5xx responses
# minute -> [latency]. Exact percentiles need every sample, so this is the one
# aggregate that still grows with the line count (one float per request). If
# that is too much, swap the list for a fixed-bucket histogram or a t-digest
# and accept approximate percentiles.
minute_latencies = defaultdict(list)


def record_entry(entry):
    """Fold one parsed line into the running aggregates."""
    endpoint_counts[entry["endpoint"]] += 1
    ip_counts[entry["ip"]] += 1
    minute_totals[entry["minute"]] += 1
    if entry["status"] >= 500:  # 4xx is the client's fault, not ours
        minute_errors[entry["minute"]] += 1
    minute_latencies[entry["minute"]].append(entry["latency"])


def error_rate_per_minute():
    """Return {minute: (total requests, error rate as a percentage)}."""
    result = {}
    for minute, total in minute_totals.items():
        errors = minute_errors[minute]
        error_rate = errors / total * 100
        result[minute] = (total, error_rate)
    return result


def latency_percentiles_per_minute(pcts=(95, 99)):
    """Return {minute: {pct: latency}} for each requested percentile."""
    result = {}
    for minute, latencies in minute_latencies.items():
        by_pct = {}
        for pct in pcts:
            by_pct[pct] = percentile(latencies, pct)
        result[minute] = by_pct
    return result


def analyze(lines, top_n=3):
    # Single pass: each line is parsed, folded into the aggregates, then dropped.
    skipped = 0
    for line in lines:
        entry = parse_line(line)
        if entry is None:
            skipped += 1
            continue
        record_entry(entry)

    print("Requests per endpoint:")
    for endpoint, count in endpoint_counts.most_common():
        print(f"  {endpoint:<15} {count}")

    print(f"\nTop {top_n} IPs:")
    for ip, count in ip_counts.most_common(top_n):
        print(f"  {ip:<15} {count}")

    error_rates = error_rate_per_minute()
    percentiles = latency_percentiles_per_minute()
    minutes = len(error_rates)

    # Average the per-minute values instead of printing every bucket. Each
    # minute counts equally, so a quiet minute weighs as much as a busy one.
    if minutes:
        avg_requests = sum(total for total, _ in error_rates.values()) / minutes
        avg_error_rate = sum(rate for _, rate in error_rates.values()) / minutes
        avg_p95 = sum(by_pct[95] for by_pct in percentiles.values()) / minutes
        avg_p99 = sum(by_pct[99] for by_pct in percentiles.values()) / minutes
        print(f"\nPer-minute average (over {minutes} minute(s)):")
        print(
            f"  requests={avg_requests:.1f}  error_rate={avg_error_rate:.1f}%  "
            f"p95={avg_p95:.3f}s  p99={avg_p99:.3f}s"
        )

    print(f"\nSkipped {skipped} unparseable line(s)")


if __name__ == "__main__":
    # usage: python log_manipulation.py [access.log]
    path = sys.argv[1] if len(sys.argv) > 1 else SAMPLE_LOG_PATH
    analyze(read_log(path))
