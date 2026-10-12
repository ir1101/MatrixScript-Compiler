"""Language guide page - the grammar, the tokens, the rules and the errors."""

import streamlit as st

from matrixscript import compile_source
from ui.components import esc, page_header, section, show, spacer
from ui.state import open_in_playground
from ui.visuals import shape_html

GRAMMAR = [
    ("program", [("me", "→ "), ("nt", "statement"), ("me", "*")]),
    ("statement", [("me", "→ "), ("nt", "declaration"), ("me", " | "), ("nt", "assignment"), ("me", " | "), ("nt", "print")]),
    ("declaration", [("me", "→ "), ("tm", "'matrix'"), ("nt", " ID "), ("tm", "'['"), ("nt", " NUMBER "), ("tm", "']' '['"),
                     ("nt", " NUMBER "), ("tm", "']'"), ("me", "\n                 [ "), ("tm", "'=' '{'"), ("nt", " NUMBER "),
                     ("me", "("), ("tm", "','"), ("nt", " NUMBER"), ("me", ")* "), ("tm", "'}'"), ("me", " ]")]),
    ("assignment", [("me", "→ "), ("nt", "ID "), ("tm", "'='"), ("nt", " expression")]),
    ("print", [("me", "→ "), ("tm", "'print'"), ("nt", " ID")]),
    ("expression", [("me", "→ "), ("nt", "term"), ("me", " ( "), ("tm", "'+'"), ("nt", " term"), ("me", " )*")]),
    ("term", [("me", "→ "), ("nt", "ID"), ("me", " ( "), ("tm", "'*'"), ("nt", " ID"), ("me", " )*")]),
]

TOKENS = [
    ("TOKEN_MATRIX", "k-kw", "matrix", "Keyword that starts a declaration"),
    ("TOKEN_PRINT", "k-kw", "print", "Keyword that shows a matrix"),
    ("TOKEN_ID", "k-id", "A, result, m_2", "A matrix name: letters, digits, _"),
    ("TOKEN_NUMBER", "k-num", "2, -3, 4.5", "Sizes and values"),
    ("TOKEN_PLUS", "k-op", "+", "Matrix addition"),
    ("TOKEN_STAR", "k-op", "*", "Matrix multiplication"),
    ("TOKEN_ASSIGN", "k-op", "=", "Assignment / start of values"),
    ("TOKEN_LBRACKET · RBRACKET", "k-punct", "[  ]", "Around each dimension"),
    ("TOKEN_LBRACE · RBRACE", "k-punct", "{  }", "Around the list of values"),
    ("TOKEN_COMMA", "k-punct", ",", "Between values"),
    ("TOKEN_EOF", "k-punct", "(end)", "Added by the lexer at the end"),
]

ERRORS = [
    ("Lexical", "An unknown character",
     "matrix A[2][2]\nmatrix C[2][2]\nC = A $ A\n"),
    ("Lexical", "A name that starts with a digit",
     "matrix 2A[2][2]\n"),
    ("Syntax", "A missing bracket",
     "matrix A[2 2]\n"),
    ("Syntax", "An operator with nothing after it",
     "matrix A[2][2]\nmatrix C[2][2]\nC = A +"),
    ("Semantic", "Adding matrices of different sizes",
     "matrix A[2][2]\nmatrix B[3][3]\nmatrix C[2][2]\nC = A + B\n"),
    ("Semantic", "Inner sizes that do not match",
     "matrix A[2][3]\nmatrix B[2][2]\nmatrix C[2][2]\nC = A * B\n"),
    ("Semantic", "A result that does not fit",
     "matrix A[2][3]\nmatrix B[3][2]\nmatrix C[3][3]\nC = A * B\n"),
    ("Semantic", "Using a name that was never declared",
     "matrix A[2][2]\nmatrix C[2][2]\nC = A + Q\n"),
    ("Semantic", "The wrong number of values",
     "matrix A[2][2] = {1, 2, 3}\n"),
]


def render():
    page_header("Language guide", 'Small language, <span class="grad">strict rules.</span>',
                "Everything MatrixScript understands fits on this page: three kinds of statement, two operators "
                "and two dimension rules.")

    # ---- statements ---------------------------------------------------------
    section("Statements", "One statement per line. A # starts a comment that runs to the end of the line.")
    statements = [
        ("Declare", "matrix A[2][3] = {1, 2, 3, 4, 5, 6}",
         "Creates a matrix with 2 rows and 3 columns. Values are optional and are written row by row; without them the matrix is all zeros. Sizes go from 1 to 10."),
        ("Assign", "C = A * B + D",
         "Computes the right-hand side and stores it in C. Only + and * exist, and * is done before +."),
        ("Print", "print C",
         "Shows the matrix in the Print Output tab."),
    ]
    show('<div class="grid-auto">' + "".join(
        f'<div class="card"><p class="label">{esc(name)}</p>'
        f'<div class="codewin" style="box-shadow:none;margin-bottom:.8rem"><pre>{esc(code)}</pre></div><p>{esc(text)}</p></div>'
        for name, code, text in statements) + "</div>")

    spacer()

    # ---- the two rules --------------------------------------------------------
    section("The two dimension rules", "These are what the semantic analyzer checks for every operator.")
    add_ok = (f'<div class="eq">{shape_html("A", 2, 2, "sym-a")}<span class="op">+</span>'
              f'{shape_html("B", 2, 2, "sym-b")}<span class="op">=</span>{shape_html("C", 2, 2, "sym-r")}</div>')
    mul_ok = (f'<div class="eq">{shape_html("A", 2, 3, "sym-a", hot="cols")}<span class="op">×</span>'
              f'{shape_html("B", 3, 2, "sym-b", hot="rows")}<span class="op">=</span>{shape_html("C", 2, 2, "sym-r")}</div>')
    show('<div class="rulebox">'
         f'<div class="card"><h3>Addition: same size</h3><p style="margin-bottom:1rem">A + B is allowed only when A and B '
         f'have the same rows <b>and</b> the same columns. The result has that size too.</p>{add_ok}</div>'
         f'<div class="card"><h3>Multiplication: inner sizes match</h3><p style="margin-bottom:1rem">A * B is allowed only when '
         f'the columns of A equal the rows of B. The result is A.rows × B.cols.</p>{mul_ok}</div>'
         "</div>")

    spacer()

    # ---- grammar + tokens ---------------------------------------------------
    g_col, t_col = st.columns([1, 1], gap="large")
    with g_col:
        section("Grammar", "Each rule is one method in parser.py.")
        lines = []
        for name, parts in GRAMMAR:
            body = "".join(f'<span class="{cls}">{esc(text)}</span>' for cls, text in parts)
            lines.append(f'<span class="nt">{name.ljust(12)}</span>{body}')
        show('<div class="card"><pre class="gram">' + "\n".join(lines) + "</pre></div>")
    with t_col:
        section("Tokens", "Every label the lexer can produce.")
        rows = "".join(f'<tr><td><span class="badge {css}">{esc(name)}</span></td><td class="mono">{esc(example)}</td>'
                       f'<td>{esc(meaning)}</td></tr>' for name, css, example, meaning in TOKENS)
        show('<div class="scroll" style="max-height:none"><table class="t"><tr><th>Token</th><th>Example</th>'
             f'<th>Meaning</th></tr>{rows}</table></div>')

    spacer()

    # ---- errors -------------------------------------------------------------
    section("Error gallery", "One example of every kind of error. Open any of them in the playground to see the full report.")
    cols = st.columns(3, gap="medium")
    for i, (kind, title, program) in enumerate(ERRORS):
        result = compile_source(program)
        err = result.errors[0]
        with cols[i % 3]:
            tone = {"Lexical": "var(--k-kw)", "Syntax": "var(--warn)", "Semantic": "var(--err)"}[kind]
            show(f'<div class="tcard" style="min-height:14.2rem"><div class="top"><span class="pill" style="color:{tone};'
                 f'background:color-mix(in srgb,{tone} 14%,transparent)">{kind.upper()}</span>'
                 f'<span class="id">line {err.line}</span></div><h3>{esc(title)}</h3>'
                 f'<pre>{esc(program.rstrip())}</pre><p>{esc(err.message)}</p></div>')
            if st.button("Open in playground", key=f"err{i}", icon=":material/open_in_new:", use_container_width=True):
                open_in_playground(program)
            show('<div style="height:.6rem"></div>')
