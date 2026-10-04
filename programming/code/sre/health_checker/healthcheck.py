# Health checker / poller: create a program to continuouslycheck a list of URLs concurrently and:
# 1) with timeouts, 
# 2) retries and 
# 3) exponential backoff,
# The 3 parameters should be configurable. The program should report the status of each URL and 
# the time taken to respond, and if a URL fails to respond after 
# the configured number of retries, it should be reported as failed. 
#
# Then report failures by printing out the failed URLs. 
# However, the printing must occur in a function and 
# be extensible to report the failure in other ways 
# (e.g., sending an email, logging to a file, etc.).

import argparse
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

DEFAULT_URLS = [
    "https://www.google.com",
    "https://www.github.com",
    "https://httpbin.org/status/500",
    "http://localhost:9",  # nothing listens here: connection refused
]


def check_url(url, timeout, retries, backoff):
    """Try a URL up to 1 + retries times; return a result dict.

    The wait before retry n is backoff * 2**(n-1): backoff, 2x, 4x, ...
    """
    error = None
    for attempt in range(retries + 1):
        if attempt > 0:
            time.sleep(backoff * 2 ** (attempt - 1))
        # perf_counter is monotonic, so a system clock change can't skew the timing
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                status = response.status
            elapsed = time.perf_counter() - start
            return {"url": url, "ok": True, "status": status,
                    "elapsed": elapsed, "attempts": attempt + 1, "error": None}
        except urllib.error.HTTPError as e:
            # the server answered, but with 4xx/5xx. Only 5xx and 429 are worth
            # retrying: any other 4xx will fail the same way every time.
            error = f"HTTP {e.code}"
            if e.code < 500 and e.code != 429:
                break
        except (urllib.error.URLError, OSError) as e:
            # DNS failure, connection refused, timeout (TimeoutError is an OSError)
            error = str(getattr(e, "reason", e))
    return {"url": url, "ok": False, "status": None,
            "elapsed": None, "attempts": attempt + 1, "error": error}


def check_all(urls, timeout, retries, backoff):
    """Check every URL concurrently; results come back in the same order as urls.

    Threads suit this because the work is I/O-bound: a thread blocked on the
    network releases the GIL, so the others keep running.
    """
    check_url_lambda = lambda url: check_url(url, timeout, retries, backoff)
    with ThreadPoolExecutor(max_workers=len(urls)) as pool:
        return list(pool.map(check_url_lambda, urls))


def print_status(hc_results, ok_counts, print_every=1):
    """Print every failure, but only every print_every-th success per URL.

    ok_counts maps url -> successes seen so far; the caller keeps it between
    rounds so the count carries over.
    """
    for r in hc_results:
        if r["ok"]:
            ok_counts[r["url"]] = ok_counts.get(r["url"], 0) + 1
            if ok_counts[r["url"]] % print_every != 0:
                continue
            print(f"  OK    {r['url']}  status={r['status']}  "
                  f"time={r['elapsed']:.3f}s  attempts={r['attempts']}")
        else:
            print(f"  FAIL  {r['url']}  error={r['error']}  attempts={r['attempts']}")


# A reporter is any function that takes the list of failed results. To report
# another way (email, log file, pager), write a function with the same
# signature and add it to REPORTERS: nothing else has to change.
def print_reporter(failures):
    print(f"{len(failures)} URL(s) failed:")
    for r in failures:
        print(f"  {r['url']}  ({r['error']} after {r['attempts']} attempts)")


REPORTERS = [print_reporter]


def report_failures(results, reporters=REPORTERS):
    failures = [r for r in results if not r["ok"]]
    if not failures:
        return
    for reporter in reporters:
        try:
            reporter(failures)
        except Exception as e:
            # one broken reporter must not stop the others, or the poller
            print(f"reporter {reporter.__name__} failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Poll a list of URLs and report failures.")
    parser.add_argument("urls", nargs="*", default=DEFAULT_URLS)
    parser.add_argument("--timeout", type=float, default=3.0, help="seconds per attempt")
    parser.add_argument("--retries", type=int, default=2, help="retries after the first attempt")
    parser.add_argument("--backoff", type=float, default=0.5,
                        help="seconds before the first retry, doubled each retry")
    parser.add_argument("--interval", type=float, default=10.0, help="seconds between rounds")
    parser.add_argument("--rounds", type=int, default=0, help="stop after N rounds (0 = forever)")
    parser.add_argument("--print-every", type=int, default=1, metavar="N",
                        help="print only every Nth successful check per URL (failures always print)")
    args = parser.parse_args()
    if args.print_every < 1:
        parser.error("--print-every must be >= 1")

    completed = 0
    ok_counts = {}
    try:
        while True:
            print(f"[{time.strftime('%H:%M:%S')}] checking {len(args.urls)} URL(s)")
            results = check_all(args.urls, args.timeout, args.retries, args.backoff)
            print_status(results, ok_counts, args.print_every)
            report_failures(results)
            completed += 1
            if args.rounds and completed >= args.rounds:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()




