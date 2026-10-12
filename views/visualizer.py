"""Visualizer page - walk through the compiler one phase at a time, with pictures."""

import streamlit as st

from matrixscript import PHASES, compile_source
from matrixscript.compiler import STATUS_OK
from ui.components import code_html, empty_state, error_cards, matrix_cards, page_header, show, tac_listing
from ui.state import EXAMPLES, read_example
from ui.visuals import ast_gallery, check_card, symbol_shapes, tac_map, token_legend, token_stream

STEPS = ["Source", "Tokens", "Syntax tree", "Dimension check", "Three-address code", "Output"]

# What to say for each step: (headline, explanation, input, output, viva line, phase that must have passed)
EXPLAIN = {
    "Source": ("The program as text",
               "To the computer, the program starts as one long string of characters. Nothing is understood yet.",
               "a .ms file", "a string of characters",
               "Compilation starts from plain text; every later phase adds more structure.", None),
    "Tokens": ("Phase 1 · Lexer",
               "The lexer reads one character at a time and groups characters into tokens: keywords, names, "
               "numbers, operators and brackets. Spaces and # comments are thrown away. A character that fits "
               "no token, like $, is a lexical error.",
               "characters", "a list of tokens",
               "I convert text into labelled tokens, like turning the word matrix into TOKEN_MATRIX.", PHASES[0]),
    "Syntax tree": ("Phase 2 · Parser",
                    "The parser checks that the tokens follow the grammar and builds a tree for each statement. "
                    "Because * is handled one level deeper than +, it ends up lower in the tree and is done first. "
                    "The small numbers under the nodes are the sizes the semantic phase writes onto the tree.",
                    "tokens", "a syntax tree (AST)",
                    "The parser only checks the shape of a statement, not whether the sizes make sense.", PHASES[1]),
    "Dimension check": ("Phase 3 · Semantic analyzer",
                        "Every declaration goes into the symbol table with its rows and columns. Then each operator "
                        "is checked: + needs two matrices of the same size, and * needs the columns of the left "
                        "matrix to equal the rows of the right one. Finally the result must fit the target.",
                        "the syntax tree", "a symbol table + checked tree",
                        "This is where a mistake like a 2×3 times a 2×2 is caught, before any code exists.", PHASES[1]),
    "Three-address code": ("Phase 4 · TAC generator",
                           "Each statement is rewritten as small steps that do one operation each. Results in "
                           "between are stored in temporaries T1, T2 and so on, which the compiler invents.",
                           "the checked tree", "three-address code",
                           "D = A * B + C becomes T1 = A * B, T2 = T1 + C, D = T2.", PHASES[3]),
    "Output": ("Running the TAC",
               "A tiny interpreter executes the three-address code line by line. This is not a compiler "
               "phase; it proves the generated code is correct.",
               "three-address code", "printed matrices",
               "Each print statement in the program shows up here as a matrix.", PHASES[3]),
}


def _step_nav(delta):
    i = STEPS.index(st.session_state.viz_step or STEPS[0]) + delta
    st.session_state.viz_step = STEPS[max(0, min(len(STEPS) - 1, i))]


def _never_empty(key, fallback):
    """Clicking the selected option again would clear it; put it back instead."""
    remember = f"{key}_last"
    if st.session_state.get(key) is None:
        st.session_state[key] = st.session_state.get(remember, fallback)
    else:
        st.session_state[remember] = st.session_state[key]


def render():
    page_header("Step by step", 'Watch the compiler <span class="grad">think.</span>',
                "Choose a program, then step through the phases. Each step shows what goes in, what comes out, "
                "and a sentence you can use in the viva.")

    options = ["Current playground program"] + [label for label, _, _ in EXAMPLES]
    if "viz_program" not in st.session_state:
        st.session_state.viz_program = options[0]
    choice = st.pills("Program", options, key="viz_program", label_visibility="collapsed",
                      on_change=_never_empty, args=("viz_program", options[0])) or options[0]
    if choice == options[0]:
        source = st.session_state.program
    else:
        source = read_example(next(f for label, f, _ in EXAMPLES if label == choice))

    if not source.strip():
        empty_state("The playground program is empty", "Pick one of the examples above instead.")
        return

    result = compile_source(source)

    if "viz_step" not in st.session_state:
        st.session_state.viz_step = STEPS[0]
    show('<div style="height:.4rem"></div>')
    nav_l, nav_mid, nav_r = st.columns([1, 8, 1], vertical_alignment="center")
    with nav_mid:
        st.segmented_control("Step", STEPS, key="viz_step", label_visibility="collapsed",
                             format_func=lambda s: f"{STEPS.index(s) + 1}. {s}",
                             on_change=_never_empty, args=("viz_step", STEPS[0]))
    nav_l.button("Back", icon=":material/arrow_back:", on_click=_step_nav, args=(-1,), use_container_width=True,
                 disabled=st.session_state.viz_step == STEPS[0])
    nav_r.button("Next", icon=":material/arrow_forward:", on_click=_step_nav, args=(1,), use_container_width=True,
                 disabled=st.session_state.viz_step == STEPS[-1])
    step = st.session_state.viz_step or STEPS[0]

    show('<div style="height:1rem"></div>')
    left, right = st.columns([1, 2.1], gap="large")
    headline, text, given, made, say, needs = EXPLAIN[step]
    with left:
        show(f'<div class="explain"><div class="step">Step {STEPS.index(step) + 1} of {len(STEPS)}</div>'
             f'<h3>{headline}</h3><p>{text}</p>'
             f'<div class="io"><span>Input</span><b>{given}</b><span>Output</span><b>{made}</b></div>'
             f'<div class="say"><b>Say this</b>{say}</div></div>')

    with right:
        reached = needs is None or result.status.get(needs) == STATUS_OK
        if step == "Source":
            first_error = result.errors[0].line if result.errors else None
            show(f'<div class="codewin"><div class="bar"><i></i><i></i><i></i><span>program.ms</span></div>'
                 f'{code_html(source, highlight_line=first_error)}</div>')
            if result.errors:
                show(f'<p class="rule" style="margin-top:.8rem">The highlighted line will fail in the '
                     f'<b>{result.failed_phase}</b>. Step forward to see why.</p>')
        elif step == "Tokens":
            show(token_stream(result.tokens, result.errors) + token_legend(result.tokens))
            if not reached:
                show('<div style="height:1rem"></div>')
                error_cards(result.errors, source)
        elif not reached:
            show(f'<div class="empty"><b>This step was never reached</b>The {result.failed_phase} stopped the '
                 'compiler first. Here is the error it reported:</div><div style="height:1rem"></div>')
            error_cards(result.errors, source)
        elif step == "Syntax tree":
            show(ast_gallery(result.statements, result.symbols))
        elif step == "Dimension check":
            _dimension_step(result, source)
        elif step == "Three-address code":
            show('<p class="label">Where each instruction comes from</p>' + tac_map(source, result.tac)
                 + '<div style="height:1rem"></div><p class="label">Final listing</p>' + tac_listing(result))
        elif step == "Output":
            if result.output:
                show(matrix_cards(result.output))
            else:
                empty_state("This program prints nothing", "Add a print statement to see a matrix here.")


def _dimension_step(result, source):
    lines = source.splitlines()
    if result.symbols:
        show('<p class="label">Symbol table</p>' + symbol_shapes(result.symbols) + '<div style="height:1.2rem"></div>')
    drawn = [c for c in result.checks if c.detail]
    if not drawn:
        show('<p class="rule">This program has no assignments, so there are no operators to check. '
             'Only the declarations were checked.</p>')
    else:
        show('<p class="label">Operator checks, in the order the analyzer did them</p>')
        for c in drawn:
            src = lines[c.line - 1].strip() if 1 <= c.line <= len(lines) else ""
            show(check_card(c, src))
    if result.errors:
        show('<div style="height:.4rem"></div>')
        error_cards(result.errors, source)
