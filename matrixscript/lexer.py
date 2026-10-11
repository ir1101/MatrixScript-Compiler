"""
lexer.py - PHASE 1: the Lexer (a.k.a. scanner / tokenizer).

Job: turn raw text into a list of labelled pieces called TOKENS.

    "C = A + B"   --->   TOKEN_ID(C)  TOKEN_ASSIGN(=)  TOKEN_ID(A)
                         TOKEN_PLUS(+)  TOKEN_ID(B)

The lexer does not care whether the tokens make sense together (that is the
parser's job). It only checks that every character belongs to the language.
"""

from dataclasses import dataclass

from .errors import MatrixScriptError, PHASE_LEXER

# ---------------------------------------------------------------------------
# Token types (the "labels").
# ---------------------------------------------------------------------------
TOKEN_MATRIX = "TOKEN_MATRIX"      # the keyword  matrix
TOKEN_PRINT = "TOKEN_PRINT"        # the keyword  print
TOKEN_ID = "TOKEN_ID"              # a name such as A, B, result
TOKEN_NUMBER = "TOKEN_NUMBER"      # 2, 15, -3, 4.5
TOKEN_PLUS = "TOKEN_PLUS"          # +
TOKEN_STAR = "TOKEN_STAR"          # *
TOKEN_ASSIGN = "TOKEN_ASSIGN"      # =
TOKEN_LBRACKET = "TOKEN_LBRACKET"  # [
TOKEN_RBRACKET = "TOKEN_RBRACKET"  # ]
TOKEN_LBRACE = "TOKEN_LBRACE"      # {
TOKEN_RBRACE = "TOKEN_RBRACE"      # }
TOKEN_COMMA = "TOKEN_COMMA"        # ,
TOKEN_EOF = "TOKEN_EOF"            # marks the end of the input

# Words with a special meaning. Everything else made of letters is an ID.
KEYWORDS = {
    "matrix": TOKEN_MATRIX,
    "print": TOKEN_PRINT,
}

# Characters that are a complete token all by themselves.
SINGLE_CHAR_TOKENS = {
    "+": TOKEN_PLUS,
    "*": TOKEN_STAR,
    "=": TOKEN_ASSIGN,
    "[": TOKEN_LBRACKET,
    "]": TOKEN_RBRACKET,
    "{": TOKEN_LBRACE,
    "}": TOKEN_RBRACE,
    ",": TOKEN_COMMA,
}


def is_letter(ch):
    """True for A-Z, a-z and _ (ASCII only, so odd Unicode never sneaks in)."""
    return ch != "" and ch.isascii() and (ch.isalpha() or ch == "_")


def is_digit(ch):
    """True for 0-9 only."""
    return ch != "" and ch.isascii() and ch.isdigit()


def is_word_char(ch):
    """Letters, digits or underscore - the characters allowed inside a name."""
    return is_letter(ch) or is_digit(ch)


@dataclass
class Token:
    type: str      # one of the TOKEN_* labels above
    lexeme: str    # the exact text, e.g. "A" or "+"
    value: object  # the real value for numbers (int/float); same as lexeme otherwise
    line: int      # 1-based line number
    column: int    # 1-based column number


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0       # index of the character we are looking at
        self.line = 1
        self.column = 1
        self.tokens = []
        self.errors = []

    # -- tiny helpers -------------------------------------------------------
    def peek(self, offset=0):
        """Look at a character without consuming it ('' if past the end)."""
        i = self.pos + offset
        return self.source[i] if i < len(self.source) else ""

    def advance(self):
        """Consume one character and keep line/column up to date."""
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def add_token(self, type_, lexeme, value, line, column):
        self.tokens.append(Token(type_, lexeme, value, line, column))

    def add_error(self, line, column, message, hint):
        self.errors.append(MatrixScriptError(PHASE_LEXER, line, column, message, hint))

    # -- main loop ----------------------------------------------------------
    def tokenize(self):
        """Scan the whole source. Returns (tokens, errors)."""
        while self.pos < len(self.source):
            ch = self.peek()
            line, column = self.line, self.column  # where this token starts

            if ch in " \t\r\n":                      # 1. skip whitespace
                self.advance()

            elif ch == "#":                          # 2. skip comments
                while self.peek() not in ("\n", ""):
                    self.advance()

            elif is_letter(ch):                      # 3. word: keyword or name
                self.read_word(line, column)

            elif is_digit(ch) or (ch == "-" and is_digit(self.peek(1))):
                self.read_number(line, column)       # 4. number (may start with -)

            elif ch in SINGLE_CHAR_TOKENS:           # 5. + * = [ ] { } ,
                self.advance()
                self.add_token(SINGLE_CHAR_TOKENS[ch], ch, ch, line, column)

            else:                                    # 6. anything else is illegal
                self.advance()
                self.report_illegal_character(ch, line, column)

        self.add_token(TOKEN_EOF, "", "", self.line, self.column)
        return self.tokens, self.errors

    # -- the three small readers -------------------------------------------
    def read_word(self, line, column):
        start = self.pos
        while is_word_char(self.peek()):
            self.advance()
        word = self.source[start:self.pos]
        token_type = KEYWORDS.get(word, TOKEN_ID)    # keyword or plain name?
        self.add_token(token_type, word, word, line, column)

    def read_number(self, line, column):
        start = self.pos
        if self.peek() == "-":
            self.advance()
        while is_digit(self.peek()):
            self.advance()
        if self.peek() == "." and is_digit(self.peek(1)):  # decimal part
            self.advance()
            while is_digit(self.peek()):
                self.advance()

        # A number glued to letters (like 2A) is a malformed token.
        if is_letter(self.peek()):
            while is_word_char(self.peek()):
                self.advance()
            bad = self.source[start:self.pos]
            self.add_error(
                line, column,
                f"'{bad}' is not a valid name or number.",
                "Names must start with a letter or underscore (for example A1). "
                "Numbers cannot have letters stuck to them.",
            )
            return

        text = self.source[start:self.pos]
        value = float(text) if "." in text else int(text)
        self.add_token(TOKEN_NUMBER, text, value, line, column)

    def report_illegal_character(self, ch, line, column):
        if ch == "-":
            hint = ("MatrixScript has no subtraction. Use only + and *. "
                    "A '-' is allowed only directly before a number, like -3.")
        else:
            hint = ("MatrixScript only understands letters, digits, "
                    "+ * = [ ] { } , and # comments.")
        self.add_error(line, column, f"Unexpected character '{ch}'.", hint)


def tokenize(source):
    """Convenience wrapper: tokenize(text) -> (tokens, errors)."""
    return Lexer(source).tokenize()
