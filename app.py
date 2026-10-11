"""
app.py - The MatrixScript web dashboard (Streamlit).

Run it with:      streamlit run app.py

This file only DRAWS things. All the real compiler work happens in the
`matrixscript` package; here we call compile_source() once and then show each
phase's result in a different tab.
"""

import html
import os
import re

import streamlit as st

from matrixscript import PHASES, compile_source
from matrixscript.compiler import STATUS_OK, STATUS_SKIPPED
from matrixscript.executor import clean_number
from matrixscript.lexer import (
    TOKEN_ASSIGN, TOKEN_COMMA, TOKEN_EOF, TOKEN_ID, TOKEN_LBRACE, TOKEN_LBRACKET,
    TOKEN_MATRIX, TOKEN_NUMBER, TOKEN_PLUS, TOKEN_PRINT, TOKEN_RBRACE,
    TOKEN_RBRACKET, TOKEN_STAR,
)

st.set_page_config(page_title="MatrixScript Compiler", page_icon="🧮", layout="wide")

# ---------------------------------------------------------------------------
# Example programs (loaded from the examples/ folder)
# ---------------------------------------------------------------------------
EXAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")
EXAMPLES = [
    ("1 · Declare & print", "test1_valid_declaration_print.ms"),
    ("2 · Matrix addition", "test2_valid_addition.ms"),
    ("3 · Dimension error", "test3_dimension_mismatch.ms"),
    ("4 · Lexical error", "test4_lexical_error.ms"),
    ("★ Multiplication", "bonus_valid_multiplication.ms"),
    ("★ Chained TAC", "bonus_chained_expression.ms"),
]


def read_example(filename):
    with open(os.path.join(EXAMPLE_DIR, filename), encoding="utf-8") as f:
        return f.read()


def load_example(filename):
    """Button callback: put an example into the editor."""
    st.session_state.source = read_example(filename)


# ---------------------------------------------------------------------------
# Theme (dark / light) - plain CSS variables, swapped by the toggle
# ---------------------------------------------------------------------------
DARK = """
--bg:#0d1117; --panel:#161b22; --panel2:#1c232d; --border:#2d3646; --text:#e6edf3;
--muted:#9aa7b5; --accent:#58a6ff; --ok:#3fb950; --err:#ff7b72;
--c-tokens:#58a6ff; --c-sem:#e3b341; --c-tac:#bc8cff; --c-out:#39d0c0;
--k-kw:#ff7b72; --k-id:#79c0ff; --k-num:#e3b341; --k-op:#d2a8ff; --k-punct:#9aa7b5;
"""
LIGHT = """
--bg:#f4f6f9; --panel:#ffffff; --panel2:#eef1f5; --border:#d0d7de; --text:#1f2328;
--muted:#59636e; --accent:#0969da; --ok:#1a7f37; --err:#cf222e;
--c-tokens:#0969da; --c-sem:#9a6700; --c-tac:#8250df; --c-out:#0a7c72;
--k-kw:#cf222e; --k-id:#0550ae; --k-num:#953800; --k-op:#8250df; --k-punct:#6e7781;
"""

STYLE = """
<style>
:root { %s }
.stApp { background: var(--bg); color: var(--text); }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1500px; padding-top: 2.2rem; padding-bottom: 3rem; }
.stApp p, .stApp label, .stApp li, .stApp summary, .stApp [data-testid="stWidgetLabel"] *,
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stExpander"] * { color: var(--text); }

/* ---- header ---- */
.hero .h1 { display: block; font-size: 1.9rem; font-weight: 700; line-height: 1.15; margin: 0; color: var(--text);
           letter-spacing: -0.01em; padding: 0; }
.hero .h1 span { color: var(--accent); }
.hero p { margin: .35rem 0 0 0; color: var(--muted) !important; font-size: .95rem; }

/* ---- pipeline strip ---- */
.pipe { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem; margin: 1.1rem 0 1.3rem 0; }
.chip { display: inline-flex; align-items: center; gap: .45rem; padding: .45rem .8rem; border-radius: 999px;
        font-size: .82rem; font-weight: 600; border: 1px solid var(--border); background: var(--panel);
        color: var(--muted); transition: background .15s, border-color .15s; }
.chip .dot { width: .6rem; height: .6rem; border-radius: 50%%; background: var(--border); }
.chip.ok { color: var(--ok); border-color: var(--ok); background: color-mix(in srgb, var(--ok) 12%%, var(--panel)); }
.chip.ok .dot { background: var(--ok); }
.chip.failed { color: var(--err); border-color: var(--err); background: color-mix(in srgb, var(--err) 12%%, var(--panel)); }
.chip.failed .dot { background: var(--err); }
.arrow { color: var(--muted); font-size: .9rem; }

/* ---- panel headings ---- */
.panel-title { font-size: .75rem; font-weight: 600; letter-spacing: .09em; text-transform: uppercase;
               color: var(--muted); margin: 0 0 .5rem 0; }

/* ---- editor ---- */
.stTextArea textarea { font-family: ui-monospace, "Cascadia Code", Consolas, monospace !important;
    font-size: .92rem !important; line-height: 1.55 !important; background: var(--panel) !important;
    color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }
.stTextArea textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 1px var(--accent) !important; }
.stButton > button, .stDownloadButton > button { border-radius: 8px; font-weight: 600; font-size: .85rem;
    background: var(--panel); color: var(--text); border: 1px solid var(--border); min-height: 2.5rem; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--accent); color: var(--accent); }
.stButton > button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.stButton > button[kind="primary"] { background: var(--accent); border-color: var(--accent); color: #fff; }
.stButton > button[kind="primary"]:hover { filter: brightness(1.1); color: #fff; }
.stButton > button p { color: inherit !important; }

/* ---- theme toggle: keep the switch visible in both themes ---- */
label:has(input[role="switch"]) > div:nth-of-type(1) { border: 1px solid var(--muted); }
label:has(input[role="switch"]:not(:checked)) > div:nth-of-type(1) { background: var(--panel2) !important; }
label:has(input[role="switch"]:not(:checked)) > div:nth-of-type(1) > div { background: var(--muted) !important; }

/* ---- banners ---- */
.banner { border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 1rem; border: 1px solid; display: flex;
          gap: .9rem; align-items: flex-start; }
.banner .icon { font-size: 1.6rem; line-height: 1; font-weight: 700; }
.banner .t { font-size: 1.1rem; font-weight: 700; margin: 0; }
.banner .s { margin: .2rem 0 0 0; font-size: .88rem; opacity: .9; }
.banner.ok { color: var(--ok); border-color: var(--ok); background: color-mix(in srgb, var(--ok) 13%%, var(--panel)); }
.banner.err { color: var(--err); border-color: var(--err); background: color-mix(in srgb, var(--err) 12%%, var(--panel)); }
.banner.idle { color: var(--muted); border-color: var(--border); background: var(--panel); }
.stat-row { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .7rem; }
.stat { font-size: .78rem; font-weight: 600; padding: .2rem .6rem; border-radius: 6px;
        background: color-mix(in srgb, var(--ok) 16%%, transparent); }

.errcard { border: 1px solid var(--err); border-left-width: 5px; border-radius: 10px; background: var(--panel);
           padding: .9rem 1.1rem; margin-bottom: .8rem; }
.errcard .where { font-size: .75rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--err); }
.errcard .msg { font-size: 1.02rem; font-weight: 600; margin: .3rem 0 .6rem 0; color: var(--text); }
.errcard pre { margin: 0 0 .6rem 0; padding: .6rem .8rem; border-radius: 8px; background: var(--panel2);
               font-family: ui-monospace, Consolas, monospace; font-size: .86rem; overflow-x: auto; color: var(--text); }
.errcard pre .caret { color: var(--err); font-weight: 700; }
.errcard .hint { font-size: .88rem; color: var(--muted); }
.errcard .hint b { color: var(--text); }

/* ---- tabs (each one has its own colour) ---- */
.stTabs [role="tablist"] { gap: .4rem; border-bottom: 1px solid var(--border); }
.stTabs [role="tab"] { height: 2.7rem; padding: 0 1rem; border-radius: 8px 8px 0 0; background: transparent;
                       border-bottom: 3px solid transparent; cursor: pointer; }
.stTabs [role="tab"] p { font-size: .88rem; font-weight: 600; color: var(--tc) !important; opacity: .75; }
.stTabs [role="tab"]:nth-child(1) { --tc: var(--c-tokens); }
.stTabs [role="tab"]:nth-child(2) { --tc: var(--c-sem); }
.stTabs [role="tab"]:nth-child(3) { --tc: var(--c-tac); }
.stTabs [role="tab"]:nth-child(4) { --tc: var(--c-out); }
.stTabs [role="tab"]:hover p { opacity: 1; }
.stTabs [role="tab"][aria-selected="true"] { background: color-mix(in srgb, var(--tc) 14%%, transparent);
                                            border-bottom-color: var(--tc); }
.stTabs [role="tab"][aria-selected="true"] p { opacity: 1; }
.stTabs [role="tab"]:focus-visible { outline: 2px solid var(--tc); outline-offset: -2px; }
.stTabs .react-aria-SelectionIndicator, .stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ---- generic cards / tables ---- */
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: .9rem 1rem; margin-bottom: .8rem; }
.scroll { max-height: 430px; overflow: auto; border: 1px solid var(--border); border-radius: 10px; background: var(--panel); }
table.t { width: 100%%; border-collapse: collapse; font-size: .85rem; }
table.t th { position: sticky; top: 0; background: var(--panel2); color: var(--muted); text-align: left; font-size: .72rem;
             letter-spacing: .07em; text-transform: uppercase; padding: .5rem .7rem; border-bottom: 1px solid var(--border); }
table.t td { padding: .38rem .7rem; border-bottom: 1px solid var(--border); font-variant-numeric: tabular-nums; color: var(--text); }
table.t tr:last-child td { border-bottom: none; }
table.t tr.bad td { background: color-mix(in srgb, var(--err) 12%%, transparent); color: var(--err); font-weight: 600; }
table.t tr.dim td { color: var(--muted); }
.mono { font-family: ui-monospace, "Cascadia Code", Consolas, monospace; }
.badge { display: inline-block; padding: .08rem .5rem; border-radius: 5px; font-size: .74rem; font-weight: 600;
         font-family: ui-monospace, Consolas, monospace; background: color-mix(in srgb, currentColor 14%%, transparent); }
.k-kw { color: var(--k-kw); } .k-id { color: var(--k-id); } .k-num { color: var(--k-num); }
.k-op { color: var(--k-op); } .k-punct { color: var(--k-punct); }
.pass { color: var(--ok); font-weight: 700; } .fail { color: var(--err); font-weight: 700; }

.sym { display: inline-flex; align-items: baseline; gap: .5rem; padding: .35rem .75rem; margin: 0 .5rem .5rem 0;
       border-radius: 8px; background: var(--panel2); border: 1px solid var(--border); }
.sym b { font-size: 1.05rem; color: var(--c-sem); } .sym span { font-size: .82rem; color: var(--muted); }

.rule { font-size: .85rem; color: var(--muted); margin: 0 0 .8rem 0; }
.rule code { color: var(--c-sem); background: var(--panel2); padding: .05rem .35rem; border-radius: 4px; }

/* ---- TAC ---- */
.tac { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: .6rem 0; }
.tac-line { display: flex; gap: 1rem; padding: .18rem 1rem; font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
            font-size: .92rem; color: var(--text); }
.tac-line:hover { background: var(--panel2); }
.tac-line .ln { color: var(--muted); width: 1.6rem; text-align: right; user-select: none; }
.tac-temp { color: var(--c-tac); font-weight: 700; } .tac-kw { color: var(--k-kw); }

/* ---- printed matrices ---- */
.mx-card { display: inline-block; vertical-align: top; margin: 0 1rem 1rem 0; padding: .8rem 1.1rem 1rem 1.1rem;
           background: var(--panel); border: 1px solid var(--border); border-radius: 12px; }
.mx-head { display: flex; justify-content: space-between; gap: 1.5rem; margin-bottom: .6rem; }
.mx-head b { font-size: 1.05rem; color: var(--c-out); } .mx-head span { font-size: .78rem; color: var(--muted); }
table.mx { border-collapse: separate; border-spacing: .35rem .25rem; border-left: 3px solid var(--text);
           border-right: 3px solid var(--text); border-radius: 8px; }
table.mx td { min-width: 2.6rem; text-align: right; padding: .15rem .5rem; font-size: 1.15rem;
              font-family: ui-monospace, Consolas, monospace; font-variant-numeric: tabular-nums; color: var(--text); }

.empty { text-align: center; padding: 2.2rem 1rem; color: var(--muted); border: 1px dashed var(--border);
         border-radius: 10px; font-size: .92rem; }
.empty b { display: block; color: var(--text); font-size: 1rem; margin-bottom: .25rem; }

@media (max-width: 640px) { .hero .h1 { display: block; font-size: 1.5rem; } .block-container { padding-left: 1rem; padding-right: 1rem; } }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
"""


# ---------------------------------------------------------------------------
# Small HTML helpers (everything the user typed goes through html.escape)
# ---------------------------------------------------------------------------
def esc(value):
    return html.escape(str(value))


def show(markup):
    """Draw raw HTML. st.html skips the Markdown step, so * and newlines stay untouched."""
    st.html(markup)


def empty_state(title, text):
    show(f'<div class="empty"><b>{esc(title)}</b>{esc(text)}</div>')


def skipped_state(result, what):
    failed = result.failed_phase
    empty_state(f"{what} was skipped", f"The {failed} reported an error, so the compiler stopped before this step. "
                                       "Fix the error shown above and compile again.")


def dims(rows, cols):
    return f"{rows}x{cols}"


# ---------------------------------------------------------------------------
# Pipeline strip + banner
# ---------------------------------------------------------------------------
def render_pipeline(result):
    parts = []
    for phase in PHASES:
        state = result.status.get(phase, STATUS_SKIPPED) if result else "idle"
        css = {"ok": "ok", "failed": "failed"}.get(state, "")
        mark = {"ok": "✔", "failed": "✖"}.get(state, "")
        parts.append(f'<span class="chip {css}"><span class="dot"></span>{esc(phase)} {mark}</span>')
    show('<div class="pipe">' + '<span class="arrow">➜</span>'.join(parts) + "</div>")


def render_banner(result, source):
    if not source.strip():
        show('<div class="banner idle"><div class="icon">…</div><div><p class="t">Nothing to compile yet</p>'
             '<p class="s">Type a program on the left or pick an example.</p></div></div>')
        return

    if result.success:
        stats = [
            f"{len(result.tokens) - 1} tokens",
            f"{len(result.symbols)} matrices",
            f"{len(result.checks)} checks passed",
            f"{len(result.tac)} TAC instructions",
        ]
        chips = "".join(f'<span class="stat">{esc(s)}</span>' for s in stats)
        show('<div class="banner ok"><div class="icon">✔</div><div>'
             '<p class="t">SUCCESS — compilation finished with no errors</p>'
             f'<p class="s">All four phases passed.</p><div class="stat-row">{chips}</div></div></div>')
        return

    count = len(result.errors)
    noun = "error" if count == 1 else "errors"
    show('<div class="banner err"><div class="icon">✖</div><div>'
         f'<p class="t">FAILED — {count} {noun} found by the {esc(result.failed_phase)}</p>'
         '<p class="s">Nothing after this phase was run.</p></div></div>')

    lines = source.splitlines()
    for err in result.errors:
        snippet = ""
        if 1 <= err.line <= len(lines):
            number = str(err.line)
            code = f"{number} | {esc(lines[err.line - 1])}"
            caret = ""
            if err.column:
                caret = "\n" + " " * len(number) + " | " + " " * (err.column - 1) + '<span class="caret">^</span>'
            snippet = f"<pre>{code}{caret}</pre>"
        hint = f'<div class="hint"><b>How to fix:</b> {esc(err.hint)}</div>' if err.hint else ""
        show(f'<div class="errcard"><div class="where">Line {err.line} · {esc(err.kind())}</div>'
             f'<div class="msg">{esc(err.message)}</div>{snippet}{hint}</div>')


# ---------------------------------------------------------------------------
# Tab 1 - Tokens
# ---------------------------------------------------------------------------
TOKEN_STYLE = {
    TOKEN_MATRIX: "k-kw", TOKEN_PRINT: "k-kw", TOKEN_ID: "k-id", TOKEN_NUMBER: "k-num",
    TOKEN_PLUS: "k-op", TOKEN_STAR: "k-op", TOKEN_ASSIGN: "k-op",
    TOKEN_LBRACKET: "k-punct", TOKEN_RBRACKET: "k-punct", TOKEN_LBRACE: "k-punct",
    TOKEN_RBRACE: "k-punct", TOKEN_COMMA: "k-punct", TOKEN_EOF: "k-punct",
}


def render_tokens_tab(result):
    rows = []   # (line, column, html)
    for t in result.tokens:
        css = TOKEN_STYLE.get(t.type, "k-punct")
        dim = ' class="dim"' if t.type == TOKEN_EOF else ""
        lexeme = "(end of input)" if t.type == TOKEN_EOF else esc(t.lexeme)
        rows.append((t.line, t.column, 1, f'<tr{dim}><td>{t.line}:{t.column}</td>'
                     f'<td><span class="badge {css}">{esc(t.type)}</span></td><td class="mono">{lexeme}</td></tr>'))
    # Lexical errors are shown in red, at the position where they were found.
    for e in result.errors:
        if e.phase == "Lexer":
            rows.append((e.line, e.column, 0, f'<tr class="bad"><td>{e.line}:{e.column}</td>'
                         f'<td>✖ LEXICAL ERROR</td><td>{esc(e.message)}</td></tr>'))
    rows.sort(key=lambda r: (r[0], r[1], r[2]))

    body = "".join(r[3] for r in rows)
    show(f'<p class="rule">The lexer cut your text into <b>{len(result.tokens) - 1}</b> labelled tokens '
         '(reading left to right, line by line).</p>'
         f'<div class="scroll"><table class="t"><tr><th>Line:Col</th><th>Token type</th><th>Text</th></tr>{body}</table></div>')


# ---------------------------------------------------------------------------
# Tab 2 - Semantic check
# ---------------------------------------------------------------------------
def render_semantic_tab(result, source):
    if result.status[PHASES[2]] == STATUS_SKIPPED:
        skipped_state(result, "Semantic checking")
        return

    show('<p class="rule">Rules:&nbsp; <code>A + B</code> needs the <b>same size</b> &nbsp;·&nbsp; '
         '<code>A * B</code> needs <b>A.cols = B.rows</b> &nbsp;·&nbsp; '
         '<code>C = …</code> needs the result to <b>fit C</b>.</p>')

    if result.symbols:
        show('<div class="panel-title">Symbol table</div>' + "".join(
            f'<span class="sym"><b>{esc(s.name)}</b><span>{s.rows} rows × {s.cols} cols</span></span>'
            for s in result.symbols.values()))

    lines = source.splitlines()
    rows = []
    for c in result.checks:
        src = lines[c.line - 1].strip() if 1 <= c.line <= len(lines) else ""
        icon = '<span class="pass">✔</span>' if c.ok else '<span class="fail">✖</span>'
        css = "" if c.ok else ' class="bad"'
        rows.append(f'<tr{css}><td>{c.line}</td><td class="mono">{esc(src)}</td><td>{icon}</td><td>{esc(c.text)}</td></tr>')
    show('<div class="panel-title" style="margin-top:.4rem">Check log</div>'
         '<div class="scroll"><table class="t"><tr><th>Line</th><th>Statement</th><th></th><th>Check</th></tr>'
         + "".join(rows) + "</table></div>")


# ---------------------------------------------------------------------------
# Tab 3 - TAC
# ---------------------------------------------------------------------------
def colour_tac(text):
    text = esc(text)
    text = re.sub(r"\bT\d+\b", lambda m: f'<span class="tac-temp">{m.group(0)}</span>', text)
    return re.sub(r"^(declare|print)\b", lambda m: f'<span class="tac-kw">{m.group(0)}</span>', text)


def render_tac_tab(result):
    if result.status[PHASES[3]] != STATUS_OK:
        skipped_state(result, "Code generation")
        return

    listing = "".join(f'<div class="tac-line"><span class="ln">{n}</span><span>{colour_tac(str(ins))}</span></div>'
                      for n, ins in enumerate(result.tac, start=1))
    rows = []
    for n, ins in enumerate(result.tac, start=1):
        def cell(v):
            if v is None:
                return "–"
            return "{…}" if isinstance(v, list) else esc(v)
        rows.append(f'<tr><td>{n}</td><td class="mono">{esc(ins.op)}</td><td class="mono">{cell(ins.arg1)}</td>'
                    f'<td class="mono">{cell(ins.arg2)}</td><td class="mono">{esc(ins.result)}</td><td>{ins.line}</td></tr>')

    left, right = st.columns([1, 1.15], gap="medium")
    with left:
        show('<div class="panel-title">Three-address code</div><div class="tac">' + listing + "</div>")
        show('<p class="rule" style="margin-top:.6rem">One operation per line. <span class="tac-temp">T1, T2…</span> '
             "are temporaries invented by the compiler.</p>")
        st.download_button("⬇ Download TAC", "\n".join(str(i) for i in result.tac) + "\n",
                           file_name="program.tac", mime="text/plain")
    with right:
        show('<div class="panel-title">Same code as quadruples</div><div class="scroll"><table class="t">'
             "<tr><th>#</th><th>op</th><th>arg1</th><th>arg2</th><th>result</th><th>src line</th></tr>"
             + "".join(rows) + "</table></div>")


# ---------------------------------------------------------------------------
# Tab 4 - Print output
# ---------------------------------------------------------------------------
def render_output_tab(result):
    if result.status[PHASES[3]] != STATUS_OK:
        skipped_state(result, "Running the program")
        return
    if not result.output:
        empty_state("This program prints nothing", "Add a line such as  print C  to see a matrix here.")
        return

    show('<p class="rule">Output produced by running the generated TAC.</p>')
    cards = []
    for item in result.output:
        rows = "".join("<tr>" + "".join(f"<td>{esc(clean_number(v))}</td>" for v in row) + "</tr>"
                       for row in item.matrix)
        cards.append(f'<div class="mx-card"><div class="mx-head"><b>{esc(item.name)}</b>'
                     f'<span>{len(item.matrix)} × {len(item.matrix[0])} · line {item.line}</span></div>'
                     f'<table class="mx">{rows}</table></div>')
    show("".join(cards))


# ---------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------
if "dark" not in st.session_state:
    st.session_state.dark = True
if "source" not in st.session_state:
    st.session_state.source = read_example("test2_valid_addition.ms")

show(STYLE % (DARK if st.session_state.dark else LIGHT))

title_col, toggle_col = st.columns([5, 1], vertical_alignment="center")
with title_col:
    show('<div class="hero"><div class="h1" role="heading" aria-level="1">Matrix<span>Script</span> Compiler</div>'
         '<p>A visual matrix-arithmetic compiler: Lexer ➜ Parser ➜ Semantic dimension check ➜ Three-address code</p></div>')
with toggle_col:
    st.toggle("🌙 Dark mode", key="dark")

source = st.session_state.source
result = compile_source(source) if source.strip() else None
render_pipeline(result)

left, right = st.columns([5, 7], gap="large")

with left:
    show('<div class="panel-title">Input editor</div>')
    names = st.columns(2)
    for i, (label, filename) in enumerate(EXAMPLES):
        names[i % 2].button(label, key=f"ex{i}", on_click=load_example, args=(filename,), use_container_width=True)
    st.text_area("MatrixScript source", key="source", height=330, label_visibility="collapsed")
    st.button("▶ Compile & Run", type="primary", use_container_width=True)
    st.caption("Results update as you edit (press Ctrl+Enter or click Compile to apply).")
    with st.expander("MatrixScript cheat sheet"):
        st.code("# declare (values are optional, row by row)\n"
                "matrix A[2][3] = {1, 2, 3, 4, 5, 6}\n"
                "matrix C[2][2]\n\n"
                "# assign: only + and *\n"
                "C = A * B + D\n\n"
                "# show a matrix\n"
                "print C", language="text")

with right:
    show('<div class="panel-title">Compiled output</div>')
    render_banner(result, source)
    if result is None:
        empty_state("No output yet", "Compiled results will appear here as soon as the editor has code.")
    else:
        labels = ["🔤 Tokens", "🛡 Semantic Check", "🧾 Generated TAC", "🖨 Print Output"]
        # Open the most useful tab by default: the one that explains the result.
        if result.success:
            first = labels[3]
        elif result.failed_phase == PHASES[2]:
            first = labels[1]
        else:
            first = labels[0]
        try:
            t1, t2, t3, t4 = st.tabs(labels, default=first)
        except TypeError:                      # older Streamlit without default=
            t1, t2, t3, t4 = st.tabs(labels)
        with t1:
            render_tokens_tab(result)
        with t2:
            render_semantic_tab(result, source)
        with t3:
            render_tac_tab(result)
        with t4:
            render_output_tab(result)
