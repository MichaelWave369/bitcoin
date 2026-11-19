"""Offline tests: no network, credentials, or Bitcoin nodes."""
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import triage


class FakeResponse:
    def __init__(self, data):
        self.stream = io.BytesIO(json.dumps(data).encode("utf-8"))

    def __enter__(self):
        return self.stream

    def __exit__(self, *_):
        self.stream.close()


def fake_issue(number=36874, title="build: CMake error", labels=None):
    return {
        "number": number,
        "html_url": triage.WEB_ROOT + str(number),
        "title": title,
        "state": "open",
        "updated_at": "2026-11-19T00:00:00Z",
        "labels": [{"name": label} for label in (labels or [])],
    }


class TriageTests(unittest.TestCase):
    def test_fixed_read_only_endpoint_and_summary(self):
        seen = []

        def opener(req, timeout):
            seen.append((req.full_url, req.get_method(), timeout))
            return FakeResponse(fake_issue())

        result = triage.fetch_issue(36874, opener=opener)
        self.assertEqual(seen, [(triage.API_ROOT + "36874", "GET", 10)])
        self.assertEqual(result["category_hint"], "build")
        self.assertEqual(result["assessment"], "unverified; human review required")
        self.assertNotIn("body", result)

    def test_reject_pull_requests(self):
        item = fake_issue()
        item["pull_request"] = {"url": "unused"}
        with self.assertRaisesRegex(ValueError, "pull request"):
            triage.fetch_issue(36874, opener=lambda *_args, **_kwargs: FakeResponse(item))

    def test_reject_mismatched_identity(self):
        item = fake_issue()
        item["html_url"] = "https://example.com/other"
        with self.assertRaisesRegex(ValueError, "identity"):
            triage.fetch_issue(36874, opener=lambda *_args, **_kwargs: FakeResponse(item))

    def test_reject_invalid_number_without_request(self):
        for number in (0, -1, 1000000, "36874", True):
            with self.subTest(number=number):
                with self.assertRaises(ValueError):
                    triage.fetch_issue(number)

    def test_hints_are_not_factual_findings(self):
        self.assertEqual(triage.category("Maintain Tor IPv4 outbound peer", []), "network")
        self.assertEqual(triage.category("A strange unexplained behavior", []), "needs-human-review")
        self.assertEqual(triage.category("Something", ["documentation"]), "documentation")


if __name__ == "__main__":
    unittest.main()
