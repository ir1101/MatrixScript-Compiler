"""
semantic.py - PHASE 3: the Semantic Analyzer (the dimension checker).

The parser only knows the SHAPE of a statement. It happily accepts
        C = A * B
even when A and B can never be multiplied. Meaning is checked here.

What this phase does:
    1. Builds the SYMBOL TABLE: a dictionary   name -> (rows, cols)
    2. Checks every statement, one at a time:
         declaration -> size is valid, name is new, value count matches
         assignment  -> names exist, then the DIMENSION RULES below
         print       -> the name exists
    3. Writes a plain-English CHECK LOG (the GUI shows it as a checklist).

Dimension rules (the heart of the project):
    A + B   needs   A.rows == B.rows  AND  A.cols == B.cols   -> result: same size
    A * B   needs   A.cols == B.rows                          -> result: A.rows x B.cols
    C = ... needs   the result size to equal C's declared size
"""

from dataclasses import dataclass

from .ast_nodes import Assignment, BinOp, Declaration, PrintStmt, Var, expr_to_text
from .errors import MatrixScriptError, PHASE_SEMANTIC

MAX_DIM = 10   # keeps demos readable and the program fast


@dataclass
class Symbol:
    name: str
    rows: int
    cols: int
    line: int      # line where it was declared


@dataclass
class Check:
    """One line of the semantic check log."""
    line: int
    ok: bool
    text: str              # e.g. "A.cols (3) = B.rows (3)"
    detail: dict = None    # operand names and sizes, used by the GUI to draw the check


class SemanticAnalyzer:
    def __init__(self, statements):
        self.statements = statements
        self.symbols = {}      # the symbol table
        self.checks = []       # the check log
        self.errors = []

    # -- helpers ------------------------------------------------------------
    def log(self, line, ok, text, detail=None):
        self.checks.append(Check(line, ok, text, detail))

    def fail(self, line, column, message, hint=""):
        return MatrixScriptError(PHASE_SEMANTIC, line, column, message, hint)

    def lookup(self, name, line, column):
        """Find a matrix in the symbol table or complain that it is undeclared."""
        if name not in self.symbols:
            self.log(line, False, f"{name} is declared")
            raise self.fail(
                line, column,
                f"Matrix '{name}' is used here, but it was never declared.",
                f"Declare it first, for example:  matrix {name}[2][2]",
            )
        return self.symbols[name]

    # -- main loop ----------------------------------------------------------
    def analyze(self):
        """Check all statements. Returns (symbols, checks, errors)."""
        for stmt in self.statements:
            try:
                if isinstance(stmt, Declaration):
                    self.check_declaration(stmt)
                elif isinstance(stmt, Assignment):
                    self.check_assignment(stmt)
                elif isinstance(stmt, PrintStmt):
                    self.check_print(stmt)
            except MatrixScriptError as err:
                self.errors.append(err)        # remember it, go on with next statement
        return self.symbols, self.checks, self.errors

    # -- declarations -------------------------------------------------------
    def check_declaration(self, d):
        rows, cols = d.rows, d.cols

        # Is the size a whole number between 1 and MAX_DIM?
        for value in (rows, cols):
            if not isinstance(value, int) or not (1 <= value <= MAX_DIM):
                self.log(d.line, False, f"{d.name} has a valid size")
                raise self.fail(
                    d.line, d.column,
                    f"Matrix '{d.name}' has an invalid size [{rows}][{cols}].",
                    f"Rows and columns must be whole numbers from 1 to {MAX_DIM}.",
                )

        # Is the name still free?
        if d.name in self.symbols:
            first = self.symbols[d.name].line
            self.log(d.line, False, f"{d.name} is not declared twice")
            raise self.fail(
                d.line, d.column,
                f"Matrix '{d.name}' is already declared on line {first}.",
                "Every matrix can be declared only once. Pick a different name.",
            )

        self.symbols[d.name] = Symbol(d.name, rows, cols, d.line)
        self.log(d.line, True, f"{d.name} declared as {rows}x{cols}")

        # If initial values were given, there must be exactly rows*cols of them.
        if d.values:
            needed = rows * cols
            if len(d.values) != needed:
                self.log(d.line, False, f"{d.name} needs {needed} values, got {len(d.values)}")
                raise self.fail(
                    d.line, d.column,
                    f"Matrix '{d.name}' is {rows}x{cols}, so it needs exactly "
                    f"{needed} values, but {len(d.values)} were given.",
                    f"Write {needed} numbers inside the braces, row by row.",
                )
            self.log(d.line, True, f"{d.name} has the right number of values ({needed})")

    # -- print --------------------------------------------------------------
    def check_print(self, p):
        self.lookup(p.name, p.line, p.column)
        self.log(p.line, True, f"{p.name} is declared, so it can be printed")

    # -- assignments (where the dimension checking happens) -----------------
    def check_assignment(self, a):
        target = self.lookup(a.target, a.line, a.column)
        rows, cols = self.size_of(a.expr)            # size of the right-hand side

        if (rows, cols) != (target.rows, target.cols):
            self.log(a.line, False, f"result {rows}x{cols} fits {a.target} ({target.rows}x{target.cols})",
                     detail("=", a.target, expr_to_text(a.expr), (target.rows, target.cols), (rows, cols), None))
            raise self.fail(
                a.line, a.column,
                f"Cannot store a {rows}x{cols} result in '{a.target}', "
                f"which was declared as {target.rows}x{target.cols}.",
                f"Declare it as  matrix {a.target}[{rows}][{cols}]  or change the "
                f"expression so it produces a {target.rows}x{target.cols} matrix.",
            )
        self.log(a.line, True, f"result {rows}x{cols} fits {a.target} ({target.rows}x{target.cols})",
                 detail("=", a.target, expr_to_text(a.expr), (target.rows, target.cols), (rows, cols), (rows, cols)))

    def size_of(self, node):
        """Work out (rows, cols) of an expression, checking every operator on the way.

        This is the only recursive method, and it only goes as deep as the
        expression is long: A * B + C is just two levels.
        """
        if isinstance(node, Var):
            symbol = self.lookup(node.name, node.line, node.column)
            node.size = (symbol.rows, symbol.cols)          # annotate the tree
            return node.size

        left_size = self.size_of(node.left)
        right_size = self.size_of(node.right)
        left, right = operand_text(node.left), operand_text(node.right)

        if node.op == "+":
            node.size = self.check_addition(node, left, right, left_size, right_size)
        else:
            node.size = self.check_multiplication(node, left, right, left_size, right_size)
        return node.size                                    # annotate the tree

    def check_addition(self, node, left, right, lsize, rsize):
        """Rule for +  : both sides must have exactly the same size."""
        (lrows, lcols), (rrows, rcols) = lsize, rsize
        if lsize != rsize:
            self.log(node.line, False, f"{left} + {right}: sizes differ ({lrows}x{lcols} vs {rrows}x{rcols})",
                     detail(node.op, left, right, lsize, rsize, None))
            raise self.fail(
                node.line, node.column,
                f"Cannot add {left} ({lrows}x{lcols}) and {right} ({rrows}x{rcols}): "
                f"matrices can only be added when they have the same number of rows and columns.",
                f"Make both operands the same size, for example declare both as "
                f"[{lrows}][{lcols}].",
            )
        self.log(node.line, True, f"{left} + {right}: both are {lrows}x{lcols}, so the result is {lrows}x{lcols}",
                 detail(node.op, left, right, lsize, rsize, lsize))
        return lsize

    def check_multiplication(self, node, left, right, lsize, rsize):
        """Rule for *  : columns of the left side must equal rows of the right side."""
        (lrows, lcols), (rrows, rcols) = lsize, rsize
        if lcols != rrows:
            self.log(node.line, False, f"{left} * {right}: {left}.cols ({lcols}) is not equal to {right}.rows ({rrows})",
                     detail(node.op, left, right, lsize, rsize, None))
            hint = (f"For {left} * {right}, the number of COLUMNS of the left matrix "
                    f"must equal the number of ROWS of the right matrix. "
                    f"Here the left has {lcols} columns but the right has {rrows} rows.")
            if rcols == lrows:                          # would swapping the order work?
                hint += f" Tip: {right} * {left} would be valid ({rrows}x{rcols} times {lrows}x{lcols})."
            raise self.fail(
                node.line, node.column,
                f"Cannot multiply {left} ({lrows}x{lcols}) by {right} ({rrows}x{rcols}): "
                f"{left} has {lcols} columns but {right} has {rrows} rows.",
                hint,
            )
        self.log(node.line, True, f"{left} * {right}: {left}.cols ({lcols}) equals {right}.rows ({rrows}), so the result is {lrows}x{rcols}",
                 detail(node.op, left, right, lsize, rsize, (lrows, rcols)))
        return lrows, rcols


def detail(op, left, right, left_size, right_size, result_size):
    """Structured version of a check, so the GUI can draw the matrix shapes."""
    return {"op": op, "left": left, "right": right,
            "left_size": left_size, "right_size": right_size, "result_size": result_size}


def operand_text(node):
    """Name of a variable, or '(A * B)' for a sub-expression - used in messages."""
    text = expr_to_text(node)
    return f"({text})" if isinstance(node, BinOp) else text


def analyze(statements):
    """Convenience wrapper: analyze(statements) -> (symbols, checks, errors)."""
    return SemanticAnalyzer(statements).analyze()
