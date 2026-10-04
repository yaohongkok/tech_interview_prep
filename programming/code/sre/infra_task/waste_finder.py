# Our team pays for EBS volumes nobody uses. Using the provided client, 
# write find_waste(client, required_tags) that returns a report of:

# - Unattached volumes: State == "available"
# - Untagged volumes: missing any required tag, and which tags are missing

# The client mimics boto3: results are paginated.
#
# Your can find the fake client in waste_index_helper.py, and a test in waste_index_test.py.

import random
import time
from typing import Any, Callable, Iterable, Iterator

from waste_index_helper import FakeEC2Client, ThrottlingException


def _call_with_retry(
    call: Callable[[], dict[str, Any]],
    max_attempts: int = 8,
    base_delay: float = 0.1,
    max_delay: float = 5.0,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Run `call`, retrying on throttling with exponential backoff.

    Full jitter (a random delay up to the cap) so that many callers throttled
    at the same moment do not all retry at the same moment too.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return call()
        except ThrottlingException:
            if attempt == max_attempts:
                raise
            cap = min(max_delay, base_delay * 2 ** (attempt - 1))
            sleep(random.uniform(0, cap))
    raise ValueError("max_attempts must be at least 1")


def _iter_volumes(client: Any, **retry: Any) -> Iterator[dict[str, Any]]:
    """Yield every volume, following NextToken until the last page.

    The retry wraps a single page, not the whole listing, so a throttle on
    page 50 does not throw away pages 1-49.
    """
    token = None
    while True:
        kwargs = {"NextToken": token} if token else {}
        resp = _call_with_retry(lambda: client.describe_volumes(**kwargs), **retry)
        yield from resp.get("Volumes", [])

        token = resp.get("NextToken")
        if not token:
            return


def find_waste(
    client: Any, required_tags: Iterable[str], **retry: Any
) -> dict[str, Any]:
    """Report unattached and badly tagged EBS volumes. O(volumes) time.

    Returns:
        "unattached":    [{"VolumeId": ..., "SizeGiB": ...}]
        "untagged":      [{"VolumeId": ..., "MissingTags": [...]}]
        "unattached_gib": total size of the unattached volumes
        "scanned":       number of volumes looked at
    A volume can be in both lists. `retry` is passed to _call_with_retry.
    """
    # dict.fromkeys: drop duplicates but keep the caller's order for the report
    required = list(dict.fromkeys(required_tags))
    report: dict[str, Any] = {
        "unattached": [],
        "untagged": [],
        "unattached_gib": 0,
        "scanned": 0,
    }

    for volume in _iter_volumes(client, **retry):
        report["scanned"] += 1
        volume_id = volume["VolumeId"]

        if volume.get("State") == "available":
            size = volume.get("Size", 0)
            report["unattached"].append({"VolumeId": volume_id, "SizeGiB": size})
            report["unattached_gib"] += size

        # "Tags" is absent (not an empty list) on a volume with no tags
        present = {tag["Key"] for tag in volume.get("Tags", [])}
        missing = [key for key in required if key not in present]
        if missing:
            report["untagged"].append({"VolumeId": volume_id, "MissingTags": missing})

    return report


def format_report(report: dict[str, Any]) -> str:
    """Render a report as one line per finding."""
    lines = [f"Scanned {report['scanned']} volumes."]

    lines.append(
        f"Unattached: {len(report['unattached'])} ({report['unattached_gib']} GiB)"
    )
    lines += [f"  {v['VolumeId']}: {v['SizeGiB']} GiB" for v in report["unattached"]]

    lines.append(f"Untagged: {len(report['untagged'])}")
    lines += [
        f"  {v['VolumeId']}: missing {', '.join(v['MissingTags'])}"
        for v in report["untagged"]
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_report(find_waste(FakeEC2Client(), ["Owner", "Env"])))
    # Scanned 5 volumes.
    # Unattached: 2 (550 GiB)
    #   vol-02: 500 GiB
    #   vol-03: 50 GiB
    # Untagged: 3
    #   vol-02: missing Env
    #   vol-03: missing Owner, Env
    #   vol-04: missing Owner
