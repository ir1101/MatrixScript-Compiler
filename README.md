# MatrixScript: A Visual Matrix Arithmetic Compiler

A small compiler for matrix arithmetic, written in Python, with a Streamlit dashboard.
Pipeline: **Lexer -> Parser -> Semantic Dimension Check -> Three-Address Code**.

```
C = A * B     ->  tokens  ->  tree  ->  "A.cols = B.rows ?"  ->  T1 = A * B
                                                                 C  = T1
```

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

No Streamlit? The compiler itself needs only Python 3.8+ (no packages):

```bash
python main.py examples/test2_valid_addition.ms
python -m unittest discover -s tests -v
```

## The language in 10 seconds

```
# declare matrices (values are optional, written row by row)
matrix A[2][3] = {1, 2, 3, 4, 5, 6}
matrix B[3][2] = {7, 8, 9, 10, 11, 12}
matrix C[2][2]

C = A * B        # only + and *   ( * is done before + )
print C          # [  58   64 ]
                 # [ 139  154 ]
```

One statement per line. `#` starts a comment. Matrices are at most 10x10.

## Where is everything?

| Project section | Files |
|-----------------|-------|
| **1. Proposal, abstract, architecture diagram** | [docs/SECTION1_Proposal_and_Architecture.md](docs/SECTION1_Proposal_and_Architecture.md) |
| **2. Compiler source code** | [matrixscript/](matrixscript/) (see table below) |
| **3. GUI (multi-page web app)** | [app.py](app.py) (navigation), [views/](views/) (one file per page), [ui/](ui/) (theme + shared drawing code), [assets/](assets/) |
| **4. Test cases + viva guide** | [docs/SECTION4_Test_Cases_and_Viva_Guide.md](docs/SECTION4_Test_Cases_and_Viva_Guide.md), [examples/](examples/), [tests/](tests/) |

### Source modules (read them in this order)

| File | Phase | What it does |
|------|-------|--------------|
| [matrixscript/lexer.py](matrixscript/lexer.py) | 1. Lexer | Text -> tokens |
| [matrixscript/ast_nodes.py](matrixscript/ast_nodes.py) | - | The tree node shapes |
| [matrixscript/parser.py](matrixscript/parser.py) | 2. Parser | Tokens -> tree (grammar check) |
| [matrixscript/semantic.py](matrixscript/semantic.py) | 3. Semantic | Symbol table + dimension checks |
| [matrixscript/tac.py](matrixscript/tac.py) | 4. TAC | Tree -> three-address code |
| [matrixscript/executor.py](matrixscript/executor.py) | (run) | Executes the TAC to produce the print output |
| [matrixscript/compiler.py](matrixscript/compiler.py) | - | Runs the phases in order, stops at the first failing phase |
| [matrixscript/errors.py](matrixscript/errors.py) | - | One friendly error type shared by all phases |
| [main.py](main.py) | - | Command-line runner |

## The web app

Six pages, linked from the top navigation bar:

| Page | What it is for |
|------|----------------|
| **Home** | What MatrixScript is, the four phases, and a live example of an error caught at compile time |
| **Playground** | The editor with one-click examples, the pipeline strip, the green/red result banner, and colour-coded tabs: Tokens, Semantic Check, Generated TAC, Print Output |
| **Step by step** | Walks through the compiler one phase at a time with pictures: token chips, a drawn syntax tree annotated with matrix sizes, `[A] x [B] = [C]` dimension diagrams, and a source-to-TAC map. Each step has a "Say this" line for the viva |
| **Language** | Statements, the two dimension rules as diagrams, the grammar, the token list, and an error gallery whose examples open in the playground |
| **Test lab** | Runs the six demo cases live with PASS/FAIL cards, and runs the full unit-test suite with one click |
| **Viva prep** | The 20-second pitch, one card per phase, likely questions with answers, and a five-minute demo plan |

* Dark and light themes (toggle at the top right of every page).
* Errors show the line, a code snippet with a `^` marker, the reason, and how to fix it.
* The program in the editor is shared between pages, so "Open in playground" and "Current playground program" always mean the same thing.
* Fonts (Inter, JetBrains Mono) come from Google Fonts; without internet the app falls back to system fonts and still works.

| UI file | What it does |
|---------|--------------|
| [ui/theme.py](ui/theme.py) | Colours for both themes and all CSS |
| [ui/components.py](ui/components.py) | Page header, pipeline strip, banners, error cards, the four output tabs |
| [ui/visuals.py](ui/visuals.py) | Token chips, syntax-tree drawing, matrix shape diagrams, TAC mapping |
| [ui/state.py](ui/state.py) | Example list, the shared program, moving between pages |

## Tested with

Python 3.13 and Streamlit 1.65. Every page was checked in a real browser in dark and light themes and at phone width; the compiler has 41 passing unit tests. The top navigation bar needs a recent Streamlit (older versions fall back to sidebar navigation), so 1.50 or newer is recommended.
