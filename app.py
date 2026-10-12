"""
app.py - The MatrixScript web app (Streamlit). Run it with:

    streamlit run app.py

This file only sets up the theme and the navigation. Each page lives in the
views/ folder, the shared drawing code in ui/, and the compiler itself in
matrixscript/.
"""

import os

import streamlit as st

from ui.state import PAGES, init_state
from ui.theme import apply_theme
from views import home, language, playground, testlab, visualizer, viva

HERE = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="MatrixScript Compiler", page_icon=os.path.join(HERE, "assets", "icon.svg"),
                   layout="wide")

init_state()
apply_theme()
st.logo(os.path.join(HERE, "assets", "logo.svg"), icon_image=os.path.join(HERE, "assets", "icon.svg"), size="large")

PAGES.update({
    "home": st.Page(home.render, title="Home", icon=":material/home:", default=True),
    "playground": st.Page(playground.render, title="Playground", icon=":material/code:", url_path="playground"),
    "visualizer": st.Page(visualizer.render, title="Step by step", icon=":material/account_tree:", url_path="steps"),
    "language": st.Page(language.render, title="Language", icon=":material/menu_book:", url_path="language"),
    "tests": st.Page(testlab.render, title="Test lab", icon=":material/science:", url_path="tests"),
    "viva": st.Page(viva.render, title="Viva prep", icon=":material/school:", url_path="viva"),
})

try:
    navigation = st.navigation(list(PAGES.values()), position="top")
except TypeError:                       # older Streamlit: navigation lives in the sidebar
    navigation = st.navigation(list(PAGES.values()))
navigation.run()
