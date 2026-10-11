"""
executor.py - Runs the TAC so the "Print Output" tab has something to show.

This is a tiny TAC interpreter. It is NOT a compiler phase; it only proves that
the generated TAC is correct by actually executing it, one line at a time.

Matrices are plain Python lists of rows:   [[1, 2], [3, 4]]
No NumPy is used, so every step is easy to follow.
"""

from dataclasses import dataclass

from .tac import OP_ADD, OP_COPY, OP_DECLARE, OP_INIT, OP_MUL, OP_PRINT


@dataclass
class PrintResult:
    name: str
    matrix: list     # list of rows
    line: int


def make_zero_matrix(rows, cols):
    return [[0] * cols for _ in range(rows)]


def add_matrices(a, b):
    """Element by element:  result[i][j] = a[i][j] + b[i][j]"""
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def multiply_matrices(a, b):
    """Row-times-column:  result[i][j] = sum over k of a[i][k] * b[k][j]"""
    rows, inner, cols = len(a), len(b), len(b[0])
    result = make_zero_matrix(rows, cols)
    for i in range(rows):
        for j in range(cols):
            for k in range(inner):
                result[i][j] += a[i][k] * b[k][j]
    return result


def clean_number(x):
    """Show 6.0 as 6 and 0.30000000000000004 as 0.3."""
    if isinstance(x, float):
        x = round(x, 6)
        if x == int(x):
            return int(x)
    return x


def format_matrix(matrix):
    """Plain-text version of a matrix, with aligned columns."""
    cells = [[str(clean_number(v)) for v in row] for row in matrix]
    width = max(len(c) for row in cells for c in row)
    return "\n".join("[ " + "  ".join(c.rjust(width) for c in row) + " ]" for row in cells)


def run_tac(code):
    """Execute TAC instructions. Returns a list of PrintResult."""
    memory = {}      # name -> matrix (this is the "RAM" of our tiny machine)
    outputs = []

    for ins in code:
        if ins.op == OP_DECLARE:
            memory[ins.result] = make_zero_matrix(ins.arg1, ins.arg2)

        elif ins.op == OP_INIT:
            matrix = memory[ins.result]
            cols = len(matrix[0])
            for index, value in enumerate(ins.arg1):          # fill row by row
                matrix[index // cols][index % cols] = value

        elif ins.op == OP_ADD:
            memory[ins.result] = add_matrices(memory[ins.arg1], memory[ins.arg2])

        elif ins.op == OP_MUL:
            memory[ins.result] = multiply_matrices(memory[ins.arg1], memory[ins.arg2])

        elif ins.op == OP_COPY:
            memory[ins.result] = [row[:] for row in memory[ins.arg1]]   # a real copy

        elif ins.op == OP_PRINT:
            snapshot = [row[:] for row in memory[ins.result]]
            outputs.append(PrintResult(ins.result, snapshot, ins.line))

    return outputs
