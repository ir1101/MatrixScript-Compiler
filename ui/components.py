"""
components.py - Reusable pieces of HTML used by several pages.

Rule: everything that came from the user's program goes through esc()
before it is placed inside HTML.
"""

import base64
import html
import re

import streamlit as st

from matrixscript import PHASES
from matrixscript.compiler import STATUS_OK, STATUS_SKIPPED
from matrixscript.executor import clean_number
from matrixscript.lexer import (
    TOKEN_ASSIGN, TOKEN_COMMA, TOKEN_EOF, TOKEN_ID, TOKEN_LBRACE, TOKEN_LBRACKET,
    TOKEN_MATRIX, TOKEN_NUMBER, TOKEN_PLUS, TOKEN_PRINT, TOKEN_RBRACE,
    TOKEN_RBRACKET, TOKEN_STAR,
)

from .theme import theme_toggle

# Colour family of each token type (matches the .k-* CSS classes)
TOKEN_STYLE = {
    TOKEN_MATRIX: "k-kw", TOKEN_PRINT: "k-kw", TOKEN_ID: "k-id", TOKEN_NUMBER: "k-num",
    TOKEN_PLUS: "k-op", TOKEN_STAR: "k-op", TOKEN_ASSIGN: "k-op",
    TOKEN_LBRACKET: "k-punct", TOKEN_RBRACKET: "k-punct", TOKEN_LBRACE: "k-punct",
    TOKEN_RBRACE: "k-punct", TOKEN_COMMA: "k-punct", TOKEN_EOF: "k-punct",
}


# ---------------------------------------------------------------------------
# basics
# ---------------------------------------------------------------------------
def esc(value):
    return html.escape(str(value))


def show(markup):
    """Draw raw HTML. st.html skips the Markdown step, so * and newlines stay untouched."""
    st.html(markup)


def svg_img(svg, alt, css_class=""):
    """st.html removes inline <svg>, so pictures are embedded as data-URI images instead."""
    data = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img class="{css_class}" alt="{esc(alt)}" src="data:image/svg+xml;base64,{data}">'


def page_header(eyebrow, title_html, subtitle):
    """Eyebrow + big title + subtitle, with the theme switch on the right."""
    left, right = st.columns([6, 1], vertical_alignment="top")
    with left:
        show(f'<div class="eyebrow"><span class="pulse"></span>{esc(eyebrow)}</div>'
             f'<div class="page-title" role="heading" aria-level="1">{title_html}</div>'
             f'<p class="page-sub">{esc(subtitle)}</p>')
    with right:
        theme_toggle()
    show('<div style="height:1.4rem"></div>')


def section(title, subtitle=""):
    sub = f'<p class="section-sub">{esc(subtitle)}</p>' if subtitle else ""
    show(f'<div class="section-title" role="heading" aria-level="2">{esc(title)}</div>{sub}')


def spacer():
    show('<div class="spacer"></div>')


def empty_state(title, text):
    show(f'<div class="empty"><b>{esc(title)}</b>{esc(text)}</div>')


def skipped_state(result, what):
    empty_state(f"{what} was skipped",
                f"The {result.failed_phase} reported an error, so the compiler stopped before this step. "
                "Fix the error and compile again.")


def code_html(source, highlight_line=None):
    """Source code with line numbers, comments dimmed and one line optionally highlighted."""
    rows = []
    for number, line in enumerate(source.splitlines(), start=1):
        text = esc(line)
        if "#" in line:
            before, _, after = line.partition("#")
            text = esc(before) + f'<span class="cm">#{esc(after)}</span>'
        row = f'<span class="ln">{number}</span>{text}'
        if number == highlight_line:
            row = f'<span class="hl">{row}</span>'
        rows.append(row)
    return "<pre>" + "\n".join(rows) + "</pre>"


# ---------------------------------------------------------------------------
# pipeline strip + result banner + error cards
# ---------------------------------------------------------------------------
def pipeline_strip(result):
    parts = []
    for phase in PHASES:
        state = result.status.get(phase, STATUS_SKIPPED) if result else "idle"
        css = {"ok": "ok", "failed": "failed"}.get(state, "")
        mark = {"ok": " ✓", "failed": " ✕"}.get(state, "")
        parts.append(f'<span class="chip {css}"><span class="dot"></span>{esc(phase)}{mark}</span>')
    show('<div class="pipe">' + '<span class="arrow"></span>'.join(parts) + "</div>")


def result_banner(result, source):
    if result is None:
        show('<div class="banner idle"><div class="icon">…</div><div><p class="t">Nothing to compile yet</p>'
             '<p class="s">Type a program in the editor or pick an example.</p></div></div>')
        return

    if result.success:
        stats = [f"{len(result.tokens) - 1} tokens", f"{len(result.symbols)} matrices",
                 f"{len(result.checks)} checks passed", f"{len(result.tac)} TAC instructions"]
        chips = "".join(f'<span class="stat">{esc(s)}</span>' for s in stats)
        show('<div class="banner ok"><div class="icon">✓</div><div>'
             '<p class="t">Compiled successfully</p>'
             f'<p class="s">All four phases passed with no errors.</p><div class="stat-row">{chips}</div></div></div>')
        return

    count = len(result.errors)
    noun = "error" if count == 1 else "errors"
    show('<div class="banner err"><div class="icon">✕</div><div>'
         f'<p class="t">Compilation failed: {count} {noun} in the {esc(result.failed_phase)}</p>'
         '<p class="s">The phases after this one were not run.</p></div></div>')
    error_cards(result.errors, source)


def error_cards(errors, source):
    lines = source.splitlines()
    for err in errors:
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
# the four output tabs
# ---------------------------------------------------------------------------
def tokens_table(result):
    rows = []   # (line, column, order, html)
    for t in result.tokens:
        css = TOKEN_STYLE.get(t.type, "k-punct")
        dim = ' class="dim"' if t.type == TOKEN_EOF else ""
        lexeme = "(end of input)" if t.type == TOKEN_EOF else esc(t.lexeme)
        rows.append((t.line, t.column, 1, f'<tr{dim}><td>{t.line}:{t.column}</td>'
                     f'<td><span class="badge {css}">{esc(t.type)}</span></td><td class="mono">{lexeme}</td></tr>'))
    for e in result.errors:               # lexical errors appear in red, where they happened
        if e.phase == "Lexer":
            rows.append((e.line, e.column, 0, f'<tr class="bad"><td>{e.line}:{e.column}</td>'
                         f'<td>✕ LEXICAL ERROR</td><td>{esc(e.message)}</td></tr>'))
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    show(f'<p class="rule">The lexer cut the text into <b>{len(result.tokens) - 1}</b> labelled tokens, '
         'reading left to right, line by line.</p>'
         '<div class="scroll"><table class="t"><tr><th>Line:Col</th><th>Token type</th><th>Text</th></tr>'
         + "".join(r[3] for r in rows) + "</table></div>")


def semantic_panel(result, source):
    if result.status[PHASES[2]] == STATUS_SKIPPED:
        skipped_state(result, "Semantic checking")
        return
    show('<p class="rule">Rules: <code>A + B</code> needs the <b>same size</b> · '
         '<code>A * B</code> needs <b>A.cols = B.rows</b> · <code>C = …</code> needs the result to <b>fit C</b>.</p>')
    if result.symbols:
        show('<p class="label">Symbol table</p>' + "".join(
            f'<span class="sym"><b>{esc(s.name)}</b><span>{s.rows} rows × {s.cols} cols</span></span>'
            for s in result.symbols.values()))
    lines = source.splitlines()
    rows = []
    for c in result.checks:
        src = lines[c.line - 1].strip() if 1 <= c.line <= len(lines) else ""
        icon = '<span class="pass">✓</span>' if c.ok else '<span class="fail">✕</span>'
        css = "" if c.ok else ' class="bad"'
        rows.append(f'<tr{css}><td>{c.line}</td><td class="mono">{esc(src)}</td><td>{icon}</td><td>{esc(c.text)}</td></tr>')
    show('<p class="label" style="margin-top:.6rem">Check log</p>'
         '<div class="scroll"><table class="t"><tr><th>Line</th><th>Statement</th><th></th><th>Check</th></tr>'
         + "".join(rows) + "</table></div>")


def colour_tac(text):
    text = esc(text)
    text = re.sub(r"\bT\d+\b", lambda m: f'<span class="tac-temp">{m.group(0)}</span>', text)
    return re.sub(r"^(declare|print)\b", lambda m: f'<span class="tac-kw">{m.group(0)}</span>', text)


def tac_listing(result):
    return ('<div class="tac">' + "".join(
        f'<div class="tac-line"><span class="ln">{n}</span><span>{colour_tac(str(ins))}</span></div>'
        for n, ins in enumerate(result.tac, start=1)) + "</div>")


def tac_panel(result):
    if result.status[PHASES[3]] != STATUS_OK:
        skipped_state(result, "Code generation")
        return

    def cell(v):
        if v is None:
            return "–"
        return "{…}" if isinstance(v, list) else esc(v)

    rows = "".join(f'<tr><td>{n}</td><td class="mono">{esc(i.op)}</td><td class="mono">{cell(i.arg1)}</td>'
                   f'<td class="mono">{cell(i.arg2)}</td><td class="mono">{esc(i.result)}</td><td>{i.line}</td></tr>'
                   for n, i in enumerate(result.tac, start=1))
    left, right = st.columns([1, 1.15], gap="medium")
    with left:
        show('<p class="label">Three-address code</p>' + tac_listing(result)
             + '<p class="rule" style="margin-top:.7rem">One operation per line. <span class="tac-temp">T1, T2…</span> '
               "are temporaries the compiler invents.</p>")
        st.download_button("Download TAC", "\n".join(str(i) for i in result.tac) + "\n",
                           file_name="program.tac", mime="text/plain", icon=":material/download:")
    with right:
        show('<p class="label">Same code as quadruples</p><div class="scroll"><table class="t">'
             "<tr><th>#</th><th>op</th><th>arg1</th><th>arg2</th><th>result</th><th>line</th></tr>"
             + rows + "</table></div>")


def matrix_cards(outputs):
    cards = []
    for item in outputs:
        rows = "".join("<tr>" + "".join(f"<td>{esc(clean_number(v))}</td>" for v in row) + "</tr>"
                       for row in item.matrix)
        cards.append(f'<div class="mx-card"><div class="mx-head"><b>{esc(item.name)}</b>'
                     f'<span>{len(item.matrix)} × {len(item.matrix[0])} · line {item.line}</span></div>'
                     f'<table class="mx">{rows}</table></div>')
    return '<div class="mx-wrap">' + "".join(cards) + "</div>"


def output_panel(result):
    if result.status[PHASES[3]] != STATUS_OK:
        skipped_state(result, "Running the program")
        return
    if not result.output:
        empty_state("This program prints nothing", "Add a line such as  print C  to see a matrix here.")
        return
    show('<p class="rule">Produced by executing the generated TAC.</p>' + matrix_cards(result.output))
