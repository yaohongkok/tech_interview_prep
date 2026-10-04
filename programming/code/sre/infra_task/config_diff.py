# You have two deployment configs, expected.json (what's in Git) and
# actual.json (what's running).
# Write a function that reports every difference:
# keys added, removed, or changed, using dotted paths for nested keys.
#
# Convention: differences are described going from expected -> actual.
#   added   = key is running but is not in Git
#   removed = key is in Git but is not running
#   changed = key is in both, with a different value
# Only dicts are recursed into. A list is compared as a single value, so a
# list that differs is reported as one "changed" entry at the list's path.

import json
import sys
from typing import Any


def _flatten(value: Any, path: str) -> dict[str, Any]:
    """Return {dotted path: leaf value} for everything under `value`.

    An empty dict has no leaves, so it is kept as a value itself; otherwise
    adding or removing `"labels": {}` would not show up at all.
    """
    if not isinstance(value, dict) or not value:
        return {path: value}

    leaves: dict[str, Any] = {}
    for key, child in value.items():
        leaves.update(_flatten(child, f"{path}.{key}"))
    return leaves


def _same(expected: Any, actual: Any) -> bool:
    """Equal value AND equal type.

    Python says 1 == True and 1 == 1.0, but in a config `replicas: 1` and
    `replicas: true` are not the same setting.
    """
    if type(expected) is not type(actual):
        return False
    if isinstance(expected, list):
        return len(expected) == len(actual) and all(
            _same(e, a) for e, a in zip(expected, actual)
        )
    if isinstance(expected, dict):
        return expected.keys() == actual.keys() and all(
            _same(expected[key], actual[key]) for key in expected
        )
    return expected == actual


def _walk(
    expected: dict[str, Any],
    actual: dict[str, Any],
    prefix: str,
    diff: dict[str, dict[str, Any]],
) -> None:
    """Compare two dicts key by key, recording differences into `diff`."""
    # sorted so the report is in the same order on every run
    for key in sorted(expected.keys() | actual.keys()):
        path = f"{prefix}.{key}" if prefix else key

        if key not in expected:
            diff["added"].update(_flatten(actual[key], path))
        elif key not in actual:
            diff["removed"].update(_flatten(expected[key], path))
        elif isinstance(expected[key], dict) and isinstance(actual[key], dict):
            # Both sides are nested: the difference (if any) is further down.
            _walk(expected[key], actual[key], path, diff)
        elif not _same(expected[key], actual[key]):
            diff["changed"][path] = {
                "expected": expected[key],
                "actual": actual[key],
            }


def diff_configs(
    expected: dict[str, Any], actual: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Report every difference between two configs. O(total keys) time.

    Returns a dict with three keys, each mapping dotted path -> detail:
        "added":   {path: value in actual}
        "removed": {path: value in expected}
        "changed": {path: {"expected": ..., "actual": ...}}
    All three are empty when the configs match.
    """
    diff: dict[str, dict[str, Any]] = {"added": {}, "removed": {}, "changed": {}}
    _walk(expected, actual, "", diff)
    return diff


def format_diff(diff: dict[str, dict[str, Any]]) -> str:
    """Render a diff as one line per difference, git-style (+, -, ~)."""
    lines = [
        *(f"+ {path}: {json.dumps(v)}" for path, v in diff["added"].items()),
        *(f"- {path}: {json.dumps(v)}" for path, v in diff["removed"].items()),
        *(
            f"~ {path}: {json.dumps(v['expected'])} -> {json.dumps(v['actual'])}"
            for path, v in diff["changed"].items()
        ),
    ]
    return "\n".join(lines) if lines else "No differences."


def _load(path: str) -> dict[str, Any]:
    with open(path) as f:
        config = json.load(f)
    if not isinstance(config, dict):
        raise ValueError(f"{path}: top level must be a JSON object")
    return config


if __name__ == "__main__":
    # usage: python config_diff.py expected.json actual.json
    if len(sys.argv) == 3:
        drift = diff_configs(_load(sys.argv[1]), _load(sys.argv[2]))
        print(format_diff(drift))
        # non-zero exit on drift, so this can gate a pipeline (like `diff`)
        sys.exit(1 if any(drift.values()) else 0)

    expected = {
        "service": "api",
        "replicas": 3,
        "image": {"name": "api", "tag": "1.4.2"},
        "env": {"LOG_LEVEL": "info", "TIMEOUT": 30},
        "ports": [80, 443],
    }
    actual = {
        "service": "api",
        "replicas": 5,
        "image": {"name": "api", "tag": "1.4.3"},
        "env": {"LOG_LEVEL": "info", "DEBUG": True},
        "ports": [80, 443, 8080],
        "resources": {"limits": {"cpu": "500m"}},
    }
    print(format_diff(diff_configs(expected, actual)))
    # + env.DEBUG: true
    # + resources.limits.cpu: "500m"
    # - env.TIMEOUT: 30
    # ~ image.tag: "1.4.2" -> "1.4.3"
    # ~ ports: [80, 443] -> [80, 443, 8080]
    # ~ replicas: 3 -> 5
