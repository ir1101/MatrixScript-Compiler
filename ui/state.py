"""
state.py - Things every page shares: the example programs, the program that is
currently in the editor, and a way to jump to another page.

Streamlit forgets a widget's value when you move to a page that does not show
that widget, so the program text is kept in a plain session key ("program")
that no widget owns.
"""

import os

import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE_DIR = os.path.join(ROOT, "examples")

# (short label, file name, one-line description)
EXAMPLES = [
    ("Declare & print", "test1_valid_declaration_print.ms", "The smallest valid program."),
    ("Matrix addition", "test2_valid_addition.ms", "Two 2x2 matrices added together."),
    ("Dimension error", "test3_dimension_mismatch.ms", "A 2x3 times a 2x2 - caught at compile time."),
    ("Lexical error", "test4_lexical_error.ms", "A stray $ the lexer does not know."),
    ("Multiplication", "bonus_valid_multiplication.ms", "2x3 times 3x2 gives a 2x2."),
    ("Chained TAC", "bonus_chained_expression.ms", "Two operations, two temporaries."),
]

DEFAULT_EXAMPLE = "test2_valid_addition.ms"

# Filled in by app.py so pages can link to each other: name -> st.Page
PAGES = {}


def read_example(filename):
    with open(os.path.join(EXAMPLE_DIR, filename), encoding="utf-8") as f:
        return f.read()


def init_state():
    """Create the shared session keys the first time the app opens."""
    if "program" not in st.session_state:
        st.session_state.program = read_example(DEFAULT_EXAMPLE)
    if "theme_dark" not in st.session_state:
        st.session_state.theme_dark = True


def set_program(text):
    st.session_state.program = text
    st.session_state.editor = text      # also refresh the editor widget, if it exists


def go(page_name):
    """Switch to another page (call this from normal code, not from a callback)."""
    st.switch_page(PAGES[page_name])


def open_in_playground(text):
    set_program(text)
    go("playground")
