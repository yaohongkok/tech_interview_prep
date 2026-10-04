# Services dependencies are stored in dict[str, list[str]]. Each service is a string.
# Create functions to:
# (1) Check if all services can be started (i.e., no circular dependencies).
# (2) Return a list of services in the order they can be started.
#
# Convention: deps[service] = services that must be started BEFORE `service`.
# A service that only appears as a dependency (not as a key) is treated as a
# service with no dependencies of its own.

from collections import deque


class CircularDependencyError(ValueError):
    """Raised when the services cannot be ordered because of a cycle."""


def _create_intermediate_data_struct(
    deps: dict[str, list[str]],
) -> tuple[dict[str, int], dict[str, list[str]]]:
    """Return (in_degree, dependents) for the dependency graph.

    in_degree[s] = number of not-yet-started dependencies of s
    dependents[d] = services waiting on d (reverse of deps)
    """
    in_degree: dict[str, int] = {}
    dependents: dict[str, list[str]] = {}

    # Each "service requires dep" is an edge dep -> service, so it adds 1 to
    # the service's in-degree.
    for service, requires in deps.items():
        # dedupe (keeping order) so a dependency listed twice is counted once
        unique_requires = list(dict.fromkeys(requires))
        in_degree[service] = len(unique_requires)
        for dep in unique_requires:
            in_degree.setdefault(dep, 0)
            dependents.setdefault(dep, []).append(service)

    return in_degree, dependents


def _calc_service_order(
    in_degree: dict[str, int], dependents: dict[str, list[str]]
) -> list[str]:
    """Calculate services start order

    Decrements `in_degree` in place: afterwards, any service whose count is
    still above 0 was never unblocked.
    """
    # Services with nothing to wait for can start right away.
    ready = deque(s for s, degree in in_degree.items() if degree == 0)
    order: list[str] = []

    # Start a ready service, then tell everything waiting on it that one of
    # its dependencies is now up. A service whose count drops to 0 has all of
    # its dependencies started, so it becomes ready too.
    while ready:
        service = ready.popleft()
        order.append(service)
        for dependent in dependents.get(service, []):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                ready.append(dependent)

    return order


def _start_order(deps: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    """Kahn's algorithm (BFS topological sort). O(V + E) time and space.

    Returns (order, stuck): `order` is the services that can be started, in
    start order; `stuck` is the services that can never start because they are
    in a cycle or depend on one. `stuck` is empty when everything can start.
    """
    in_degree, dependents = _create_intermediate_data_struct(deps)
    order = _calc_service_order(in_degree, dependents)

    # Anything still waiting was never unblocked. Services in a cycle wait on
    # each other, so their counts can never reach 0.
    stuck = [s for s, degree in in_degree.items() if degree > 0]
    return order, stuck


def can_start_all(deps: dict[str, list[str]]) -> bool:
    """(1) True if every service can be started, i.e. no circular dependencies."""
    _, stuck = _start_order(deps)
    return not stuck


def get_start_order(deps: dict[str, list[str]]) -> list[str]:
    """(2) Return the services in an order they can be started.

    Every service appears after all of its dependencies. Raises
    CircularDependencyError if there is a circular dependency.
    """
    order, stuck = _start_order(deps)
    if stuck:
        raise CircularDependencyError(
            f"Circular dependency; cannot start: {sorted(stuck)}"
        )
    return order


if __name__ == "__main__":
    services = {
        "web": ["api", "cache"],
        "api": ["db", "cache"],
        "cache": [],
        "db": [],
    }
    print(can_start_all(services))    # True
    print(get_start_order(services))  # ['cache', 'db', 'api', 'web']

    services["db"] = ["web"]          # web -> api -> db -> web
    print(can_start_all(services))    # False

