import unittest

from config_diff import diff_configs, format_diff


def diff(added=None, removed=None, changed=None) -> dict:
    return {"added": added or {}, "removed": removed or {}, "changed": changed or {}}


def change(expected, actual) -> dict:
    return {"expected": expected, "actual": actual}


class TestNoDifference(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(diff_configs({}, {}), diff())

    def test_identical_nested(self):
        config = {"a": 1, "b": {"c": [1, 2], "d": {"e": None}}}
        self.assertEqual(diff_configs(config, config), diff())

    def test_key_order_does_not_matter(self):
        self.assertEqual(diff_configs({"a": 1, "b": 2}, {"b": 2, "a": 1}), diff())


class TestTopLevel(unittest.TestCase):
    def test_added(self):
        self.assertEqual(diff_configs({}, {"a": 1}), diff(added={"a": 1}))

    def test_removed(self):
        self.assertEqual(diff_configs({"a": 1}, {}), diff(removed={"a": 1}))

    def test_changed(self):
        self.assertEqual(
            diff_configs({"a": 1}, {"a": 2}), diff(changed={"a": change(1, 2)})
        )

    def test_all_three(self):
        self.assertEqual(
            diff_configs({"keep": 1, "gone": 2, "edit": 3}, {"keep": 1, "new": 4, "edit": 5}),
            diff(added={"new": 4}, removed={"gone": 2}, changed={"edit": change(3, 5)}),
        )


class TestNested(unittest.TestCase):
    def test_dotted_paths(self):
        expected = {"db": {"host": "a", "pool": {"size": 5, "timeout": 30}}}
        actual = {"db": {"host": "b", "pool": {"size": 5, "max": 10}}}
        self.assertEqual(
            diff_configs(expected, actual),
            diff(
                added={"db.pool.max": 10},
                removed={"db.pool.timeout": 30},
                changed={"db.host": change("a", "b")},
            ),
        )

    def test_added_subtree_is_reported_per_leaf(self):
        self.assertEqual(
            diff_configs({}, {"a": {"b": 1, "c": {"d": 2}}}),
            diff(added={"a.b": 1, "a.c.d": 2}),
        )

    def test_removed_subtree_is_reported_per_leaf(self):
        self.assertEqual(
            diff_configs({"a": {"b": 1, "c": {"d": 2}}}, {}),
            diff(removed={"a.b": 1, "a.c.d": 2}),
        )

    def test_empty_dict_added_and_removed(self):
        self.assertEqual(diff_configs({}, {"a": {}}), diff(added={"a": {}}))
        self.assertEqual(diff_configs({"a": {}}, {}), diff(removed={"a": {}}))

    def test_dict_replaced_by_scalar(self):
        self.assertEqual(
            diff_configs({"a": {"b": 1}}, {"a": "off"}),
            diff(changed={"a": change({"b": 1}, "off")}),
        )

    def test_scalar_replaced_by_dict(self):
        self.assertEqual(
            diff_configs({"a": "off"}, {"a": {"b": 1}}),
            diff(changed={"a": change("off", {"b": 1})}),
        )


class TestValues(unittest.TestCase):
    def test_list_is_compared_as_one_value(self):
        self.assertEqual(
            diff_configs({"ports": [80, 443]}, {"ports": [80, 8443]}),
            diff(changed={"ports": change([80, 443], [80, 8443])}),
        )

    def test_list_order_matters(self):
        self.assertEqual(
            diff_configs({"a": [1, 2]}, {"a": [2, 1]}),
            diff(changed={"a": change([1, 2], [2, 1])}),
        )

    def test_type_change_with_equal_value(self):
        # Python: 1 == True and 1 == 1.0, but these are different settings.
        self.assertEqual(
            diff_configs({"a": 1, "b": 1}, {"a": True, "b": 1.0}),
            diff(changed={"a": change(1, True), "b": change(1, 1.0)}),
        )

    def test_type_change_inside_list(self):
        self.assertEqual(
            diff_configs({"a": [1, {"b": 0}]}, {"a": [1, {"b": False}]}),
            diff(changed={"a": change([1, {"b": 0}], [1, {"b": False}])}),
        )

    def test_null_is_not_missing(self):
        self.assertEqual(
            diff_configs({"a": None}, {}), diff(removed={"a": None})
        )
        self.assertEqual(
            diff_configs({"a": None}, {"a": 0}), diff(changed={"a": change(None, 0)})
        )


class TestFormat(unittest.TestCase):
    def test_no_differences(self):
        self.assertEqual(format_diff(diff_configs({}, {})), "No differences.")

    def test_lines(self):
        result = diff_configs(
            {"a": {"gone": 1, "edit": "x"}}, {"a": {"new": True, "edit": "y"}}
        )
        self.assertEqual(
            format_diff(result),
            '+ a.new: true\n- a.gone: 1\n~ a.edit: "x" -> "y"',
        )


if __name__ == "__main__":
    unittest.main()
