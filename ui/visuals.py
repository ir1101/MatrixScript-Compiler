"""
visuals.py - Pictures of what each compiler phase produced.

    token_stream()   tokens drawn as coloured chips, one row per source line
    ast_svg()        a statement's syntax tree as an SVG drawing
    shape_html()     a matrix drawn as a little grid of cells (rows x cols)
    check_card()     one dimension check drawn as  [A] x [B] = [result]
    tac_map()        which TAC lines came from which source line
"""

from matrixscript.ast_nodes import Assignment, BinOp, Declaration, Var, statement_to_text
from matrixscript.lexer import TOKEN_EOF

from .components import TOKEN_STYLE, colour_tac, esc, svg_img
from .theme import palette

SHORT_NAME = {
    "TOKEN_MATRIX": "MATRIX", "TOKEN_PRINT": "PRINT", "TOKEN_ID": "ID", "TOKEN_NUMBER": "NUM",
    "TOKEN_PLUS": "PLUS", "TOKEN_STAR": "STAR", "TOKEN_ASSIGN": "ASSIGN", "TOKEN_LBRACKET": "LBRACK",
    "TOKEN_RBRACKET": "RBRACK", "TOKEN_LBRACE": "LBRACE", "TOKEN_RBRACE": "RBRACE", "TOKEN_COMMA": "COMMA",
}


# ---------------------------------------------------------------------------
# tokens
# ---------------------------------------------------------------------------
def token_stream(tokens, errors):
    """One row per source line; each token is a chip showing its text and type."""
    rows = {}
    for t in tokens:
        if t.type == TOKEN_EOF:
            continue
        chip = (f'<span class="tok {TOKEN_STYLE[t.type]}" title="{esc(t.type)} at {t.line}:{t.column}">'
                f'<b>{esc(t.lexeme)}</b><small>{SHORT_NAME[t.type]}</small></span>')
        rows.setdefault(t.line, []).append((t.column, chip))
    for e in errors:
        if e.phase == "Lexer":
            chip = (f'<span class="tok bad" title="{esc(e.message)}"><b>?</b><small>ERROR</small></span>')
            rows.setdefault(e.line, []).append((e.column, chip))
    body = "".join(
        f'<div class="row"><span class="ln">{line}</span><div class="toks">'
        + "".join(c for _, c in sorted(chips, key=lambda x: x[0])) + "</div></div>"
        for line, chips in sorted(rows.items()))
    return f'<div class="stream">{body}</div>'


def token_legend(tokens):
    counts = {}
    for t in tokens:
        if t.type != TOKEN_EOF:
            family = TOKEN_STYLE[t.type]
            counts[family] = counts.get(family, 0) + 1
    names = [("k-kw", "Keywords"), ("k-id", "Names"), ("k-num", "Numbers"),
             ("k-op", "Operators"), ("k-punct", "Punctuation")]
    return '<div class="legend">' + "".join(
        f'<span class="{css}"><i></i><span style="color:var(--muted)">{label} · {counts.get(css, 0)}</span></span>'
        for css, label in names) + "</div>"


# ---------------------------------------------------------------------------
# syntax tree (SVG)
# ---------------------------------------------------------------------------
def _node(label, kind, children=(), size=None):
    return {"label": str(label), "kind": kind, "kids": list(children), "size": size}


def _expr_tree(expr):
    if isinstance(expr, Var):
        return _node(expr.name, "var", size=expr.size)
    return _node(expr.op, "op", [_expr_tree(expr.left), _expr_tree(expr.right)], size=expr.size)


def _statement_tree(stmt, symbols):
    if isinstance(stmt, Declaration):
        kids = [_node(stmt.name, "var"), _node(f"{stmt.rows}×{stmt.cols}", "num")]
        if stmt.values:
            kids.append(_node(f"{len(stmt.values)} values", "num"))
        return _node("matrix", "kw", kids)
    if isinstance(stmt, Assignment):
        target = symbols.get(stmt.target)
        target_size = (target.rows, target.cols) if target else None
        return _node("=", "assign", [_node(stmt.target, "var", size=target_size), _expr_tree(stmt.expr)])
    symbol = symbols.get(stmt.name)
    return _node("print", "kw", [_node(stmt.name, "var", size=(symbol.rows, symbol.cols) if symbol else None)])


def ast_svg(stmt, symbols):
    """Draw one statement's tree. Leaves are spread out evenly; a parent sits
    above the middle of its children."""
    root = _statement_tree(stmt, symbols)
    gap_y, pad = 78, 18
    counter = [0]

    def place(n, depth):
        n["depth"] = depth
        if not n["kids"]:
            n["x"] = counter[0]
            counter[0] += 1
        else:
            for k in n["kids"]:
                place(k, depth + 1)
            n["x"] = (n["kids"][0]["x"] + n["kids"][-1]["x"]) / 2

    place(root, 0)
    leaves = counter[0]

    def depth_of(n):
        return max([n["depth"]] + [depth_of(k) for k in n["kids"]])

    def box_w(n):
        return max(40, 9 * len(n["label"]) + 22)

    widest = max(box_w(n) for n in _walk(root))
    gap_x = max(64, widest + 12)          # leaves never overlap, however long their labels
    has_sizes = any(n["size"] for n in _walk(root))
    box_h = 46 if has_sizes else 34       # taller boxes leave room for the size under the label
    width = (leaves - 1) * gap_x + widest + 2 * pad
    height = depth_of(root) * gap_y + box_h + 2 * pad
    x0 = pad + widest / 2

    def cx(n):
        return x0 + n["x"] * gap_x

    def cy(n):
        return pad + box_h / 2 + n["depth"] * gap_y

    colors = palette()
    kind_color = {"assign": colors["accent"], "op": colors["k-op"], "var": colors["k-id"],
                  "kw": colors["k-kw"], "num": colors["k-num"]}
    mono = "JetBrains Mono, Cascadia Code, Consolas, monospace"

    edges, nodes = [], []
    for n in _walk(root):
        for k in n["kids"]:
            y1, y2 = cy(n) + box_h / 2, cy(k) - box_h / 2
            mid = (y1 + y2) / 2
            edges.append(f'<path d="M{cx(n):.1f},{y1:.1f} C{cx(n):.1f},{mid:.1f} {cx(k):.1f},{mid:.1f} {cx(k):.1f},{y2:.1f}" '
                         f'stroke="{colors["border-strong"]}" stroke-width="1.6" fill="none"/>')
        w = box_w(n)
        c = kind_color[n["kind"]]
        text_fill = colors["text"] if n["kind"] == "assign" else c
        top = cy(n) - box_h / 2
        label_y = cy(n) - 3 if n["size"] else cy(n) + 4.5
        size = ""
        if n["size"]:
            size = (f'<text x="{cx(n):.1f}" y="{cy(n) + 13:.1f}" text-anchor="middle" font-family="Segoe UI, system-ui, sans-serif" '
                    f'font-size="10.5" font-weight="600" fill="{colors["muted"]}">{n["size"][0]}×{n["size"][1]}</text>')
        nodes.append(f'<rect x="{cx(n) - w / 2:.1f}" y="{top:.1f}" width="{w}" height="{box_h}" rx="10" '
                     f'fill="{colors["panel"]}" stroke="{c}" stroke-width="1.4"/>'
                     f'<rect x="{cx(n) - w / 2:.1f}" y="{top:.1f}" width="{w}" height="{box_h}" rx="10" fill="{c}" fill-opacity=".16"/>'
                     f'<text x="{cx(n):.1f}" y="{label_y:.1f}" text-anchor="middle" font-family="{mono}" font-size="13" '
                     f'font-weight="700" fill="{text_fill}">{esc(n["label"])}</text>{size}')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
           f'viewBox="0 0 {width:.0f} {height:.0f}">' + "".join(edges) + "".join(nodes) + "</svg>")
    return svg_img(svg, f"Syntax tree for {statement_to_text(stmt)}", "ast")


def _walk(n):
    yield n
    for k in n["kids"]:
        yield from _walk(k)


def ast_gallery(statements, symbols):
    cards = []
    for stmt in statements:
        wide = isinstance(stmt, Assignment) and isinstance(stmt.expr, BinOp) and isinstance(stmt.expr.left, BinOp)
        cards.append(f'<div class="ast-card{" wide" if wide else ""}"><div class="cap"><code>{esc(statement_to_text(stmt))}</code>'
                     f'<span>line {stmt.line}</span></div>{ast_svg(stmt, symbols)}</div>')
    return '<div class="ast-grid">' + "".join(cards) + "</div>"


# ---------------------------------------------------------------------------
# matrix shapes + dimension checks
# ---------------------------------------------------------------------------
def shape_html(name, rows, cols, tone="sym-a", hot=None, hot_ok=True, cell=None):
    """A matrix as a grid of cells. `hot` ("rows" or "cols") highlights one number in the caption."""
    biggest = max(rows, cols)
    cell = cell or (16 if biggest <= 3 else 12 if biggest <= 6 else 8)
    cells = "<i></i>" * (rows * cols)
    r = f'<span class="hot {"ok" if hot_ok else "bad"}">{rows}</span>' if hot == "rows" else str(rows)
    c = f'<span class="hot {"ok" if hot_ok else "bad"}">{cols}</span>' if hot == "cols" else str(cols)
    return (f'<div class="shape {tone}" style="--cell:{cell}px">'
            f'<div class="grid" style="grid-template-columns:repeat({cols}, var(--cell))">{cells}</div>'
            f'<div class="cap"><b>{esc(name)}</b>{r} × {c}</div></div>')


def check_card(check, source_line):
    """Draw one operator check (+, * or the final =) from the semantic log."""
    d = check.detail
    lr, lc = d["left_size"]
    rr, rc = d["right_size"]
    ok = check.ok
    if d["op"] == "*":
        left = shape_html(d["left"], lr, lc, "sym-a", hot="cols", hot_ok=ok)
        right = shape_html(d["right"], rr, rc, "sym-b", hot="rows", hot_ok=ok)
        rule = (f"Columns of {d['left']} ({lc}) {'=' if ok else '≠'} rows of {d['right']} ({rr})")
        op = "×"
    elif d["op"] == "+":
        left = shape_html(d["left"], lr, lc, "sym-a")
        right = shape_html(d["right"], rr, rc, "sym-b")
        rule = (f"{d['left']} is {lr}×{lc}, {d['right']} is {rr}×{rc}: "
                + ("same size" if ok else "different sizes"))
        op = "+"
    else:   # "=" : does the result fit the target?
        left = shape_html(d["left"], lr, lc, "sym-r")
        right = shape_html("result", rr, rc, "sym-a")
        rule = f"{d['left']} is {lr}×{lc} and the result is {rr}×{rc}: " + ("it fits" if ok else "it does not fit")
        op = "←"

    if d["op"] == "=":
        eq = f'<div class="eq">{left}<span class="op">{op}</span>{right}</div>'
    else:
        result = (shape_html("result", *d["result_size"], "sym-r") if d["result_size"]
                  else '<div class="q" title="No valid result">?</div>')
        eq = f'<div class="eq">{left}<span class="op">{op}</span>{right}<span class="op">=</span>{result}</div>'

    verdict = "ok" if ok else "bad"
    mark = "✓ " if ok else "✕ "
    title = f"{d['left']} {d['op']} {d['right']}" if d["op"] != "=" else f"{d['left']} = {d['right']}"
    return (f'<div class="eq-card {verdict}"><div class="head"><code>{esc(title)}</code>'
            f'<span>line {check.line} · {esc(source_line)}</span></div>{eq}'
            f'<div class="verdict {verdict}">{mark}{esc(rule)}</div></div>')


def symbol_shapes(symbols):
    return '<div class="shapes">' + "".join(
        shape_html(s.name, s.rows, s.cols, "sym-r") for s in symbols.values()) + "</div>"


# ---------------------------------------------------------------------------
# source -> TAC mapping
# ---------------------------------------------------------------------------
def tac_map(source, tac):
    lines = source.splitlines()
    groups = {}
    for ins in tac:
        groups.setdefault(ins.line, []).append(ins)
    rows = []
    for line, instructions in groups.items():
        src = lines[line - 1].strip() if 1 <= line <= len(lines) else ""
        dst = "".join(f"<span>{colour_tac(str(i))}</span>" for i in instructions)
        rows.append(f'<div class="r"><div class="src"><small>{line}</small>{esc(src)}</div>'
                    f'<div class="arr">→</div><div class="dst">{dst}</div></div>')
    return '<div class="map">' + "".join(rows) + "</div>"
