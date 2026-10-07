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

import json
import time
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.error import URLError, HTTPError
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor

HcParam = dict[str, Any]        # timeout, retries, backoff, interval, rounds, print_every
Monitor = dict[str, Any]        # url plus its timeout, retries and backoff
Result = dict[str, Any]         # url, ok, status, elapsed, attempts, error
Reporter = Callable[[list[Result]], None]

# Used for any key missing from the config file's "hc_param" section.
DEFAULT_HC_PARAM: HcParam = {
    "timeout": 3.0,     # seconds per attempt
    "retries": 2,       # retries after the first attempt
    "backoff": 0.5,     # seconds before the first retry, doubled each retry
    "interval": 10.0,   # seconds between rounds
    "rounds": 0,        # stop after N rounds (0 = forever)
    "print_every": 1,   # print only every Nth successful check per URL (failures always print)
}

# hc_param keys that a "monitor" entry may override for its own URL
URL_PARAMS: tuple[str, ...] = ("timeout", "retries", "backoff")

CONFIG_PATH: Path = Path(__file__).with_name("config.json")


def reject_unknown_keys(keys: Iterable[str], allowed: Iterable[str], where: str | Path) -> None:
    unknown: set[str] = set(keys) - set(allowed)
    if unknown:
        # a typo like "retires" would otherwise be silently ignored
        raise ValueError(f"unknown key(s) in {where}: {', '.join(sorted(unknown))}")


def validate_hc_param(overrides: dict[str, Any], where: str) -> None:
    """Raise ValueError if the config file's "hc_param" section is invalid."""
    reject_unknown_keys(overrides, DEFAULT_HC_PARAM, where)
    if overrides.get("print_every", DEFAULT_HC_PARAM["print_every"]) < 1:
        raise ValueError("print_every must be >= 1")


def validate_monitors(entries: Any, path: Path) -> None:
    """Raise ValueError if the config file's "monitor" section is invalid."""
    if not isinstance(entries, list) or not entries:
        raise ValueError(f'{path} must have a "monitor" list with at least 1 URL')

    for i, entry in enumerate(entries):
        where: str = f"{path} monitor[{i}]"
        if not isinstance(entry, dict) or not entry.get("url"):
            raise ValueError(f'{where} must be an object with a "url"')
        reject_unknown_keys(entry, ("url", *URL_PARAMS), where)


def validate_config(raw: dict[str, Any], path: Path) -> None:
    """Raise ValueError if raw, the parsed config file at path, is invalid."""
    reject_unknown_keys(raw, ("hc_param", "monitor"), path)
    validate_hc_param(raw.get("hc_param", {}), f"{path} hc_param")
    validate_monitors(raw.get("monitor"), path)


def load_config(path: Path = CONFIG_PATH) -> tuple[HcParam, list[Monitor]]:
    """Return (hc_param, monitors) read from the JSON file at path.

    hc_param is DEFAULT_HC_PARAM overridden by the file's "hc_param" section.
    monitors has one dict per "monitor" entry: its url plus timeout, retries
    and backoff, each taken from the entry if set there, else from hc_param.
    """
    with open(path) as f:
        raw: dict[str, Any] = json.load(f)
    validate_config(raw, path)

    hc_param: HcParam = {**DEFAULT_HC_PARAM, **raw.get("hc_param", {})}

    monitors: list[Monitor] = []
    for entry in raw["monitor"]:
        monitor: Monitor = {"url": entry["url"]}
        for key in URL_PARAMS:
            monitor[key] = entry.get(key, hc_param[key])
        monitors.append(monitor)
    return hc_param, monitors


def check_url(monitor: Monitor) -> Result:
    """Try the monitor's URL up to 1 + retries times; return a result dict.

    The wait before retry n is backoff * 2**(n-1): backoff, 2x, 4x, ...
    """
    url: str = monitor["url"]
    timeout: float = monitor["timeout"]
    retries: int = monitor["retries"]
    backoff: float = monitor["backoff"]

    error: str | None = None
    for attempt in range(retries + 1):
        if attempt > 0:
            time.sleep(backoff * 2 ** (attempt - 1))
        # perf_counter is monotonic, so a system clock change can't skew the timing
        start: float = time.perf_counter()
        try:
            with urlopen(url, timeout=timeout) as response:
                status: int = response.status
            elapsed: float = time.perf_counter() - start
            return {"url": url, "ok": True, "status": status,
                    "elapsed": elapsed, "attempts": attempt + 1, "error": None}
        except HTTPError as httpErr:
            # the server answered, but with 4xx/5xx. Only 5xx and 429 are worth
            # retrying: any other 4xx will fail the same way every time.
            error = f"HTTP {httpErr.code}"
            if httpErr.code < 500 and httpErr.code != 429:
                break
        except URLError as urlErr:
            # DNS failure, connection refused, timeout (TimeoutError is an OSError)
            error = str(getattr(urlErr, "reason", urlErr))
    return {"url": url, "ok": False, "status": None,
            "elapsed": None, "attempts": attempt + 1, "error": error}


def check_all(monitors: list[Monitor]) -> list[Result]:
    """Check every monitor's URL concurrently; results come back in the same order as monitors.

    Each monitor carries its own timeout, retries and backoff (see load_config).

    Threads suit this because the work is I/O-bound: a thread blocked on the
    network releases the GIL, so the others keep running.
    """
    with ThreadPoolExecutor(max_workers=len(monitors)) as pool:
        return list(pool.map(check_url, monitors))


def print_status(hc_results: list[Result], ok_counts: dict[str, int], print_every: int = 1) -> None:
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
def print_reporter(failures: list[Result]) -> None:
    print(f"{len(failures)} URL(s) failed:")
    for r in failures:
        print(f"  {r['url']}  ({r['error']} after {r['attempts']} attempts)")


REPORTERS: list[Reporter] = [print_reporter]

def report_failures(results: list[Result], reporters: list[Reporter] = REPORTERS) -> None:
    failures: list[Result] = [r for r in results if not r["ok"]]
    if not failures:
        return
    for reporter in reporters:
        try:
            reporter(failures)
        except Exception as e:
            # one broken reporter must not stop the others, or the poller
            print(f"reporter {reporter.__name__} failed: {e}")


def main() -> None:
    config, monitors = load_config()

    completed: int = 0
    ok_counts: dict[str, int] = {}
    try:
        while True:
            print(f"[{time.strftime('%H:%M:%S')}] checking {len(monitors)} URL(s)")
            results: list[Result] = check_all(monitors)

            print_status(results, ok_counts, config["print_every"])
            report_failures(results)
            
            completed += 1
            if config["rounds"] and completed >= config["rounds"]:
                break
            time.sleep(config["interval"])
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()




