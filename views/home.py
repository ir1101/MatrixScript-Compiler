"""Home page - what MatrixScript is, in one screen."""

import streamlit as st

from matrixscript import compile_source
from matrixscript.lexer import KEYWORDS, SINGLE_CHAR_TOKENS
from ui.components import code_html, esc, section, show, spacer, svg_img
from ui.state import go, read_example
from ui.theme import palette, theme_toggle

ICON_SHIELD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round"><path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg>')
ICON_CHAT = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
             'stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M9 11h6M9 14h4"/></svg>')
ICON_EYE = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>')

PHASE_CARDS = [
    ("Lexer", "Cuts the text into labelled tokens and rejects unknown characters.", "C = A * B", "ID ASSIGN ID STAR ID"),
    ("Parser", "Checks the grammar and builds a syntax tree for every statement.", "tokens", "= ( C , * ( A , B ) )"),
    ("Semantic check", "Looks up every size in the symbol table and applies the matrix rules.", "A 2×3 · B 3×2", "3 = 3  → 2×2"),
    ("TAC generator", "Rewrites each statement as simple steps with one operation each.", "tree", "T1 = A * B · C = T1"),
]


@st.cache_data
def count_unit_tests():
    import os
    import unittest
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    suite = unittest.defaultTestLoader.discover(os.path.join(here, "tests"))
    return suite.countTestCases()


def render():
    _, toggle_col = st.columns([6, 1])
    with toggle_col:
        theme_toggle()

    # ---- hero ----------------------------------------------------------------
    left, right = st.columns([1.05, 1], gap="large", vertical_alignment="center")
    with left:
        show('<div class="eyebrow"><span class="pulse"></span>Compiler Design · Semester Project</div>'
             '<div class="display" role="heading" aria-level="1">Matrix maths,<br><span class="grad">checked before<br>it runs.</span></div>'
             '<p class="lead">MatrixScript is a tiny language for matrix arithmetic. Its four-phase compiler catches '
             'dimension mistakes at compile time, explains them in plain English, and shows every phase on screen.</p>')
        # A horizontal row that wraps, so the buttons never get squeezed and cut off.
        with st.container(horizontal=True, wrap=True, gap="small"):
            if st.button("Open the playground", type="primary", icon=":material/play_arrow:", width="content"):
                go("playground")
            if st.button("See it step by step", icon=":material/account_tree:", width="content"):
                go("visualizer")

    with right:
        source = read_example("test3_dimension_mismatch.ms")
        body = source.split("\n", 1)[1]                      # drop the long first comment
        source = "# A is 2x3, B is 2x2: should this compile?\n" + body
        result = compile_source(source)
        err = result.errors[0]
        show(f'<div class="codewin"><div class="bar"><i></i><i></i><i></i><span>dimension_error.ms</span></div>'
             f'{code_html(source, highlight_line=err.line)}'
             f'<div class="foot"><span><b>Line {err.line} · {esc(err.kind())}</b><br>{esc(err.message)}</span></div></div>')

    spacer()

    # ---- pipeline ------------------------------------------------------------
    section("Four phases, one straight line",
            "Each phase hands its output to the next. The first phase that finds a mistake stops the line.")
    cards = "".join(
        f'<div class="phase"><div class="num">{i}</div><h3>{esc(name)}</h3><p>{esc(text)}</p>'
        f'<div class="io">{esc(src)}<br><b>→ {esc(out)}</b></div></div>'
        for i, (name, text, src, out) in enumerate(PHASE_CARDS, start=1))
    show(f'<div class="phase-row">{cards}</div>')

    spacer()

    # ---- why -----------------------------------------------------------------
    section("Why a dedicated matrix language?")
    colors = palette()
    features = [
        ("var(--ok)", ICON_SHIELD.format(color=colors["ok"]), "Mistakes found before running",
         "Python or MATLAB only fail when the bad line runs. MatrixScript knows every size up front, "
         "so a 2×3 times 2×2 never gets past the compiler."),
        ("var(--warn)", ICON_CHAT.format(color=colors["warn"]), "Errors a person can read",
         "Each error names the phase, the line and the column, says what is wrong, and suggests a fix."),
        ("var(--c-tokens)", ICON_EYE.format(color=colors["c-tokens"]), "Every phase is visible",
         "Tokens, syntax trees, dimension checks and three-address code are drawn on screen, "
         "so each idea from the course can be pointed at."),
    ]
    show('<div class="grid-auto">' + "".join(
        f'<div class="card feature" style="--fc:{color}"><div class="ico">{svg_img(icon, "")}</div><h3>{esc(title)}</h3><p>{esc(text)}</p></div>'
        for color, icon, title, text in features) + "</div>")

    spacer()

    # ---- numbers -------------------------------------------------------------
    token_types = len(set(KEYWORDS.values())) + len(set(SINGLE_CHAR_TOKENS.values())) + 3   # + ID, NUMBER, EOF
    stats = [("4", "compiler phases"), (str(token_types), "token types"),
             ("2", "dimension rules"), (str(count_unit_tests()), "automated tests")]
    show('<div class="stats">' + "".join(
        f'<div><b class="grad">{n}</b><span>{esc(label)}</span></div>' for n, label in stats) + "</div>")

    show('<div class="footer"><span>MatrixScript v1.0 · Lexer → Parser → Semantic → TAC</span>'
         '<span>Built with Python and Streamlit</span></div>')
