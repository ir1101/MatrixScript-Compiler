# Section 1 - Academic Proposal & Architecture

## Project Title

**MatrixScript: A Visual Matrix Arithmetic Compiler**

---

## Abstract

Matrix mistakes are usually found too late. In general-purpose languages such as Python or MATLAB, multiplying a 2x3 matrix by a 2x2 matrix is perfectly legal *to write*; the program only crashes when that line actually runs. **MatrixScript** is a small, purpose-built language that does only matrix arithmetic (declaration, `+`, `*`, assignment and `print`). Because the language is so small, the compiler knows the exact size of every matrix before the program runs, so it can check dimensions *at compile time* and report a plain-English error with the line number. The compiler follows the classic four-step pipeline (Lexer, Parser, Semantic Dimension Check, Three-Address Code) and comes with a Streamlit dashboard that shows the result of every phase side by side, making each concept of an introductory compiler course visible on screen.

## Literature Review

A general-purpose language has to support everything (strings, files, objects, loops), so its compiler cannot reason about every matrix shape; tools such as MATLAB and NumPy therefore report a shape mismatch only at run time, when the offending line executes. Libraries that use fixed-size matrices (for example Eigen in C++) can catch some size mismatches during compilation, but they rely on advanced template machinery that is hard for beginners to read. A domain-specific language trades generality for predictability: with only two operators and one data type, the rules for `+` (same size) and `*` (inner sizes match) can be checked by a few lines in the semantic analysis phase. The structure of the compiler follows the standard textbook phases described by Aho, Lam, Sethi and Ullman, which makes MatrixScript a compact, complete example of lexical analysis, parsing, semantic analysis and intermediate code generation.

**References**

1. A. V. Aho, M. S. Lam, R. Sethi, J. D. Ullman, *Compilers: Principles, Techniques, and Tools* (2nd ed.), Pearson, 2006 (the "Dragon Book").
2. NumPy documentation, "Broadcasting" and `numpy.matmul` (shape errors raised at run time) - numpy.org.
3. Eigen documentation, "Matrix and vector arithmetic" (fixed-size matrices) - eigen.tuxfamily.org.

---

## Proposed System

MatrixScript is a **simple linear pipeline**. Each phase takes the output of the previous phase, and the pipeline stops at the first phase that finds an error.

### Architecture diagram

```
                      MATRIXSCRIPT COMPILER PIPELINE

  +---------------+
  | Source code   |   matrix A[2][2] = {1, 2, 3, 4}
  | (text)        |   C = A + B
  +-------+-------+
          |
          v
  +---------------+    turns text into labelled pieces
  | 1. LEXER      |    "C = A + B"  ->  ID  =  ID  +  ID
  +-------+-------+                     (finds illegal characters)
          | list of tokens
          v
  +---------------+    checks the grammar, builds a tree
  | 2. PARSER     |         =
  +-------+-------+        / \
          |               C   +        (finds syntax errors)
          |                  / \
          | AST             A   B
          v
  +---------------+    checks MEANING: are the sizes legal?
  | 3. SEMANTIC   |    A + B  -> same size?   A * B -> A.cols = B.rows?
  |    (dimension |    uses the SYMBOL TABLE   A:2x2  B:2x2  C:2x2
  |     check)    |    (finds dimension errors)
  +-------+-------+
          | checked AST
          v
  +---------------+    one operation per line
  | 4. TAC        |    T1 = A + B
  |    GENERATOR  |    C  = T1
  +-------+-------+
          | three-address code
          v
  +---------------+
  | Run TAC       |    prints the result matrices
  | (output)      |    [ 6  8 ]
  +---------------+    [10 12 ]

  Any phase may stop the pipeline with a friendly error message
  (phase name + line number + reason + how to fix it).
```

### What each phase receives and produces

| # | Phase | Input | Output | Errors it finds |
|---|-------|-------|--------|-----------------|
| 1 | Lexer (`lexer.py`) | Source text | List of tokens | Illegal characters, malformed names like `2A` |
| 2 | Parser (`parser.py`) | Tokens | AST (tree of statements) | Missing `]`, missing operand, two statements on a line |
| 3 | Semantic Analyzer (`semantic.py`) | AST | Symbol table + check log | Undeclared name, wrong value count, **dimension mismatch** |
| 4 | TAC Generator (`tac.py`) | Checked AST | Three-address code | none (input is already valid) |

### The MatrixScript language

```
program      ->  statement*
statement    ->  declaration | assignment | print
declaration  ->  'matrix' ID '[' NUMBER ']' '[' NUMBER ']'
                   [ '=' '{' NUMBER (',' NUMBER)* '}' ]
assignment   ->  ID '=' expression
print        ->  'print' ID
expression   ->  term ( '+' term )*
term         ->  ID ( '*' ID )*
```

* One statement per line; `#` starts a comment.
* Only two operators: `+` (addition) and `*` (matrix multiplication). `*` is evaluated before `+`.
* Initial values are written row by row. A matrix declared without values is filled with zeros.

### Token set (the Lexer's vocabulary)

| Token | Examples | Token | Examples |
|-------|----------|-------|----------|
| `TOKEN_MATRIX` | `matrix` | `TOKEN_PLUS` | `+` |
| `TOKEN_PRINT` | `print` | `TOKEN_STAR` | `*` |
| `TOKEN_ID` | `A`, `result` | `TOKEN_ASSIGN` | `=` |
| `TOKEN_NUMBER` | `2`, `-3`, `4.5` | `TOKEN_LBRACKET` / `RBRACKET` | `[` `]` |
| `TOKEN_COMMA` | `,` | `TOKEN_LBRACE` / `RBRACE` | `{` `}` |
| `TOKEN_EOF` | (end of input) | | |

### The two dimension rules (the heart of the project)

| Operation | Condition | Result size |
|-----------|-----------|-------------|
| `A + B` | `A.rows == B.rows` **and** `A.cols == B.cols` | same as A |
| `A * B` | `A.cols == B.rows` | `A.rows x B.cols` |
| `C = ...` | result size equals the declared size of `C` | - |

### Worked example (one line, all four phases)

Source: `D = A * B + C`

| Phase | Result |
|-------|--------|
| Lexer | `ID(D) ASSIGN ID(A) STAR ID(B) PLUS ID(C)` |
| Parser | `D = ( (A * B) + C )` as a tree - the `*` is lower in the tree, so it is done first |
| Semantic | `A*B`: A.cols = B.rows? yes -> 2x2. `(A*B)+C`: both 2x2? yes. Result 2x2 fits `D`? yes |
| TAC | `T1 = A * B` , `T2 = T1 + C` , `D = T2` |

### Technology choices

| Choice | Reason |
|--------|--------|
| Python 3 | Readable, no compiler-construction library needed - every phase is hand-written |
| Plain lists for matrices | No NumPy, so the arithmetic is visible in a few lines |
| Streamlit | A web dashboard written in Python, so the demo needs no separate front-end code |
