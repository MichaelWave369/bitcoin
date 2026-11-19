#!/usr/bin/env python3
"""Read-only, bounded triage for explicitly selected public Bitcoin Core issues."""
import argparse
import json
import sys
from urllib import error, request

API_ROOT = "https://api.github.com/repos/bitcoin/bitcoin/issues/"
WEB_ROOT = "https://github.com/bitcoin/bitcoin/issues/"
MAX_ISSUES = 20


def category(title, labels):
    """Return a rough review hint, never a severity or vulnerability claim."""
    words = (title + " " + " ".join(labels)).lower()
    hints = (
        ("tests", ("test", "ci ", "flaky", "fuzz")),
        ("documentation", ("documentation", "doc:", "readme")),
        ("build", ("build", "cmake", "compiler", "configure")),
        ("network", ("tor", "ipv4", "ipv6", "p2p", "peer", "network")),
        ("wallet", ("wallet", "descriptor", "psbt")),
    )
    return next((name for name, terms in hints if any(t in words for t in terms)), "needs-human-review")


def fetch_issue(number, opener=request.urlopen):
    """Fetch one issue by number from a fixed GitHub public endpoint."""
    if type(number) is not int or not (1 <= number <= 999999):
        raise ValueError("issue number must be an integer between 1 and 999999")
    req = request.Request(
        API_ROOT + str(number),
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "phi-bitcoin-read-only-research",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    with opener(req, timeout=10) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError("unexpected API response")
    if "pull_request" in payload:
        raise ValueError(f"#{number} is a pull request, not an issue")
    if payload.get("number") != number or payload.get("html_url") != WEB_ROOT + str(number):
        raise ValueError(f"unexpected issue identity for #{number}")
    title = payload.get("title")
    if not isinstance(title, str):
        raise ValueError(f"missing title for #{number}")
    raw_labels = payload.get("labels", [])
    if not isinstance(raw_labels, list):
        raise ValueError(f"invalid labels for #{number}")
    labels = [item["name"] for item in raw_labels
              if isinstance(item, dict) and isinstance(item.get("name"), str)]
    return {
        "number": number,
        "title": title,
        "url": WEB_ROOT + str(number),
        "state": payload.get("state"),
        "updated_at": payload.get("updated_at"),
        "labels": labels,
        "category_hint": category(title, labels),
        "assessment": "unverified; human review required",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue", type=int, action="append", required=True,
                        help="Bitcoin Core issue number; repeat for multiple issues")
    args = parser.parse_args(argv)
    numbers = list(dict.fromkeys(args.issue))
    if len(numbers) > MAX_ISSUES:
        parser.error(f"select no more than {MAX_ISSUES} issues")
    try:
        findings = [fetch_issue(n) for n in numbers]
    except (ValueError, error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        print(f"read-only triage failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"source": "bitcoin/bitcoin", "read_only": True,
                      "issues": findings}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
