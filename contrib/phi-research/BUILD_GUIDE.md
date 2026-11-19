# Build-and-test gate for the Bitcoin Core fork (owner-run)

Status: instructions only. No Bitcoin Core build or CTest run was executed by
the research lab when this document was added. This is not an upstream patch.

Use an **isolated WSL2 Ubuntu installation** (or disposable Linux VM). This is
not intended to create or connect a Bitcoin mainnet node.

## Prerequisites

In Windows PowerShell, if Ubuntu/WSL2 is not installed, refer to Microsoft's
official WSL installation guide. The optional command below requires elevated
permissions and may require a reboot:

    wsl --install -d Ubuntu

In the Ubuntu shell:

    sudo apt update
    sudo apt install -y build-essential cmake python3 libboost-dev git

Check that your installed CMake and compiler meet the requirements in the
checked-out version of doc/dependencies.md and doc/build-unix.md.

## Reproducible sequence

    git clone https://github.com/MichaelWave369/bitcoin.git
    cd bitcoin
    git switch phi-research
    git rev-parse HEAD

Run the fork-only Python tests first:

    python3 -m unittest discover -s contrib/phi-research -p "test_*.py" -v

Then configure a reduced Bitcoin Core build with wallet, GUI, IPC, and ZMQ off:

    cmake -S . -B build -DENABLE_WALLET=OFF -DBUILD_GUI=OFF -DENABLE_IPC=OFF -DWITH_ZMQ=OFF
    cmake --build build -j 4
    ctest --test-dir build --output-on-failure

Do not run bitcoind on the production Bitcoin network during research. The
commands above configure, build, and run local tests; they do not launch a
mainnet node. Some upstream tests may depend on optional packages and skip.

If dependencies/options differ or a build fails, **record the exact commit,
compiler and CMake versions, the failing command, and output**. Do not claim a
passing build or suppress warnings without understanding them.

The full Bitcoin Core functional test runner is documented in test/README.md
and should be attempted only after a successful build and normal unit tests.
Keep third-party build outputs out of commits.

## Governance

- Do not merge research-only files into this fork's upstream-tracking master.
- Do not enable agent publishing, automatic merging, or upstream PR creation.
- Public Bitcoin Core issue and PR discussion must be written by a human.
- Follow upstream doc/AI_POLICY.md, CONTRIBUTING.md and SECURITY.md.
- Agentora mission #124 is a separate qualification gate, not authorization
  to automate a second repository.
