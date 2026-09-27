import unittest

from llm_eval.core import Case, FixtureProvider, evaluate


class EvalTests(unittest.TestCase):
    def test_fixture(self):
        report = evaluate(FixtureProvider())
        self.assertEqual(report["summary"]["exact_match"], 1)
        self.assertEqual(report["summary"]["successful"], 3)

    def test_error_is_recorded(self):
        class Broken:
            name = "broken"

            def complete(self, prompt):
                raise TimeoutError("unavailable")

        report = evaluate(Broken(), (Case("x", "hi", "hello"),))
        self.assertEqual(report["summary"]["successful"], 0)
        self.assertEqual(report["summary"]["exact_match"], 0)
        self.assertIn("TimeoutError", report["cases"][0]["error"])
