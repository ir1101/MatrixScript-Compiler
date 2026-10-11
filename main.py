"""
main.py - Run the MatrixScript compiler from the command line.

    python main.py examples/test2_valid_addition.ms

Prints what each phase produced. (The web GUI in app.py shows the same
information in a prettier way.)
"""

import sys

from matrixscript import compile_source, PHASES
from matrixscript.compiler import STATUS_FAILED, STATUS_OK
from matrixscript.executor import format_matrix


def print_error(error, source_lines):
    print(f"  [{error.kind()}] line {error.line}: {error.message}")
    if 1 <= error.line <= len(source_lines):
        print(f"      {error.line} | {source_lines[error.line - 1]}")
        if error.column:
            print(f"      {' ' * len(str(error.line))} | {' ' * (error.column - 1)}^")
    if error.hint:
        print(f"  Hint: {error.hint}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <file.ms>")
        return 2

    # Make sure special characters print correctly on any console.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    with open(sys.argv[1], encoding="utf-8") as f:
        source = f.read()

    result = compile_source(source)

    print("=== PHASES ===")
    for phase in PHASES:
        print(f"  {phase:<18} {result.status[phase].upper()}")

    print("\n=== TOKENS ===")
    for t in result.tokens:
        print(f"  {t.line}:{t.column:<3} {t.type:<15} {t.lexeme!r}")

    if result.checks:
        print("\n=== SEMANTIC CHECKS ===")
        for c in result.checks:
            print(f"  line {c.line}: {'OK  ' if c.ok else 'FAIL'} {c.text}")

    if result.tac:
        print("\n=== THREE-ADDRESS CODE ===")
        for number, ins in enumerate(result.tac, start=1):
            print(f"  {number:>2}: {ins}")

    if result.output:
        print("\n=== PROGRAM OUTPUT ===")
        for item in result.output:
            print(f"{item.name} =")
            print(format_matrix(item.matrix))

    if result.errors:
        print("\n=== COMPILATION FAILED ===")
        lines = source.splitlines()
        for error in result.errors:
            print_error(error, lines)
        return 1

    print("\nCompilation successful.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
