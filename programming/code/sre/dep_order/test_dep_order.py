import unittest

from dep_order import CircularDependencyError, can_start_all, get_start_order


class DepOrderTestCase(unittest.TestCase):
    def assert_valid_order(self, deps: dict[str, list[str]], order: list[str]) -> None:
        """Every service appears exactly once, after all of its dependencies."""
        expected = set(deps) | {d for requires in deps.values() for d in requires}
        self.assertEqual(len(order), len(set(order)), "service started twice")
        self.assertEqual(set(order), expected)

        position = {service: i for i, service in enumerate(order)}
        for service, requires in deps.items():
            for dep in requires:
                self.assertLess(
                    position[dep], position[service],
                    f"{service} started before its dependency {dep}",
                )

    def assert_startable(self, deps: dict[str, list[str]]) -> None:
        self.assertTrue(can_start_all(deps))
        self.assert_valid_order(deps, get_start_order(deps))

    def assert_circular(self, deps: dict[str, list[str]]) -> None:
        self.assertFalse(can_start_all(deps))
        with self.assertRaises(CircularDependencyError):
            get_start_order(deps)


class TestStartable(DepOrderTestCase):
    def test_empty(self):
        self.assertTrue(can_start_all({}))
        self.assertEqual(get_start_order({}), [])

    def test_single_service_no_deps(self):
        self.assertTrue(can_start_all({"db": []}))
        self.assertEqual(get_start_order({"db": []}), ["db"])

    def test_independent_services(self):
        deps = {"a": [], "b": [], "c": []}
        self.assert_startable(deps)

    def test_linear_chain(self):
        deps = {"web": ["api"], "api": ["db"], "db": []}
        self.assert_startable(deps)
        self.assertEqual(get_start_order(deps), ["db", "api", "web"])

    def test_diamond(self):
        deps = {
            "web": ["api", "worker"],
            "api": ["db"],
            "worker": ["db"],
            "db": [],
        }
        self.assert_startable(deps)
        order = get_start_order(deps)
        self.assertEqual(order[0], "db")
        self.assertEqual(order[-1], "web")

    def test_multiple_dependencies(self):
        deps = {
            "web": ["api", "cache"],
            "api": ["db", "cache"],
            "cache": [],
            "db": [],
        }
        self.assert_startable(deps)

    def test_disconnected_groups(self):
        deps = {"a": ["b"], "b": [], "x": ["y"], "y": []}
        self.assert_startable(deps)

    def test_dependency_not_declared_as_key(self):
        # "db" only appears as a dependency; it is still a service to start.
        deps = {"api": ["db"]}
        self.assert_startable(deps)
        self.assertEqual(get_start_order(deps), ["db", "api"])

    def test_duplicate_dependency(self):
        deps = {"api": ["db", "db"], "db": []}
        self.assert_startable(deps)
        self.assertEqual(get_start_order(deps), ["db", "api"])

    def test_key_order_does_not_matter(self):
        deps = {"db": [], "api": ["db"], "web": ["api"]}
        reversed_deps = dict(reversed(list(deps.items())))
        self.assert_startable(deps)
        self.assert_startable(reversed_deps)

    def test_long_chain(self):
        # Deep enough to break a naive recursive DFS.
        n = 5000
        deps = {f"s{i}": [f"s{i - 1}"] for i in range(1, n)}
        deps["s0"] = []
        self.assertTrue(can_start_all(deps))
        self.assertEqual(get_start_order(deps), [f"s{i}" for i in range(n)])

    def test_input_not_mutated(self):
        deps = {"web": ["api"], "api": ["db"], "db": []}
        snapshot = {k: list(v) for k, v in deps.items()}
        can_start_all(deps)
        get_start_order(deps)
        self.assertEqual(deps, snapshot)


class TestCircular(DepOrderTestCase):
    def test_self_dependency(self):
        self.assert_circular({"a": ["a"]})

    def test_two_service_cycle(self):
        self.assert_circular({"a": ["b"], "b": ["a"]})

    def test_three_service_cycle(self):
        self.assert_circular({"a": ["b"], "b": ["c"], "c": ["a"]})

    def test_cycle_alongside_valid_services(self):
        deps = {"db": [], "api": ["db"], "x": ["y"], "y": ["x"]}
        self.assert_circular(deps)

    def test_service_depending_on_cycle(self):
        # "web" is not in the cycle but can never start because it needs it.
        deps = {"web": ["a"], "a": ["b"], "b": ["a"]}
        self.assert_circular(deps)

    def test_cycle_reachable_from_valid_service(self):
        # "db" can start, but everything downstream of it is cyclic.
        deps = {"db": [], "a": ["db", "b"], "b": ["a"]}
        self.assert_circular(deps)

    def test_error_names_stuck_services(self):
        deps = {"db": [], "a": ["b"], "b": ["a"]}
        with self.assertRaises(CircularDependencyError) as ctx:
            get_start_order(deps)
        message = str(ctx.exception)
        self.assertIn("a", message)
        self.assertIn("b", message)
        self.assertNotIn("db", message)

    def test_error_is_value_error(self):
        with self.assertRaises(ValueError):
            get_start_order({"a": ["a"]})


if __name__ == "__main__":
    unittest.main()
