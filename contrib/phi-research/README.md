# Phi Bitcoin Research Lab (fork-only experiment)

This directory is **research tooling in MichaelWave369's fork**, not part of
upstream Bitcoin Core and not a proposed upstream patch.

## Mission

Collect a small, explicitly selected set of *public* Bitcoin Core issue
metadata for human review and reproducible local analysis. Start read-only.
Do not modify consensus code, send transactions, contact peers, or open PRs.

## Guardrails

- The program sends only GET requests to the fixed public GitHub API endpoint
  for the bitcoin/bitcoin repository and explicit issue numbers.
- No tokens, write APIs, bots posting comments, or agent-driven pull requests.
- It does not execute issue text, clone repositories, build Bitcoin Core, or
  connect to the Bitcoin network. Issue titles/labels are untrusted data.
- A category is a simple keyword hint, **not** a confirmed diagnosis, severity,
  security finding, or proof that an issue is actionable.
- Follow the official Bitcoin Core AI policy:
  https://github.com/bitcoin/bitcoin/blob/master/doc/AI_POLICY.md
  A human must choose, understand and explain upstream contributions. The
  policy prohibits autonomous agents from opening or driving upstream PRs
  and AI-generated comments to upstream maintainers.
- Report suspected security vulnerabilities privately per SECURITY.md, not
  through public issue comments:
  https://github.com/bitcoin/bitcoin/blob/master/SECURITY.md
- Keep this experiment isolated on phi-research. Do not merge this fork-only
  tooling into master.

## Requirements

Python 3.10+ standard library. No installation or token needed. GitHub's
unauthenticated API rate limit applies.

## Run from repository root

    python3 contrib/phi-research/triage.py --issue 36874 --issue 36913
    python3 -m unittest discover -s contrib/phi-research -p "test_*.py" -v

The program prints JSON to standard output. Network failures exit nonzero.
It does not write reports, modify the repository, or open pull requests.

## CI on this fork

The fork-only workflow at `.github/workflows/phi-research-ci.yml` is scoped
to pushes to `phi-research` and the research directory. It uses a pinned
GitHub-owned checkout action, read-only contents permission, no repository
secrets, and 11 offline unit tests.

A second, **non-blocking** job makes unauthenticated GET requests for two
known public issues. Its result is separate from offline tests; GitHub API
rate limiting or network failures must not be mistaken for a successful
live smoke test. Inspect both job results.

GitHub normally leaves Actions disabled on newly created forks. The owner
may need to enable Actions in the fork's Actions tab. Merely committing a
workflow does not prove GitHub ran it.

## Isolated Bitcoin Core build gate

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for owner-run WSL2/Linux commands to
compile and test Bitcoin Core without launching a mainnet node. Those CMake
and CTest commands have **not** been executed as part of this experiment.

## Next gates

1. Validate offline unit tests and capture one example triage run.
2. Human selects one narrow, non-consensus issue for manual review.
3. Only after the existing Agentora R9 / Autonomous R1 lane is field-qualified,
   and this repo is explicitly allowlisted, consider orchestration integration.
   There is no delegated GitHub write/merge authority here.
4. Any upstream patch requires human understanding, real Bitcoin Core tests,
   and compliance with the upstream AI policy.

Tracking context: https://github.com/MichaelWave369/Agentora/issues/124
