from __future__ import annotations

import ast
import os
import sys

print("Python", sys.version, "\n")

failures = 0

for base, _, files in os.walk("."):
    for f in files:
        if not f.endswith(".py"):
            continue
        filename = os.path.normpath(os.path.join(base, f))
        try:
            with open(filename) as fh:
                ast.parse(fh.read())
        except SyntaxError as se:
            failures += 1
            print(
                f"##vso[task.logissue type=error;sourcepath={filename};"
                f"linenumber={se.lineno};columnnumber={se.offset};]"
                f"SyntaxError: {se.msg}"
            )
            print(" " + se.text + " " * se.offset + "^")
            print(f"SyntaxError: {se.msg} in {filename} line {se.lineno}")
            print()

if failures:
    print(f"##vso[task.logissue type=warning]Found {failures} syntax error(s)")
    print(f"##vso[task.complete result=Failed;]Found {failures} syntax error(s)")
