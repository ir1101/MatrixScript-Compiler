"""
compiler.py - The pipeline: runs the phases one after another.

    source text
        |  Lexer      -> tokens
        |  Parser     -> AST  (list of statements)
        |  Semantic   -> symbol table + dimension checks
        |  TAC        -> three-address code
        v  (run)      -> print output

The pipeline STOPS at the first phase that reports errors; the phases after
it are marked "skipped". Every phase's result is kept so the GUI can show it.
"""

from dataclasses import dataclass, field

from .errors import PHASE_LEXER, PHASE_PARSER, PHASE_SEMANTIC, PHASE_TAC
from .executor import run_tac
from .lexer import tokenize
from .parser import parse
from .semantic import analyze
from .tac import generate_tac

# Order of the phases, as shown in the GUI pipeline strip.
PHASES = [PHASE_LEXER, PHASE_PARSER, PHASE_SEMANTIC, PHASE_TAC]

STATUS_OK = "ok"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"


@dataclass
class CompilationResult:
    source: str
    tokens: list = field(default_factory=list)
    statements: list = field(default_factory=list)   # the AST
    symbols: dict = field(default_factory=dict)      # the symbol table
    checks: list = field(default_factory=list)       # semantic check log
    tac: list = field(default_factory=list)
    output: list = field(default_factory=list)       # PrintResult objects
    errors: list = field(default_factory=list)
    status: dict = field(default_factory=dict)       # phase name -> ok/failed/skipped

    @property
    def success(self):
        return not self.errors

    @property
    def failed_phase(self):
        for phase in PHASES:
            if self.status.get(phase) == STATUS_FAILED:
                return phase
        return None


def compile_source(source):
    """Run the whole pipeline on a MatrixScript program."""
    result = CompilationResult(source=source)
    result.status = {phase: STATUS_SKIPPED for phase in PHASES}

    # Phase 1 - Lexer
    result.tokens, errors = tokenize(source)
    if errors:
        result.errors = errors
        result.status[PHASE_LEXER] = STATUS_FAILED
        return result
    result.status[PHASE_LEXER] = STATUS_OK

    # Phase 2 - Parser
    result.statements, errors = parse(result.tokens)
    if errors:
        result.errors = errors
        result.status[PHASE_PARSER] = STATUS_FAILED
        return result
    result.status[PHASE_PARSER] = STATUS_OK

    # Phase 3 - Semantic analysis (dimension checks)
    result.symbols, result.checks, errors = analyze(result.statements)
    if errors:
        result.errors = errors
        result.status[PHASE_SEMANTIC] = STATUS_FAILED
        return result
    result.status[PHASE_SEMANTIC] = STATUS_OK

    # Phase 4 - Three-address code, then run it to produce the print output
    result.tac = generate_tac(result.statements)
    result.status[PHASE_TAC] = STATUS_OK
    result.output = run_tac(result.tac)
    return result
