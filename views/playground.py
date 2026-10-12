"""Playground page - write a program, compile it, inspect every phase."""

import streamlit as st

from matrixscript import PHASES, compile_source
from ui.components import (output_panel, page_header, pipeline_strip, result_banner,
                           semantic_panel, show, tac_panel, tokens_table, empty_state)
from ui.state import EXAMPLES, read_example, set_program

TABS = ["Tokens", "Semantic Check", "Generated TAC", "Print Output"]
TAB_ICONS = [":material/data_array:", ":material/rule:", ":material/format_list_numbered:", ":material/grid_on:"]


def _keep_program():
    """Editor callback: copy the editor text into the shared program key."""
    st.session_state.program = st.session_state.editor


def _load(filename):
    set_program(read_example(filename))


def render():
    page_header("Playground", 'Write it. <span class="grad">Compile it.</span> See inside.',
                "Edit the program on the left. Every phase of the compiler runs again as soon as you apply your change.")

    source = st.session_state.program
    result = compile_source(source) if source.strip() else None
    pipeline_strip(result)

    left, right = st.columns([5, 7], gap="large")

    with left:
        show('<p class="label">Examples</p>')
        cols = st.columns(3)
        for i, (label, filename, help_text) in enumerate(EXAMPLES):
            cols[i % 3].button(label, key=f"ex{i}", help=help_text, on_click=_load, args=(filename,),
                               use_container_width=True)

        lines = source.count("\n") + 1 if source else 0
        show('<div style="height:.6rem"></div><div class="edhead"><span class="file"><i></i><i></i><i></i>program.ms</span>'
             f'<span class="meta">{lines} lines · {len(source)} chars</span></div>')
        st.session_state.editor = st.session_state.program          # editor always shows the shared program
        st.text_area("MatrixScript source", key="editor", height=340, label_visibility="collapsed",
                     on_change=_keep_program)
        st.button("Compile & run", type="primary", icon=":material/play_arrow:", use_container_width=True)
        st.caption("Results refresh when you click outside the editor, press Ctrl+Enter, or click the button.")

        with st.expander("Cheat sheet", icon=":material/menu_book:"):
            st.code("# declare (values optional, row by row)\n"
                    "matrix A[2][3] = {1, 2, 3, 4, 5, 6}\n"
                    "matrix C[2][2]\n\n"
                    "# assign: only + and *  (* first)\n"
                    "C = A * B + D\n\n"
                    "# show a matrix\n"
                    "print C", language="text")

    with right:
        show('<p class="label">Compiled output</p>')
        result_banner(result, source)
        if result is None:
            empty_state("No output yet", "Results appear here as soon as the editor has code.")
            return

        labels = [f"{icon} {name}" for icon, name in zip(TAB_ICONS, TABS)]
        # Open the tab that best explains the result.
        if result.success:
            first = labels[3]
        elif result.failed_phase == PHASES[2]:
            first = labels[1]
        else:
            first = labels[0]
        try:
            t1, t2, t3, t4 = st.tabs(labels, default=first)
        except TypeError:                        # older Streamlit without default=
            t1, t2, t3, t4 = st.tabs(labels)
        with t1:
            tokens_table(result)
        with t2:
            semantic_panel(result, source)
        with t3:
            tac_panel(result)
        with t4:
            output_panel(result)
