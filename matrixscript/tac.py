"""
tac.py - PHASE 4: the Three-Address Code (TAC) generator.

TAC is a very simple "assembly-like" language where every line does ONE thing
and has at most THREE addresses (names): two inputs and one output.

    Source:   D = A * B + C

    TAC:      T1 = A * B        <- first operation, result in temporary T1
              T2 = T1 + C       <- second operation, result in temporary T2
              D = T2            <- finally copy the answer into D

T1, T2, ... are "temporaries": names the compiler invents to hold in-between
results. Each instruction is stored as a QUADRUPLE: (op, arg1, arg2, result).
"""

from dataclasses import dataclass

from .ast_nodes import Assignment, Declaration, PrintStmt, Var

# Instruction kinds (the "op" of the quadruple)
OP_DECLARE = "declare"   # declare A[2][3]         arg1=rows arg2=cols result=A
OP_INIT = "init"         # A = {1, 2, 3, ...}      arg1=values       result=A
OP_ADD = "+"             # T1 = A + B
OP_MUL = "*"             # T1 = A * B
OP_COPY = "copy"         # C = T1
OP_PRINT = "print"       # print C


@dataclass
class TACInstruction:
    op: str
    arg1: object = None
    arg2: object = None
    result: str = ""
    line: int = 0          # source line this instruction came from

    def __str__(self):
        if self.op == OP_DECLARE:
            return f"declare {self.result}[{self.arg1}][{self.arg2}]"
        if self.op == OP_INIT:
            return f"{self.result} = {{{', '.join(str(v) for v in self.arg1)}}}"
        if self.op in (OP_ADD, OP_MUL):
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        if self.op == OP_COPY:
            return f"{self.result} = {self.arg1}"
        return f"print {self.result}"


class TACGenerator:
    def __init__(self, statements):
        self.statements = statements
        self.code = []
        self.temp_count = 0

    def new_temp(self):
        """Invent a fresh temporary name: T1, T2, T3, ..."""
        self.temp_count += 1
        return f"T{self.temp_count}"

    def emit(self, op, arg1=None, arg2=None, result="", line=0):
        self.code.append(TACInstruction(op, arg1, arg2, result, line))

    def generate(self):
        """Walk the statements in order and emit TAC for each one."""
        for stmt in self.statements:
            if isinstance(stmt, Declaration):
                self.emit(OP_DECLARE, stmt.rows, stmt.cols, stmt.name, stmt.line)
                if stmt.values:
                    self.emit(OP_INIT, stmt.values, None, stmt.name, stmt.line)

            elif isinstance(stmt, Assignment):
                place = self.gen_expression(stmt.expr)       # where the answer lives
                self.emit(OP_COPY, place, None, stmt.target, stmt.line)

            elif isinstance(stmt, PrintStmt):
                self.emit(OP_PRINT, None, None, stmt.name, stmt.line)
        return self.code

    def gen_expression(self, node):
        """Emit code for an expression and return the name that holds its result."""
        if isinstance(node, Var):
            return node.name                                 # already stored somewhere

        left = self.gen_expression(node.left)                # inputs first ...
        right = self.gen_expression(node.right)
        temp = self.new_temp()                               # ... then one operation
        self.emit(OP_ADD if node.op == "+" else OP_MUL, left, right, temp, node.line)
        return temp


def generate_tac(statements):
    """Convenience wrapper: generate_tac(statements) -> list of TACInstruction."""
    return TACGenerator(statements).generate()
