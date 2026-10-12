"""
theme.py - The look of the app: colours, fonts and every CSS rule.

Both themes use the same CSS; only the colour variables at the top change.
Fonts load from Google Fonts and fall back to system fonts when offline.
"""

import re

import streamlit as st

DARK = """
  --bg:#0a0c13; --bg-glow-a:rgba(124,108,255,.16); --bg-glow-b:rgba(45,212,200,.10);
  --panel:#11141d; --panel2:#171b27; --panel3:#1e2332; --border:#252b3b; --border-strong:#343c52;
  --text:#eef0f7; --muted:#9ba2b8; --faint:#6b7389;
  --accent:#8f7dff; --accent-2:#38d5cb; --on-accent:#0a0c13;
  --grad:linear-gradient(120deg,#a08cff 0%,#7a8dff 45%,#38d5cb 100%);
  --ok:#3ddc97; --err:#ff6b81; --warn:#ffc861;
  --c-tokens:#76a9ff; --c-sem:#ffc861; --c-tac:#b9a4ff; --c-out:#38d5cb;
  --k-kw:#ff8fb8; --k-id:#7fc4ff; --k-num:#ffc861; --k-op:#b9a4ff; --k-punct:#8a92aa;
  --shadow:0 1px 0 rgba(255,255,255,.04) inset, 0 12px 32px -12px rgba(0,0,0,.55);
  --header:rgba(10,12,19,.72);
"""

LIGHT = """
  --bg:#f6f6fb; --bg-glow-a:rgba(106,92,255,.12); --bg-glow-b:rgba(15,165,160,.10);
  --panel:#ffffff; --panel2:#f2f3f9; --panel3:#e9ebf4; --border:#e1e4ee; --border-strong:#cdd2e1;
  --text:#161a2c; --muted:#565d74; --faint:#7d849a;
  --accent:#6550f0; --accent-2:#0b9690; --on-accent:#ffffff;
  --grad:linear-gradient(120deg,#6a52f5 0%,#4f6cf0 45%,#0b9690 100%);
  --ok:#11845a; --err:#d12e4a; --warn:#a86a10;
  --c-tokens:#2563d9; --c-sem:#a86a10; --c-tac:#6550f0; --c-out:#0b8580;
  --k-kw:#c0306b; --k-id:#1f5fc4; --k-num:#9a5a08; --k-op:#6550f0; --k-punct:#6b7189;
  --shadow:0 1px 2px rgba(22,26,44,.05), 0 10px 30px -14px rgba(22,26,44,.18);
  --header:rgba(246,246,251,.78);
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  /*VARS*/
  --font: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, "Cascadia Code", Consolas, monospace;
  --r-sm: 8px; --r-md: 12px; --r-lg: 18px;
}

/* ===== app shell ===== */
.stApp {
  background:
    radial-gradient(900px 520px at 8% -10%, var(--bg-glow-a), transparent 60%),
    radial-gradient(800px 480px at 100% 0%, var(--bg-glow-b), transparent 60%),
    var(--bg);
  background-attachment: fixed;
  color: var(--text);
}
.stApp, .stApp p, .stApp li, .stApp label, .stApp button, .stApp input, .stApp summary,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp a, .stApp div[role="heading"] { font-family: var(--font); }
.stApp pre, .stApp pre *, .stApp code, .stApp textarea { font-family: var(--mono); }
.stApp p, .stApp li, .stApp label, .stApp summary, .stApp [data-testid="stWidgetLabel"] *,
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stExpander"] * { color: var(--text); }
.stApp [data-testid="stCaptionContainer"] p { color: var(--muted); }

header[data-testid="stHeader"] {
  background: var(--header); backdrop-filter: saturate(160%) blur(14px);
  -webkit-backdrop-filter: saturate(160%) blur(14px); border-bottom: 1px solid var(--border);
}
header[data-testid="stHeader"] a, header[data-testid="stHeader"] a span { color: var(--muted) !important; font-weight: 600; }
header[data-testid="stHeader"] a:hover span { color: var(--text) !important; }
header[data-testid="stHeader"] a[aria-current="page"] { background: color-mix(in srgb, var(--accent) 16%, transparent) !important; }
header[data-testid="stHeader"] a[aria-current="page"] span { color: var(--text) !important; }
header[data-testid="stHeader"] button svg, header[data-testid="stHeader"] [data-testid="stIconMaterial"] { color: var(--muted); }
[data-testid="stDecoration"] { display: none; }
.block-container { max-width: 1320px; padding-top: 5.2rem; padding-bottom: 4rem; }
.stApp a { color: var(--accent); }
::selection { background: color-mix(in srgb, var(--accent) 35%, transparent); }

/* ===== streamlit widgets ===== */
.stButton button, .stDownloadButton button {
  border-radius: var(--r-sm); font-weight: 600; font-size: .88rem; min-height: 2.6rem;
  background: var(--panel); color: var(--text); border: 1px solid var(--border);
  transition: border-color .15s ease-out, color .15s ease-out, transform .15s ease-out, box-shadow .15s ease-out;
}
.stButton button:hover, .stDownloadButton button:hover { border-color: var(--accent); color: var(--accent); }
.stButton button:active { transform: translateY(1px); }
.stButton button:disabled { background: var(--panel); color: var(--faint) !important; border-color: var(--border); opacity: .55; cursor: not-allowed; }
.stButton button:focus-visible, .stDownloadButton button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.stButton button p, .stDownloadButton button p { color: inherit !important; font-weight: 600; }
.stButton button[kind="primary"] {
  background: var(--grad); border: 0; color: #fff;
  box-shadow: 0 8px 24px -10px color-mix(in srgb, var(--accent) 75%, transparent);
}
.stButton button[kind="primary"]:hover { color: #fff; filter: brightness(1.08); }

.stTextArea textarea {
  font-family: var(--mono) !important; font-size: .9rem !important; line-height: 1.7 !important;
  background: var(--panel) !important; color: var(--text) !important; caret-color: var(--accent);
  border: 0 !important; border-radius: 0 0 var(--r-md) var(--r-md) !important; padding: .9rem 1rem !important;
}
.stTextArea div:has(> textarea), .stTextArea [data-baseweb="textarea"] {
  border: 1px solid var(--border) !important; border-top: 0 !important; background: var(--panel) !important;
  border-radius: 0 0 var(--r-md) var(--r-md) !important;
}
.stTextArea div:has(> textarea):focus-within, .stTextArea [data-baseweb="textarea"]:focus-within { border-color: var(--accent) !important; }

label:has(input[role="switch"]) > div:nth-of-type(1) { border: 1px solid var(--border-strong); }
label:has(input[role="switch"]:not(:checked)) > div:nth-of-type(1) { background: var(--panel3) !important; }
label:has(input[role="switch"]:not(:checked)) > div:nth-of-type(1) > div { background: var(--muted) !important; }
label:has(input[role="switch"]:checked) > div:nth-of-type(1) { background: var(--accent) !important; border-color: var(--accent); }

/* tabs - each one has its own colour */
.stTabs [role="tablist"] { gap: .35rem; border-bottom: 1px solid var(--border); }
.stTabs [role="tab"] { height: 2.75rem; padding: 0 1rem; border-radius: var(--r-sm) var(--r-sm) 0 0;
                       background: transparent; border-bottom: 2px solid transparent; cursor: pointer;
                       transition: background .15s ease-out; }
.stTabs [role="tab"] p { font-size: .88rem; font-weight: 600; color: var(--tc) !important; opacity: .72; }
.stTabs [role="tab"]:nth-child(1) { --tc: var(--c-tokens); }
.stTabs [role="tab"]:nth-child(2) { --tc: var(--c-sem); }
.stTabs [role="tab"]:nth-child(3) { --tc: var(--c-tac); }
.stTabs [role="tab"]:nth-child(4) { --tc: var(--c-out); }
.stTabs [role="tab"]:hover p { opacity: 1; }
.stTabs [role="tab"][aria-selected="true"] { background: color-mix(in srgb, var(--tc) 13%, transparent); border-bottom-color: var(--tc); }
.stTabs [role="tab"][aria-selected="true"] p { opacity: 1; }
.stTabs [role="tab"]:focus-visible { outline: 2px solid var(--tc); outline-offset: -2px; }
.stTabs .react-aria-SelectionIndicator, .stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* segmented control + pills */
[data-testid="stButtonGroup"] button {
  background: var(--panel); border-color: var(--border) !important; color: var(--muted);
  font-weight: 600; transition: background .15s ease-out, color .15s ease-out;
}
[data-testid="stButtonGroup"] button p { color: inherit !important; font-weight: 600; font-size: .86rem; }
[data-testid="stButtonGroup"] button:hover { color: var(--text); background: var(--panel2); }
[data-testid="stButtonGroup"] button[kind$="Active"] {
  background: color-mix(in srgb, var(--accent) 18%, var(--panel)) !important; color: var(--text) !important;
  border-color: var(--accent) !important;
}

[data-testid="stExpander"] details { background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-md); }
[data-testid="stExpander"] summary:hover * { color: var(--accent) !important; }
[data-testid="stCode"] pre, .stCode pre { background: var(--panel2) !important; border-radius: var(--r-sm); }
[data-testid="stCode"] code, .stCode code { font-family: var(--mono) !important; color: var(--text) !important; }

/* ===== typography helpers ===== */
.eyebrow { display: inline-flex; align-items: center; gap: .5rem; font-size: .74rem; font-weight: 700;
           letter-spacing: .12em; text-transform: uppercase; color: var(--accent); }
.eyebrow .pulse { width: .5rem; height: .5rem; border-radius: 50%; background: var(--accent-2);
                  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent-2) 22%, transparent); }
.page-title { font-size: 2.1rem; line-height: 1.12; font-weight: 800; letter-spacing: -.025em; margin: .4rem 0 .4rem 0; color: var(--text); }
.page-sub { font-size: 1rem; line-height: 1.55; color: var(--muted); max-width: 68ch; margin: 0; }
.grad { background: var(--grad); -webkit-background-clip: text; background-clip: text; color: transparent; }
.section-title { font-size: 1.25rem; font-weight: 700; letter-spacing: -.01em; margin: 0 0 .25rem 0; color: var(--text); }
.section-sub { font-size: .92rem; color: var(--muted); margin: 0 0 1rem 0; }
.label { font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--faint); margin: 0 0 .55rem 0; }
.muted { color: var(--muted); }
.mono { font-family: var(--mono) !important; }
.spacer { height: 2.2rem; }
.kbd { font-family: var(--mono); font-size: .78rem; padding: .05rem .4rem; border-radius: 5px;
       border: 1px solid var(--border-strong); background: var(--panel2); color: var(--text); }
code.inline { font-family: var(--mono); font-size: .86em; padding: .08rem .38rem; border-radius: 5px;
              background: var(--panel2); border: 1px solid var(--border); color: var(--text); }

/* ===== cards ===== */
.card { background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-lg); padding: 1.25rem 1.35rem;
        box-shadow: var(--shadow); }
.card h3 { font-size: 1.02rem; font-weight: 700; margin: 0 0 .35rem 0; color: var(--text); }
.card p { font-size: .9rem; line-height: 1.55; color: var(--muted); margin: 0; }
.grid-auto { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); }

/* ===== home ===== */
.display { font-size: clamp(2.3rem, 4.6vw, 3.6rem); line-height: 1.04; font-weight: 800; letter-spacing: -.035em;
           margin: 1rem 0 1rem 0; color: var(--text); }
.lead { font-size: 1.1rem; line-height: 1.6; color: var(--muted); max-width: 54ch; margin: 0 0 1.6rem 0; }

.codewin { background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-lg); box-shadow: var(--shadow); overflow: hidden; }
.codewin .bar { display: flex; align-items: center; gap: .45rem; padding: .7rem 1rem; border-bottom: 1px solid var(--border); background: var(--panel2); }
.codewin .bar i { width: .7rem; height: .7rem; border-radius: 50%; background: var(--border-strong); }
.codewin .bar i:nth-child(1) { background: #ff6b81; } .codewin .bar i:nth-child(2) { background: #ffc861; } .codewin .bar i:nth-child(3) { background: #3ddc97; }
.codewin .bar span { margin-left: .5rem; font-family: var(--mono); font-size: .78rem; color: var(--muted); }
.codewin pre { margin: 0; padding: 1rem 1.1rem; font-family: var(--mono); font-size: .88rem; line-height: 1.75; color: var(--text);
               background: transparent; white-space: pre; overflow-x: auto; }
.codewin pre .ln { color: var(--faint); display: inline-block; width: 1.6rem; user-select: none; }
.codewin pre .cm { color: var(--faint); font-style: italic; }
.codewin pre .hl { background: color-mix(in srgb, var(--err) 14%, transparent); border-radius: 4px; box-shadow: -4px 0 0 var(--err); }
.codewin .foot { display: flex; gap: .75rem; align-items: flex-start; padding: .9rem 1.1rem; border-top: 1px solid var(--border);
                 background: color-mix(in srgb, var(--err) 8%, var(--panel)); font-size: .86rem; color: var(--text); }
.codewin .foot b { color: var(--err); }

.phase-row { display: grid; gap: .9rem; grid-template-columns: repeat(4, minmax(0, 1fr)); }
.phase { position: relative; background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-lg);
         padding: 1.15rem 1.15rem 1.2rem 1.15rem; box-shadow: var(--shadow); }
.phase .num { display: inline-grid; place-items: center; width: 2rem; height: 2rem; border-radius: 10px; font-weight: 800;
              font-size: .9rem; color: #fff; background: var(--grad); margin-bottom: .8rem; }
.phase h3 { font-size: 1rem; font-weight: 700; margin: 0 0 .3rem 0; color: var(--text); }
.phase p { font-size: .86rem; line-height: 1.5; color: var(--muted); margin: 0 0 .8rem 0; }
.phase .io { font-family: var(--mono); font-size: .76rem; color: var(--text); background: var(--panel2);
             border: 1px solid var(--border); border-radius: var(--r-sm); padding: .45rem .6rem; }
.phase .io b { color: var(--accent); font-weight: 500; }
.phase:not(:last-child)::after { content: ""; position: absolute; top: 2.15rem; right: -.75rem; width: .6rem; height: .6rem;
             border-top: 2px solid var(--border-strong); border-right: 2px solid var(--border-strong); transform: rotate(45deg); }

.feature .ico { width: 2.4rem; height: 2.4rem; border-radius: 12px; display: grid; place-items: center; margin-bottom: .9rem;
                background: color-mix(in srgb, var(--fc) 15%, transparent); color: var(--fc); }
.feature .ico img { width: 1.3rem; height: 1.3rem; }

.stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border: 1px solid var(--border);
         border-radius: var(--r-lg); background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.stats div { padding: 1.3rem 1.4rem; border-right: 1px solid var(--border); }
.stats div:last-child { border-right: 0; }
.stats b { display: block; font-size: 2rem; font-weight: 800; letter-spacing: -.03em; line-height: 1.1; }
.stats span { font-size: .84rem; color: var(--muted); }

.footer { margin-top: 3.5rem; padding-top: 1.4rem; border-top: 1px solid var(--border); display: flex; justify-content: space-between;
          flex-wrap: wrap; gap: .6rem; font-size: .82rem; color: var(--faint); }

/* ===== pipeline strip ===== */
.pipe { display: flex; flex-wrap: wrap; align-items: center; gap: .45rem; margin: .2rem 0 1.4rem 0; }
.chip { display: inline-flex; align-items: center; gap: .45rem; padding: .42rem .85rem; border-radius: 999px;
        font-size: .8rem; font-weight: 600; border: 1px solid var(--border); background: var(--panel); color: var(--faint); }
.chip .dot { width: .5rem; height: .5rem; border-radius: 50%; background: var(--border-strong); }
.chip.ok { color: var(--ok); border-color: color-mix(in srgb, var(--ok) 55%, transparent); background: color-mix(in srgb, var(--ok) 10%, var(--panel)); }
.chip.ok .dot { background: var(--ok); box-shadow: 0 0 0 3px color-mix(in srgb, var(--ok) 22%, transparent); }
.chip.failed { color: var(--err); border-color: color-mix(in srgb, var(--err) 60%, transparent); background: color-mix(in srgb, var(--err) 10%, var(--panel)); }
.chip.failed .dot { background: var(--err); box-shadow: 0 0 0 3px color-mix(in srgb, var(--err) 22%, transparent); }
.pipe .arrow { width: 1.1rem; height: 1px; background: var(--border-strong); }

/* ===== editor header ===== */
.edhead { display: flex; align-items: center; justify-content: space-between; gap: .5rem; padding: .6rem .9rem;
          background: var(--panel2); border: 1px solid var(--border); border-radius: var(--r-md) var(--r-md) 0 0; }
.edhead .file { display: flex; align-items: center; gap: .45rem; font-family: var(--mono); font-size: .8rem; color: var(--muted); }
.edhead .file i { width: .6rem; height: .6rem; border-radius: 50%; background: var(--border-strong); }
.edhead .file i:nth-child(1) { background: #ff6b81; } .edhead .file i:nth-child(2) { background: #ffc861; } .edhead .file i:nth-child(3) { background: #3ddc97; margin-right: .35rem; }
.edhead .meta { font-size: .76rem; color: var(--faint); font-variant-numeric: tabular-nums; }
/* glue the editor to its header bar so they read as one window */
[data-testid="stElementContainer"]:has(.edhead) + [data-testid="stElementContainer"] { margin-top: -1rem; }

/* ===== banners + errors ===== */
.banner { border-radius: var(--r-lg); padding: 1.05rem 1.25rem; margin-bottom: 1rem; border: 1px solid; display: flex; gap: 1rem; align-items: flex-start; }
.banner .icon { flex: none; width: 2.3rem; height: 2.3rem; border-radius: 50%; display: grid; place-items: center; font-size: 1.1rem; font-weight: 800; color: #fff; }
.banner .t { font-size: 1.05rem; font-weight: 700; margin: .05rem 0 0 0; letter-spacing: -.01em; }
.banner .s { margin: .2rem 0 0 0; font-size: .87rem; color: var(--muted); }
.banner.ok { color: var(--ok); border-color: color-mix(in srgb, var(--ok) 50%, transparent);
             background: linear-gradient(120deg, color-mix(in srgb, var(--ok) 14%, var(--panel)), var(--panel) 70%); }
.banner.ok .icon { background: var(--ok); }
.banner.err { color: var(--err); border-color: color-mix(in srgb, var(--err) 55%, transparent);
              background: linear-gradient(120deg, color-mix(in srgb, var(--err) 14%, var(--panel)), var(--panel) 70%); }
.banner.err .icon { background: var(--err); }
.banner.idle { color: var(--muted); border-color: var(--border); background: var(--panel); }
.banner.idle .icon { background: var(--panel3); color: var(--muted); }
.stat-row { display: flex; flex-wrap: wrap; gap: .45rem; margin-top: .75rem; }
.stat { font-size: .76rem; font-weight: 600; padding: .22rem .6rem; border-radius: 999px; color: var(--text);
        background: color-mix(in srgb, var(--ok) 14%, transparent); border: 1px solid color-mix(in srgb, var(--ok) 30%, transparent); }

.errcard { border: 1px solid color-mix(in srgb, var(--err) 45%, var(--border)); border-left: 4px solid var(--err);
           border-radius: var(--r-md); background: var(--panel); padding: 1rem 1.15rem; margin-bottom: .8rem; }
.errcard .where { font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--err); }
.errcard .msg { font-size: 1rem; font-weight: 600; line-height: 1.45; margin: .3rem 0 .7rem 0; color: var(--text); }
.errcard pre { margin: 0 0 .7rem 0; padding: .65rem .85rem; border-radius: var(--r-sm); background: var(--panel2);
               font-family: var(--mono); font-size: .85rem; line-height: 1.6; overflow-x: auto; color: var(--text); }
.errcard pre .caret { color: var(--err); font-weight: 700; }
.errcard .hint { font-size: .87rem; line-height: 1.5; color: var(--muted); }
.errcard .hint b { color: var(--text); }

/* ===== tables ===== */
.scroll { max-height: 440px; overflow: auto; border: 1px solid var(--border); border-radius: var(--r-md); background: var(--panel); }
table.t { width: 100%; border-collapse: collapse; font-size: .85rem; }
table.t th { position: sticky; top: 0; z-index: 1; background: var(--panel2); color: var(--faint); text-align: left; font-size: .7rem;
             font-weight: 700; letter-spacing: .08em; text-transform: uppercase; padding: .6rem .8rem; border-bottom: 1px solid var(--border); }
table.t td { padding: .45rem .8rem; border-bottom: 1px solid var(--border); font-variant-numeric: tabular-nums; color: var(--text); vertical-align: top; }
table.t tr:last-child td { border-bottom: none; }
table.t tr:hover td { background: color-mix(in srgb, var(--panel2) 60%, transparent); }
table.t tr.bad td { background: color-mix(in srgb, var(--err) 11%, transparent); color: var(--err); font-weight: 600; }
table.t tr.dim td { color: var(--faint); }
.badge { display: inline-block; padding: .1rem .5rem; border-radius: 6px; font-size: .72rem; font-weight: 600;
         font-family: var(--mono); background: color-mix(in srgb, currentColor 13%, transparent); white-space: nowrap; }
.k-kw { color: var(--k-kw); } .k-id { color: var(--k-id); } .k-num { color: var(--k-num); }
.k-op { color: var(--k-op); } .k-punct { color: var(--k-punct); }
.pass { color: var(--ok); font-weight: 700; } .fail { color: var(--err); font-weight: 700; }
.rule { font-size: .86rem; line-height: 1.6; color: var(--muted); margin: 0 0 .9rem 0; }
.rule code, .rule .code { font-family: var(--mono); font-size: .82rem; color: var(--c-sem); background: var(--panel2);
                          padding: .08rem .38rem; border-radius: 5px; }

.sym { display: inline-flex; align-items: baseline; gap: .5rem; padding: .4rem .8rem; margin: 0 .5rem .5rem 0;
       border-radius: var(--r-sm); background: var(--panel); border: 1px solid var(--border); }
.sym b { font-family: var(--mono); font-size: 1rem; color: var(--c-sem); } .sym span { font-size: .8rem; color: var(--muted); }

/* ===== TAC ===== */
.tac { background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-md); padding: .55rem 0; }
.tac-line { display: flex; gap: 1rem; padding: .2rem 1rem; font-family: var(--mono); font-size: .9rem; color: var(--text); }
.tac-line:hover { background: var(--panel2); }
.tac-line .ln { color: var(--faint); width: 1.6rem; text-align: right; user-select: none; }
.tac-temp { color: var(--c-tac); font-weight: 700; } .tac-kw { color: var(--k-kw); }

/* ===== printed matrices ===== */
.mx-wrap { display: flex; flex-wrap: wrap; gap: 1rem; }
.mx-card { padding: .9rem 1.2rem 1.1rem 1.2rem; background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-lg); box-shadow: var(--shadow); }
.mx-head { display: flex; justify-content: space-between; align-items: baseline; gap: 1.6rem; margin-bottom: .7rem; }
.mx-head b { font-family: var(--mono); font-size: 1.1rem; color: var(--c-out); } .mx-head span { font-size: .76rem; color: var(--faint); }
table.mx { border-collapse: separate; border-spacing: .4rem .3rem; border-left: 2px solid var(--text); border-right: 2px solid var(--text); border-radius: 10px; }
table.mx td { min-width: 2.6rem; text-align: right; padding: .15rem .5rem; font-size: 1.15rem; font-family: var(--mono);
              font-variant-numeric: tabular-nums; color: var(--text); }

.empty { text-align: center; padding: 2.4rem 1.2rem; color: var(--muted); border: 1px dashed var(--border-strong); border-radius: var(--r-lg);
         font-size: .92rem; line-height: 1.5; background: color-mix(in srgb, var(--panel) 50%, transparent); }
.empty b { display: block; color: var(--text); font-size: 1rem; margin-bottom: .3rem; }

/* ===== visualizer ===== */
.explain { background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-lg); padding: 1.3rem 1.35rem; box-shadow: var(--shadow); }
.explain .step { font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--accent); }
.explain h3 { font-size: 1.35rem; font-weight: 800; letter-spacing: -.02em; margin: .35rem 0 .6rem 0; color: var(--text); }
.explain p { font-size: .92rem; line-height: 1.6; color: var(--muted); margin: 0 0 1rem 0; }
.explain .io { display: grid; grid-template-columns: auto 1fr; gap: .4rem .8rem; font-size: .85rem; margin-bottom: 1rem; }
.explain .io span { color: var(--faint); font-weight: 600; } .explain .io b { color: var(--text); font-weight: 600; }
.explain .say { border-left: 3px solid var(--accent); padding: .6rem .9rem; border-radius: 0 var(--r-sm) var(--r-sm) 0;
                background: color-mix(in srgb, var(--accent) 9%, transparent); font-size: .88rem; line-height: 1.55; color: var(--text); }
.explain .say b { color: var(--accent); font-size: .7rem; letter-spacing: .1em; text-transform: uppercase; display: block; margin-bottom: .2rem; }

.stream { background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-md); padding: .7rem .4rem; }
.stream .row { display: flex; align-items: flex-start; gap: .8rem; padding: .35rem .6rem; border-radius: var(--r-sm); }
.stream .row:hover { background: var(--panel2); }
.stream .ln { font-family: var(--mono); font-size: .78rem; color: var(--faint); width: 1.4rem; text-align: right; padding-top: .3rem; flex: none; }
.stream .toks { display: flex; flex-wrap: wrap; gap: .35rem; }
.tok { display: inline-flex; flex-direction: column; align-items: center; gap: .05rem; padding: .25rem .5rem .2rem .5rem; border-radius: 7px;
       border: 1px solid color-mix(in srgb, currentColor 35%, transparent); background: color-mix(in srgb, currentColor 10%, transparent); }
.tok b { font-family: var(--mono); font-size: .9rem; font-weight: 600; line-height: 1.3; }
.tok small { font-size: .58rem; font-weight: 700; letter-spacing: .06em; opacity: .85; }
.tok.bad { color: var(--err); border-style: dashed; }
.legend { display: flex; flex-wrap: wrap; gap: .8rem 1.2rem; margin-top: .9rem; font-size: .8rem; color: var(--muted); }
.legend span { display: inline-flex; align-items: center; gap: .4rem; }
.legend i { width: .65rem; height: .65rem; border-radius: 3px; background: currentColor; }

.ast-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
.ast-card { background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-lg); padding: .8rem .9rem 1rem .9rem; box-shadow: var(--shadow); overflow-x: auto; }
.ast-card.wide { grid-column: 1 / -1; }
.ast-card .cap { display: flex; justify-content: space-between; gap: .6rem; font-size: .76rem; color: var(--faint); margin-bottom: .4rem; }
.ast-card .cap code { font-family: var(--mono); color: var(--text); font-size: .8rem; }
img.ast { display: block; margin: 0 auto; max-width: 100%; height: auto; }

.shapes { display: flex; flex-wrap: wrap; gap: 1rem; }
.shape { display: inline-flex; flex-direction: column; align-items: center; gap: .45rem; --cell: 14px; }
.shape .grid { display: grid; gap: 3px; padding: 6px; border-left: 2px solid var(--sc); border-right: 2px solid var(--sc); border-radius: 6px; }
.shape .grid i { width: var(--cell); height: var(--cell); border-radius: 3px; background: color-mix(in srgb, var(--sc) 55%, transparent); }
.shape .cap { font-size: .8rem; color: var(--muted); font-variant-numeric: tabular-nums; white-space: nowrap; }
.shape .cap b { font-family: var(--mono); color: var(--text); margin-right: .25rem; }
.shape .cap .hot { font-weight: 800; padding: 0 .15rem; border-radius: 4px; }
.shape .cap .hot.ok { color: var(--ok); background: color-mix(in srgb, var(--ok) 15%, transparent); }
.shape .cap .hot.bad { color: var(--err); background: color-mix(in srgb, var(--err) 15%, transparent); }
.shape.sym-a { --sc: var(--c-tokens); } .shape.sym-b { --sc: var(--c-tac); } .shape.sym-r { --sc: var(--c-out); } .shape.sym-x { --sc: var(--err); }

.eq-card { background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-lg); padding: 1rem 1.2rem; margin-bottom: .9rem; box-shadow: var(--shadow); }
.eq-card.bad { border-color: color-mix(in srgb, var(--err) 55%, var(--border)); }
.eq-card .head { display: flex; justify-content: space-between; align-items: center; gap: .8rem; margin-bottom: .85rem; }
.eq-card .head code { font-family: var(--mono); font-size: .9rem; color: var(--text); }
.eq-card .head span { font-size: .75rem; color: var(--faint); }
.eq { display: flex; flex-wrap: wrap; align-items: center; gap: 1rem; }
.eq .op { font-family: var(--mono); font-size: 1.35rem; font-weight: 700; color: var(--muted); }
.eq .q { width: 3rem; height: 3rem; border-radius: 10px; border: 2px dashed var(--err); color: var(--err); display: grid; place-items: center; font-weight: 800; font-size: 1.2rem; }
.verdict { margin-top: .85rem; font-size: .87rem; padding: .5rem .75rem; border-radius: var(--r-sm); }
.verdict.ok { color: var(--ok); background: color-mix(in srgb, var(--ok) 11%, transparent); }
.verdict.bad { color: var(--err); background: color-mix(in srgb, var(--err) 11%, transparent); }

.map { border: 1px solid var(--border); border-radius: var(--r-md); background: var(--panel); overflow: hidden; }
.map .r { display: grid; grid-template-columns: minmax(0, 1fr) 2rem minmax(0, 1fr); align-items: center; gap: .4rem; padding: .65rem 1rem; border-bottom: 1px solid var(--border); }
.map .r:last-child { border-bottom: 0; }
.map .src { font-family: var(--mono); font-size: .85rem; color: var(--text); }
.map .src small { color: var(--faint); margin-right: .55rem; font-size: .75rem; }
.map .arr { color: var(--accent); text-align: center; font-weight: 700; }
.map .dst { display: flex; flex-direction: column; gap: .2rem; font-family: var(--mono); font-size: .85rem; color: var(--text); }

/* ===== language guide ===== */
.gram { font-family: var(--mono); font-size: .86rem; line-height: 1.85; color: var(--text); margin: 0; white-space: pre; overflow-x: auto; }
.gram .nt { color: var(--k-id); } .gram .tm { color: var(--k-kw); } .gram .me { color: var(--faint); }
.rulebox { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }

/* ===== test lab ===== */
.tcard { background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-lg); padding: 1.05rem 1.15rem; box-shadow: var(--shadow); height: 100%; }
.tcard .top { display: flex; justify-content: space-between; align-items: center; gap: .6rem; margin-bottom: .45rem; }
.tcard .id { font-family: var(--mono); font-size: .74rem; font-weight: 700; color: var(--faint); }
.tcard h3 { font-size: 1rem; font-weight: 700; margin: 0 0 .25rem 0; color: var(--text); }
.tcard p { font-size: .85rem; color: var(--muted); margin: 0 0 .7rem 0; line-height: 1.5; }
.tcard pre { margin: 0 0 .75rem 0; padding: .6rem .75rem; border-radius: var(--r-sm); background: var(--panel2); font-family: var(--mono);
             font-size: .78rem; line-height: 1.6; color: var(--text); overflow-x: auto; max-height: 9.5rem; }
.tcard .ex { display: grid; grid-template-columns: 4.6rem 1fr; gap: .3rem .6rem; font-size: .82rem; }
.tcard .ex span { color: var(--faint); font-weight: 600; } .tcard .ex b { color: var(--text); font-weight: 500; }
.pill { display: inline-flex; align-items: center; gap: .35rem; font-size: .72rem; font-weight: 800; letter-spacing: .06em;
        padding: .2rem .6rem; border-radius: 999px; }
.pill.pass { color: var(--ok); background: color-mix(in srgb, var(--ok) 14%, transparent); }
.pill.fail { color: var(--err); background: color-mix(in srgb, var(--err) 14%, transparent); }
.scorebar { display: flex; align-items: center; gap: 1.2rem; flex-wrap: wrap; }
.scorebar .big { font-size: 2.6rem; font-weight: 800; letter-spacing: -.03em; line-height: 1; }
.meter { flex: 1; min-width: 180px; height: .6rem; border-radius: 999px; background: var(--panel3); overflow: hidden; }
.meter i { display: block; height: 100%; background: var(--ok); border-radius: 999px; }

/* ===== viva prep ===== */
.quote { position: relative; padding: 1.5rem 1.6rem 1.5rem 1.7rem; border-radius: var(--r-lg); background: var(--panel);
         border: 1px solid var(--border); box-shadow: var(--shadow); font-size: 1.12rem; line-height: 1.65; color: var(--text); }
.quote::before { content: ""; position: absolute; left: 0; top: 1.1rem; bottom: 1.1rem; width: 4px; border-radius: 4px; background: var(--grad); }
.quote b { color: var(--accent); }
.tags { display: flex; flex-wrap: wrap; gap: .35rem; margin-top: .8rem; }
.tags span { font-size: .72rem; font-weight: 600; padding: .18rem .55rem; border-radius: 999px; color: var(--muted); background: var(--panel2); border: 1px solid var(--border); }
details.faq { background: var(--panel); border: 1px solid var(--border); border-radius: var(--r-md); margin-bottom: .55rem; transition: border-color .15s ease-out; }
details.faq[open] { border-color: color-mix(in srgb, var(--accent) 55%, var(--border)); }
details.faq summary { cursor: pointer; list-style: none; padding: .85rem 1.1rem; font-weight: 600; font-size: .94rem; color: var(--text);
                      display: flex; justify-content: space-between; gap: 1rem; }
details.faq summary::-webkit-details-marker { display: none; }
details.faq summary::after { content: "+"; color: var(--accent); font-weight: 700; font-size: 1.1rem; line-height: 1; }
details.faq[open] summary::after { content: "−"; }
details.faq summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: var(--r-md); }
details.faq div { padding: 0 1.1rem 1rem 1.1rem; font-size: .9rem; line-height: 1.6; color: var(--muted); }
.timeline { position: relative; padding-left: 1.6rem; }
.timeline::before { content: ""; position: absolute; left: .45rem; top: .4rem; bottom: .4rem; width: 2px; background: var(--border); }
.timeline .ev { position: relative; margin-bottom: 1.1rem; }
.timeline .ev::before { content: ""; position: absolute; left: -1.42rem; top: .3rem; width: .8rem; height: .8rem; border-radius: 50%;
                        background: var(--panel); border: 2px solid var(--accent); }
.timeline .ev .tm { font-size: .72rem; font-weight: 700; letter-spacing: .08em; color: var(--accent); }
.timeline .ev p { margin: .15rem 0 0 0; font-size: .9rem; line-height: 1.55; color: var(--text); }

/* ===== responsive + motion ===== */
@media (max-width: 960px) {
  .phase-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .phase:nth-child(2)::after { display: none; }
  .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .stats div:nth-child(2) { border-right: 0; } .stats div:nth-child(-n+2) { border-bottom: 1px solid var(--border); }
}
@media (max-width: 640px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 4.4rem; }
  .phase-row { grid-template-columns: 1fr; } .phase::after { display: none; }
  .page-title { font-size: 1.65rem; }
  .map .r { grid-template-columns: 1fr; } .map .arr { text-align: left; }
}
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; } }
</style>
"""


def palette():
    """Current theme colours as a dict, e.g. palette()["accent"] -> "#8f7dff".
    SVG pictures are drawn as images, which cannot read CSS variables, so they use this."""
    text = DARK if st.session_state.get("theme_dark", True) else LIGHT
    return {name: value.strip() for name, value in re.findall(r"--([\w-]+):([^;]+);", text)}


def apply_theme():
    """Inject the stylesheet with the colours of the current theme."""
    palette = DARK if st.session_state.get("theme_dark", True) else LIGHT
    st.html(CSS.replace("/*VARS*/", palette))


def _sync_theme():
    st.session_state.theme_dark = st.session_state.theme_toggle


def theme_toggle():
    """The dark-mode switch. Its value is mirrored into a key no widget owns,
    so it survives moving between pages."""
    st.session_state.theme_toggle = st.session_state.get("theme_dark", True)
    st.toggle("Dark mode", key="theme_toggle", on_change=_sync_theme)
