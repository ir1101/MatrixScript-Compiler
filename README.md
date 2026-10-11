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
| **3. GUI dashboard** | [app.py](app.py), [.streamlit/config.toml](.streamlit/config.toml) |
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

## GUI features

* **Input editor** (left) with one-click example programs.
* **Compiled output** (right) with colour-coded tabs: Tokens, Semantic Check, Generated TAC, Print Output.
* **Pipeline strip** showing which phase passed (green), failed (red) or was skipped (grey).
* **Green SUCCESS banner / red FAILED banner** with the line number, a code snippet with a `^` marker, the reason, and how to fix it.
* **Dark / light theme** toggle.
* The tab that explains the result opens automatically (Print Output on success, Semantic Check on a dimension error).

## Tested with

Python 3.13 and Streamlit 1.65 (the GUI was checked in a real browser in dark and light themes; the compiler has 41 passing unit tests). Streamlit 1.40 or newer is recommended.
