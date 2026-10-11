"""
parser.py - PHASE 2: the Parser.

Job: check that the tokens follow the GRAMMAR (the rules of the language) and
build a tree (the AST) from them.

The grammar of MatrixScript (each rule is one small method below):

    program      ->  statement*
    statement    ->  declaration | assignment | print
    declaration  ->  'matrix' ID '[' NUMBER ']' '[' NUMBER ']'
                       [ '=' '{' NUMBER (',' NUMBER)* '}' ]
    assignment   ->  ID '=' expression
    print        ->  'print' ID
    expression   ->  term   ( '+' term )*        # + is the weaker operator
    term         ->  ID     ( '*' ID   )*        # * binds tighter, so it is
                                                 # handled one level deeper

This is a "recursive descent" parser, but it is NOT deeply recursive: the
repeated parts `( '+' term )*` are plain while-loops. Nothing here calls
itself.
"""

from .ast_nodes import Assignment, BinOp, Declaration, PrintStmt, Var
from .errors import MatrixScriptError, PHASE_PARSER
from .lexer import (
    TOKEN_ASSIGN, TOKEN_COMMA, TOKEN_EOF, TOKEN_ID, TOKEN_LBRACE,
    TOKEN_LBRACKET, TOKEN_MATRIX, TOKEN_NUMBER, TOKEN_PLUS, TOKEN_PRINT,
    TOKEN_RBRACE, TOKEN_RBRACKET, TOKEN_STAR,
)

# Friendly hints that show the correct shape of each statement.
HINT_DECLARATION = "A declaration looks like:  matrix A[2][3]   or   matrix A[2][2] = {1, 2, 3, 4}"
HINT_ASSIGNMENT = "An assignment looks like:  C = A + B   or   C = A * B"
HINT_PRINT = "A print statement looks like:  print C"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens   # always ends with TOKEN_EOF
        self.pos = 0
        self.statements = []
        self.errors = []

    # -- tiny helpers -------------------------------------------------------
    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        token = self.tokens[self.pos]
        if token.type != TOKEN_EOF:
            self.pos += 1
        return token

    def previous(self):
        return self.tokens[self.pos - 1]

    def describe(self, token):
        """How to name a token inside an error message."""
        if token.type == TOKEN_EOF:
            return "the end of the program"
        return f"'{token.lexeme}'"

    def error(self, token, message, hint):
        return MatrixScriptError(PHASE_PARSER, token.line, token.column, message, hint)

    def expect(self, token_type, wanted, hint):
        """Consume a token of the given type, or raise a friendly error."""
        token = self.peek()
        if token.type != token_type:
            raise self.error(token, f"Expected {wanted}, but found {self.describe(token)}.", hint)
        return self.advance()

    # -- the main loop ------------------------------------------------------
    def parse(self):
        """Parse the whole program. Returns (statements, errors)."""
        while self.peek().type != TOKEN_EOF:
            start = self.pos
            try:
                self.statements.append(self.parse_statement())
            except MatrixScriptError as err:
                self.errors.append(err)
                self.skip_rest_of_line(err.line)   # recover, then keep checking
                if self.pos == start:              # safety net: always make progress
                    self.advance()
        return self.statements, self.errors

    def skip_rest_of_line(self, error_line):
        """Error recovery: throw away tokens until the next line begins."""
        while self.peek().type != TOKEN_EOF and self.peek().line <= error_line:
            self.advance()

    # -- statements ---------------------------------------------------------
    def parse_statement(self):
        token = self.peek()
        if token.type == TOKEN_MATRIX:
            stmt = self.parse_declaration()
        elif token.type == TOKEN_PRINT:
            stmt = self.parse_print()
        elif token.type == TOKEN_ID:
            stmt = self.parse_assignment()
        else:
            raise self.error(
                token,
                f"A statement cannot start with {self.describe(token)}.",
                "Every statement starts with 'matrix', 'print', or the name of a matrix.",
            )
        self.expect_end_of_statement()
        return stmt

    def expect_end_of_statement(self):
        """Each statement must be on its own line."""
        last = self.previous()
        nxt = self.peek()
        if nxt.type != TOKEN_EOF and nxt.line == last.line:
            raise self.error(
                nxt,
                f"Unexpected {self.describe(nxt)} - this statement was already complete.",
                "Put each statement on its own line.",
            )

    def parse_declaration(self):
        keyword = self.advance()                                          # 'matrix'
        name = self.expect(TOKEN_ID, "a matrix name after 'matrix'", HINT_DECLARATION)
        self.expect(TOKEN_LBRACKET, "'[' after the matrix name", HINT_DECLARATION)
        rows = self.expect(TOKEN_NUMBER, "the number of rows", HINT_DECLARATION)
        self.expect(TOKEN_RBRACKET, "']' after the number of rows", HINT_DECLARATION)
        self.expect(TOKEN_LBRACKET, "'[' before the number of columns", HINT_DECLARATION)
        cols = self.expect(TOKEN_NUMBER, "the number of columns", HINT_DECLARATION)
        self.expect(TOKEN_RBRACKET, "']' after the number of columns", HINT_DECLARATION)

        values = []
        if self.peek().type == TOKEN_ASSIGN:                              # optional = { ... }
            self.advance()
            self.expect(TOKEN_LBRACE, "'{' to start the list of values", HINT_DECLARATION)
            values.append(self.expect(TOKEN_NUMBER, "a number", HINT_DECLARATION).value)
            while self.peek().type == TOKEN_COMMA:                        # , number
                self.advance()
                values.append(self.expect(TOKEN_NUMBER, "a number after ','", HINT_DECLARATION).value)
            self.expect(TOKEN_RBRACE, "'}' or ',' in the list of values", HINT_DECLARATION)

        return Declaration(name.lexeme, rows.value, cols.value, values, keyword.line, keyword.column)

    def parse_assignment(self):
        target = self.advance()                                           # the ID
        self.expect(TOKEN_ASSIGN, f"'=' after '{target.lexeme}'", HINT_ASSIGNMENT)
        expr = self.parse_expression()
        return Assignment(target.lexeme, expr, target.line, target.column)

    def parse_print(self):
        keyword = self.advance()                                          # 'print'
        name = self.expect(TOKEN_ID, "a matrix name after 'print'", HINT_PRINT)
        return PrintStmt(name.lexeme, keyword.line, keyword.column)

    # -- expressions (loops, not recursion) ---------------------------------
    def parse_expression(self):
        """expression -> term ( '+' term )*"""
        node = self.parse_term()
        while self.peek().type == TOKEN_PLUS:
            op = self.advance()
            right = self.parse_term()
            node = BinOp("+", node, right, op.line, op.column)   # left-associative
        return node

    def parse_term(self):
        """term -> ID ( '*' ID )*"""
        node = self.parse_operand()
        while self.peek().type == TOKEN_STAR:
            op = self.advance()
            right = self.parse_operand()
            node = BinOp("*", node, right, op.line, op.column)
        return node

    def parse_operand(self):
        token = self.expect(TOKEN_ID, "a matrix name", HINT_ASSIGNMENT)
        return Var(token.lexeme, token.line, token.column)


def parse(tokens):
    """Convenience wrapper: parse(tokens) -> (statements, errors)."""
    return Parser(tokens).parse()
