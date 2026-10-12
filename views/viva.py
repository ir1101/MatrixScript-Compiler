"""Viva prep page - the pitch, one card per phase, likely questions and the demo plan."""

import streamlit as st

from ui.components import esc, page_header, section, show, spacer

PITCH = ("MatrixScript is a tiny compiler for matrix arithmetic. It reads a program in four steps: the "
         "<b>Lexer</b> cuts the text into tokens, the <b>Parser</b> checks the grammar and builds a tree, the "
         "<b>Semantic Analyzer</b> checks that the matrix sizes make sense, and the <b>TAC generator</b> writes "
         "simple one-operation-per-line code. If any step finds a mistake, it stops and shows the line number "
         "and the reason.")

PHASES = [
    ("1", "Lexer", "I convert text into labelled tokens, like turning the word matrix into TOKEN_MATRIX.",
     "A loop reads one character at a time: spaces and comments are skipped, letters make a word, digits make a "
     "number, and + * = [ ] { } , are single tokens. Anything else is a lexical error.",
     ["token", "lexeme", "keyword vs identifier", "lexical error"]),
    ("2", "Parser", "I check that the tokens follow the grammar and build a tree.",
     "One small method per grammar rule. Each one expects certain tokens next; the wrong token raises a syntax "
     "error. + is handled in parse_expression and * one level deeper in parse_term, so * is done first.",
     ["grammar", "recursive descent", "AST", "precedence", "panic-mode recovery"]),
    ("3", "Semantic analyzer", "The parser knows the shape of a statement; I check its meaning: the sizes.",
     "A symbol table maps each matrix to its rows and columns. For A * B it checks A.cols = B.rows and works out "
     "the result size; for A + B it checks both sizes are equal; then the result must fit the target.",
     ["symbol table", "type checking", "annotated AST", "compile time vs run time"]),
    ("4", "TAC generator", "I rewrite each statement as small steps that do one operation each.",
     "Walking the tree, every + or * gets a fresh temporary (T1, T2, …) and the last one is copied into the "
     "target. Each instruction is stored as a quadruple: op, arg1, arg2, result.",
     ["intermediate code", "temporaries", "quadruples"]),
]

QUESTIONS = [
    ("What is a token?", "A labelled piece of the source code, such as TOKEN_PLUS for +. The text itself is called the lexeme."),
    ("What is the difference between lexical, syntax and semantic errors?",
     "Lexical: a character that is not in the language ($). Syntax: tokens in the wrong order (A = + B). "
     "Semantic: correct order but wrong meaning, like multiplying a 2×3 by a 2×2."),
    ("Why can't the parser catch the dimension error?",
     "The grammar has no memory of sizes. Sizes live in the symbol table, which the semantic analyzer builds and reads."),
    ("What is a symbol table?", "A dictionary from each name to what we know about it; here the rows, the columns and the line it was declared on."),
    ("What is an AST?", "An abstract syntax tree: the structure of a statement with the punctuation removed. "
                        "Operators are inner nodes and matrix names are leaves."),
    ("Which parsing technique do you use?", "Recursive descent: one method per grammar rule. The repeated parts use while loops, so it does not recurse deeply."),
    ("How is * done before +?", "By grammar levels. expression handles + and calls term, which handles *. So * sits lower in the tree and its code is generated first."),
    ("What is three-address code?", "Code where each instruction has at most one operator and three names, for example T1 = A + B."),
    ("Why do you need temporaries?", "A * B + C has two operations, so the result of the first one needs a name before the second can use it."),
    ("Why does compilation stop after an error?", "Each phase needs correct input from the previous one. Inside a phase, though, all errors are listed."),
    ("Why not use NumPy?", "The goal is to show the compiler phases and the matrix rules clearly, not to be fast. Plain lists keep every step visible."),
    ("What are the limitations?", "Only + and *, no subtraction, no indexing like A[i][j], no loops, and matrices up to 10×10."),
    ("What would you add next?", "Subtraction and transpose, parentheses, an optimisation pass such as constant folding, and code generation for a real machine."),
]

DEMO = [
    ("0:00", "Open the Home page and say the 20-second pitch while pointing at the four phases."),
    ("0:30", "Playground → Declare & print. Green banner. Open the Tokens tab."),
    ("1:15", "Playground → Matrix addition. Open Generated TAC: T1 = A + B, then C = T1. Show Print Output."),
    ("2:15", "Playground → Dimension error. Red banner with line 5. Open Semantic Check and point at the red row."),
    ("3:00", "Fix it live: change B to matrix B[3][2] = {1, 2, 3, 4, 5, 6}. The banner turns green."),
    ("3:45", "Playground → Lexical error. Only the Lexer pill is red; the rest were skipped."),
    ("4:15", "Step by step page → Chained TAC. Show the syntax tree and the two temporaries. Finish."),
]


def render():
    page_header("Viva prep", 'Explain it in <span class="grad">twenty seconds.</span>',
                "Everything you need to present the project: the pitch, one sentence per phase, the questions "
                "examiners usually ask, and a five-minute demo plan.")

    section("The pitch", "Learn this one by heart.")
    show(f'<div class="quote">{PITCH}</div>')

    spacer()
    section("One card per phase", "Lead with the bold sentence, then explain how it works if asked.")
    cards = []
    for num, name, line, how, tags in PHASES:
        chips = "".join(f"<span>{esc(t)}</span>" for t in tags)
        cards.append(f'<div class="phase" style="padding-bottom:1.1rem"><div class="num">{num}</div><h3>{esc(name)}</h3>'
                     f'<p style="color:var(--text);font-weight:600">"{esc(line)}"</p><p>{esc(how)}</p>'
                     f'<div class="tags">{chips}</div></div>')
    show('<div class="phase-row">' + "".join(cards) + "</div>")

    spacer()
    q_col, d_col = st.columns([1.35, 1], gap="large")
    with q_col:
        section("Likely questions", "Click a question to see a short answer.")
        show("".join(f'<details class="faq"><summary>{esc(q)}</summary><div>{esc(a)}</div></details>'
                     for q, a in QUESTIONS))
    with d_col:
        section("Five-minute demo", "A tested order that shows every feature once.")
        show('<div class="card"><div class="timeline">' + "".join(
            f'<div class="ev"><span class="tm">{t}</span><p>{esc(text)}</p></div>' for t, text in DEMO)
            + "</div></div>")
