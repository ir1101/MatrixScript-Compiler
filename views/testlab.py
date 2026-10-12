"""Test lab page - run the demo test cases (and the full unit-test suite) live."""

import io
import os
import unittest

import streamlit as st

from matrixscript import compile_source
from matrixscript.errors import PHASE_LEXER, PHASE_SEMANTIC
from ui.components import esc, page_header, section, show, spacer
from ui.state import ROOT, open_in_playground, read_example

# id, title, file, what it shows, expected phase that fails (None = success), expected line, expected output
CASES = [
    ("T1", "Valid declaration & print", "test1_valid_declaration_print.ms",
     "The smallest complete program.", None, None, [[1, 2], [3, 4]]),
    ("T2", "Valid matrix addition", "test2_valid_addition.ms",
     "Two 2×2 matrices added; TAC uses a temporary.", None, None, [[6, 8], [10, 12]]),
    ("T3", "Dimension mismatch", "test3_dimension_mismatch.ms",
     "A 2×3 times a 2×2 must be rejected.", PHASE_SEMANTIC, 5, None),
    ("T4", "Lexical error", "test4_lexical_error.ms",
     "A $ sign is not part of the language.", PHASE_LEXER, 5, None),
    ("B1", "Valid multiplication", "bonus_valid_multiplication.ms",
     "2×3 times 3×2 gives a 2×2.", None, None, [[58, 64], [139, 154]]),
    ("B2", "Chained expression", "bonus_chained_expression.ms",
     "Two operations in one line make two temporaries.", None, None, [[12, 11], [14, 13]]),
]


def run_case(case):
    """Compile one test program and compare it with what we expect."""
    _, _, filename, _, fail_phase, fail_line, output = case
    source = read_example(filename)
    result = compile_source(source)
    if fail_phase is None:
        expected = f"Success, prints {output}"
        actual_output = result.output[0].matrix if result.output else None
        passed = result.success and actual_output == output
        actual = f"Success, prints {actual_output}" if result.success else \
            f"{result.errors[0].kind()} at line {result.errors[0].line}"
    else:
        expected = f"{fail_phase} error at line {fail_line}"
        passed = (not result.success and result.failed_phase == fail_phase and result.errors[0].line == fail_line)
        actual = (f"{result.failed_phase} error at line {result.errors[0].line}" if result.errors else "Success")
    return source, passed, expected, actual


def run_unit_tests():
    suite = unittest.defaultTestLoader.discover(os.path.join(ROOT, "tests"))
    stream = io.StringIO()
    outcome = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return outcome.testsRun, len(outcome.failures) + len(outcome.errors), stream.getvalue()


def render():
    page_header("Test lab", 'Proof that it <span class="grad">works.</span>',
                "The viva test cases run live every time this page opens. Each card compares what the compiler "
                "did with what it should do.")

    results = [(case, *run_case(case)) for case in CASES]
    passed = sum(1 for r in results if r[2])
    pct = int(100 * passed / len(results))
    show(f'<div class="card"><div class="scorebar"><div><b class="big grad">{passed}/{len(results)}</b>'
         f'<div class="muted" style="font-size:.85rem">demo cases passing</div></div>'
         f'<div class="meter" role="progressbar" aria-valuenow="{pct}" aria-valuemin="0" aria-valuemax="100">'
         f'<i style="width:{pct}%"></i></div></div></div>')

    spacer()
    section("Demo cases", "T1 to T4 are the four cases for the viva; B1 and B2 are extras.")
    cols = st.columns(3, gap="medium")
    for i, (case, source, ok, expected, actual) in enumerate(results):
        case_id, title, _, about = case[:4]
        pill = '<span class="pill pass">✓ PASS</span>' if ok else '<span class="pill fail">✕ FAIL</span>'
        with cols[i % 3]:
            show(f'<div class="tcard" style="min-height:24.5rem"><div class="top"><span class="id">{case_id}</span>{pill}</div>'
                 f'<h3>{esc(title)}</h3><p>{esc(about)}</p><pre>{esc(source.rstrip())}</pre>'
                 f'<div class="ex"><span>Expected</span><b>{esc(expected)}</b><span>Actual</span><b>{esc(actual)}</b></div></div>')
            if st.button("Open in playground", key=f"case{i}", icon=":material/open_in_new:", use_container_width=True):
                open_in_playground(source)
            show('<div style="height:.6rem"></div>')

    spacer()
    section("Full unit-test suite", "The tests/ folder checks the lexer, parser, semantic rules, TAC and error recovery.")
    if st.button("Run all unit tests", type="primary", icon=":material/science:"):
        st.session_state.unit_run = run_unit_tests()
    if "unit_run" in st.session_state:
        total, failed, log = st.session_state.unit_run
        good = total - failed
        tone = "ok" if failed == 0 else "err"
        title = f"All {total} tests passed" if failed == 0 else f"{failed} of {total} tests failed"
        icon = "✓" if failed == 0 else "✕"
        show(f'<div class="banner {tone}" style="margin-top:1rem"><div class="icon">{icon}</div><div>'
             f'<p class="t">{title}</p><p class="s">{good} passed · {failed} failed</p></div></div>')
        with st.expander("Show the test log", icon=":material/terminal:"):
            st.code(log, language="text")
