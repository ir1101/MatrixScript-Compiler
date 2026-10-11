"""
ast_nodes.py - The shapes of the tree the parser builds (the AST).

AST = Abstract Syntax Tree: the program, but organised as "things" instead of
raw tokens. The parser creates these objects; the semantic analyzer and the
TAC generator read them.

A whole program is simply a list of statements:
    Declaration  ->  matrix A[2][3]            (optionally  = {1, 2, 3, ...})
    Assignment   ->  C = A * B + D
    PrintStmt    ->  print C

Inside an Assignment the right-hand side is an expression tree made of:
    Var    ->  a matrix name such as A
    BinOp  ->  left  (+ or *)  right
"""

from dataclasses import dataclass, field


# --------------------------- expressions -----------------------------------
@dataclass
class Var:
    name: str
    line: int
    column: int


@dataclass
class BinOp:
    op: str          # "+" or "*"
    left: object     # a Var or another BinOp
    right: object    # a Var or another BinOp
    line: int        # position of the operator itself (used in error carets)
    column: int


# --------------------------- statements ------------------------------------
@dataclass
class Declaration:
    name: str
    rows: object                                  # a number token's value (checked later)
    cols: object
    values: list = field(default_factory=list)    # optional initial values, row by row
    line: int = 0
    column: int = 0


@dataclass
class Assignment:
    target: str
    expr: object                                  # a Var or a BinOp
    line: int = 0
    column: int = 0


@dataclass
class PrintStmt:
    name: str
    line: int = 0
    column: int = 0


def expr_to_text(node):
    """Turn an expression tree back into text, e.g. '(A * B) + C'."""
    if isinstance(node, Var):
        return node.name
    left, right = expr_to_text(node.left), expr_to_text(node.right)
    if isinstance(node.left, BinOp):
        left = f"({left})"
    if isinstance(node.right, BinOp):
        right = f"({right})"
    return f"{left} {node.op} {right}"


def statement_to_text(stmt):
    """One-line source-like text of a statement (used by the GUI checklist)."""
    if isinstance(stmt, Declaration):
        text = f"matrix {stmt.name}[{stmt.rows}][{stmt.cols}]"
        if stmt.values:
            text += " = {" + ", ".join(str(v) for v in stmt.values) + "}"
        return text
    if isinstance(stmt, Assignment):
        return f"{stmt.target} = {expr_to_text(stmt.expr)}"
    return f"print {stmt.name}"
