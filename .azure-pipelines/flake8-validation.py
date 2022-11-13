from __future__ import annotations

import os
import subprocess

# Flake8 validation
failures = 0
try:
    flake8 = subprocess.run(
        [
            "flake8",
            "--exit-zero",
        ],
        capture_output=True,
        check=True,
        encoding="latin-1",
        timeout=300,
    )
except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
    print(
        "##vso[task.logissue type=error;]flake8 validation failed with",
        str(e.__class__.__name__),
    )
    print(e.stdout)
    print(e.stderr)
    print("##vso[task.complete result=Failed;]flake8 validation failed")
    exit()
for line in flake8.stdout.split("\n"):
    if ":" not in line:
        continue
    filename, lineno, column, error = line.split(":", maxsplit=3)
    errcode, error = error.strip().split(" ", maxsplit=1)
    filename = os.path.normpath(filename)
    failures += 1
    print(
        f"##vso[task.logissue type=error;sourcepath={filename};"
        f"linenumber={lineno};columnnumber={column};code={errcode};]" + error
    )

if failures:
    print(f"##vso[task.logissue type=warning]Found {failures} flake8 violation(s)")
    print(f"##vso[task.complete result=Failed;]Found {failures} flake8 violation(s)")
