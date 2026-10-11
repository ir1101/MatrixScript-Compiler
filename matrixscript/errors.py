"""
errors.py - One shared error type used by every compiler phase.

Every phase (lexer, parser, semantic analyzer) reports problems the same way:
a MatrixScriptError that says
    * WHICH phase found the problem          -> phase
    * WHERE it is (line and column)          -> line, column
    * WHAT is wrong, in plain English        -> message
    * HOW to fix it                          -> hint
"""

# Names of the phases, so we never mistype a string elsewhere.
PHASE_LEXER = "Lexer"
PHASE_PARSER = "Parser"
PHASE_SEMANTIC = "Semantic Analyzer"
PHASE_TAC = "TAC Generator"


class MatrixScriptError(Exception):
    """A friendly compile error. Phases either raise it or collect it in a list."""

    def __init__(self, phase, line, column, message, hint=""):
        super().__init__(message)
        self.phase = phase      # e.g. "Semantic Analyzer"
        self.line = line        # 1-based line number in the source code
        self.column = column    # 1-based column (0 means "whole line")
        self.message = message  # what went wrong
        self.hint = hint        # how to fix it

    def kind(self):
        """Short label used in the GUI, e.g. 'Lexical Error'."""
        return {
            PHASE_LEXER: "Lexical Error",
            PHASE_PARSER: "Syntax Error",
            PHASE_SEMANTIC: "Semantic Error",
        }.get(self.phase, "Error")

    def __str__(self):
        return f"{self.kind()} at line {self.line}: {self.message}"
