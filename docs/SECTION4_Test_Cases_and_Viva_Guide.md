# Section 4 - Test Cases & Viva Strategy

All four programs are in the `examples/` folder and are also loaded by the buttons in the GUI. Line 1 of each file is a `#` comment (which shows the lexer skipping comments), so the first real statement is on line 2.

---

## Part A - The four foolproof test cases

### Test 1 - Valid declaration and print

`examples/test1_valid_declaration_print.ms`

```
# Test 1: Valid declaration and print
matrix A[2][2] = {1, 2, 3, 4}
print A
```

| Phase | What you will see |
|-------|-------------------|
| Lexer | 20 tokens, e.g. `TOKEN_MATRIX`, `TOKEN_ID(A)`, `TOKEN_LBRACKET`, `TOKEN_NUMBER(2)` ... |
| Parser | OK - one declaration, one print |
| Semantic | `A declared as 2x2`, `A has the right number of values (4)` |
| TAC | `declare A[2][2]` / `A = {1, 2, 3, 4}` / `print A` |
| Output | `[ 1  2 ]` / `[ 3  4 ]` |
| GUI | **GREEN** banner |

**Say:** "This is the simplest valid program. It shows the whole pipeline working end to end."

---

### Test 2 - Valid matrix addition

`examples/test2_valid_addition.ms`

```
# Test 2: Valid matrix addition
matrix A[2][2] = {1, 2, 3, 4}
matrix B[2][2] = {5, 6, 7, 8}
matrix C[2][2]
C = A + B
print C
```

| Phase | What you will see |
|-------|-------------------|
| Lexer | 51 tokens |
| Semantic | `A + B: both are 2x2, so the result is 2x2` and `result 2x2 fits C (2x2)` |
| TAC | `T1 = A + B` then `C = T1` (one operation per line) |
| Output | `[ 6  8 ]` / `[ 10  12 ]` |
| GUI | **GREEN** banner, Print Output tab opens automatically |

**Say:** "The compiler does not add `A + B` directly into `C`. It first puts the result into a temporary `T1`, then copies it. That is exactly what three-address code means: one operation per line."

---

### Test 3 - Invalid dimension mismatch (multiplication)

`examples/test3_dimension_mismatch.ms`

```
# Test 3: Invalid multiplication (A has 3 columns, B has only 2 rows)
matrix A[2][3] = {1, 2, 3, 4, 5, 6}
matrix B[2][2] = {1, 0, 0, 1}
matrix C[2][2]
C = A * B
print C
```

| Phase | What you will see |
|-------|-------------------|
| Lexer | OK |
| Parser | OK (the *shape* of `C = A * B` is perfectly legal) |
| Semantic | **FAILS** at line 5 - this is the demo moment |
| TAC | Skipped (pipeline pill stays grey) |
| GUI | **RED** banner |

Exact error shown (line 5, column 7, pointing at the `*`):

```
Line 5 - Semantic Error
Cannot multiply A (2x3) by B (2x2): A has 3 columns but B has 2 rows.

  5 | C = A * B
    |       ^

How to fix: For A * B, the number of COLUMNS of the left matrix must equal the
number of ROWS of the right matrix. Here the left has 3 columns but the right
has 2 rows. Tip: B * A would be valid (2x2 times 2x3).
```

**Say:** "The parser accepted this line because the grammar only checks shape. The semantic analyzer then looks up A and B in the symbol table, sees `A.cols = 3` but `B.rows = 2`, and stops compilation before any code is generated. In Python this would only crash when the line runs."

---

### Test 4 - Basic lexical error

`examples/test4_lexical_error.ms`

```
# Test 4: Lexical error ($ is not a MatrixScript symbol)
matrix A[2][2] = {1, 2, 3, 4}
matrix B[2][2] = {5, 6, 7, 8}
matrix C[2][2]
C = A $ B
print C
```

| Phase | What you will see |
|-------|-------------------|
| Lexer | **FAILS** - `Unexpected character '$'` at line 5, column 7 (shown as a red row inside the Tokens tab) |
| Parser, Semantic, TAC | Skipped |
| GUI | **RED** banner, Lexer pill red, the other three grey |

**Say:** "The lexer reads one character at a time. `$` does not belong to any token type, so it is reported immediately, and nothing after the lexer is even started."

---

### Bonus programs (optional, if the examiner asks for more)

| File | Shows |
|------|-------|
| `bonus_valid_multiplication.ms` | A 2x3 times 3x2 matrix gives a 2x2 result `[58 64] / [139 154]` |
| `bonus_chained_expression.ms` | `D = A * B + C` produces **two** temporaries: `T1 = A * B`, `T2 = T1 + C`, `D = T2` |

### Automated tests

```
python -m unittest discover -s tests -v
```

41 tests cover the four cases above plus syntax errors, undeclared names, redeclaration, invalid sizes, operator precedence and error recovery.

---

## Part B - How to explain each phase in a viva

### The 20-second summary (memorise this)

> "MatrixScript is a tiny compiler for matrix arithmetic. It reads the program in four steps: the **Lexer** cuts the text into tokens, the **Parser** checks the grammar and builds a tree, the **Semantic Analyzer** checks that the matrix sizes make sense, and the **TAC generator** writes simple one-operation-per-line code. If any step finds a mistake, it stops and shows the line number and the reason."

### Phase 1 - Lexer

* **One sentence:** "I convert text into labelled tokens, like turning the word `matrix` into `TOKEN_MATRIX`."
* **How it works:** a loop looks at one character at a time. Spaces and `#` comments are skipped; letters start a word (keyword or name); digits start a number; `+ * = [ ] { } ,` are single-character tokens; anything else is a lexical error.
* **Show:** the Tokens tab. Point to `C = A + B` becoming `TOKEN_ID TOKEN_ASSIGN TOKEN_ID TOKEN_PLUS TOKEN_ID`.
* **Key words:** *token, lexeme, keyword vs identifier, whitespace skipping, lexical error.*

### Phase 2 - Parser

* **One sentence:** "I check that the tokens follow the grammar, and I build a tree."
* **How it works:** one small method per grammar rule (`parse_declaration`, `parse_assignment`, `parse_print`). Each method calls `expect(...)` for the next token it needs; if the token is wrong, it raises a syntax error such as `Expected ']' but found '2'`.
* **Precedence in one line:** "`parse_expression` handles `+` and calls `parse_term`, which handles `*`, so `*` ends up lower in the tree and is evaluated first."
* **Not deeply recursive:** the repeated parts are `while` loops.
* **Key words:** *grammar, recursive descent, AST, syntax error, error recovery (skip to the next line).*

### Phase 3 - Semantic Analyzer (the important one)

* **One sentence:** "The parser only knows the *shape* of a statement; I check the *meaning*, mainly the matrix dimensions."
* **How it works:** it keeps a **symbol table** (a dictionary from a matrix name to its rows and columns). For `C = A * B` it looks up A and B, checks `A.cols == B.rows`, computes the result size `A.rows x B.cols`, and checks that it equals the declared size of `C`.
* **The two rules:**
  * `A + B` -> same rows and same columns.
  * `A * B` -> columns of A equal rows of B.
* **Show:** Test 3. Go to the Semantic Check tab and point at the red row `A.cols (3) is not equal to B.rows (2)`.
* **Key words:** *symbol table, type/dimension checking, semantic error, compile time vs run time.*

### Phase 4 - TAC Generator

* **One sentence:** "I rewrite each statement as very simple steps where every line does one operation and has at most three names."
* **How it works:** it walks the tree; for every `+` or `*` it makes a new temporary (`T1`, `T2`, ...), and finally copies the last temporary into the target.
* **Show:** the chained example: `D = A * B + C` becomes `T1 = A * B`, `T2 = T1 + C`, `D = T2`. Then open the quadruple table (operator, arg1, arg2, result).
* **Why TAC?** It is easy to optimise and easy to translate to machine code; it is the bridge between the front end and the back end.
* **Key words:** *intermediate code, temporaries, quadruples.*

### The "Print Output" tab

"The compiler stops at TAC, but to prove the TAC is correct I included a tiny interpreter that executes it line by line. It is not a compiler phase; it is only there to show the result."

---

## Part C - Likely viva questions

| Question | Short answer |
|----------|--------------|
| What is a token? | A labelled piece of the source, such as `TOKEN_PLUS` for `+`. |
| Lexical vs syntax vs semantic error? | Lexical: illegal character (`$`). Syntax: wrong order of tokens (`A = + B`). Semantic: right order but wrong meaning (multiplying a 2x3 by a 2x2). |
| Why can't the parser find the dimension error? | The grammar has no memory of matrix sizes; sizes live in the symbol table, which the semantic analyzer builds. |
| What is a symbol table? | A dictionary: name -> information (here rows, cols, line declared). |
| What is an AST? | A tree of the program's structure with the punctuation removed. |
| What parsing technique is used? | Recursive descent, with `while` loops for the repeated parts. |
| How is `*` before `+` handled? | By grammar levels: `expression` handles `+` and calls `term`, which handles `*`. |
| What is three-address code? | Code where each instruction has at most one operator and three addresses, e.g. `T1 = A + B`. |
| Why temporaries? | A statement like `A * B + C` has two operations, so the first result needs a name. |
| Why does the compiler stop after an error? | Later phases need valid input from the earlier phase. |
| Does it report more than one error? | Yes, within a phase: all bad characters, all bad lines, and all bad statements are listed; it just does not start the next phase. |
| Why not use NumPy? | The goal is to show compiler phases and the matrix rules, not to build a fast library. |
| What are the limitations? | Only `+` and `*`, no subtraction, no `A[i][j]` indexing, no loops; matrices are at most 10x10. |
| Future work? | Add `-`, transpose, parentheses, constant folding as an optimisation phase, code generation for a real target. |

---

## Part D - Five-minute demo script

1. **(30 s)** Show the pipeline strip and say the 20-second summary.
2. **(45 s)** Click **1 - Declare & print**: green banner; open Tokens.
3. **(60 s)** Click **2 - Matrix addition**: open Generated TAC; explain `T1 = A + B`, `C = T1`; show the Print Output matrix.
4. **(90 s)** Click **3 - Dimension error**: red banner with line number; open Semantic Check; explain the two rules and the red row. Edit `matrix B[2][2]` to `matrix B[3][2]` with 6 values, compile again, and the banner turns green.
5. **(45 s)** Click **4 - Lexical error**: red banner; Lexer pill red, the other three grey.
6. **(30 s)** Click **Chained TAC** to show two temporaries; toggle the dark/light theme and finish.

> **Tip:** the fix in step 4 is `matrix B[3][2] = {1, 2, 3, 4, 5, 6}`; then `C = A * B` is a valid 2x3 times 3x2 and `C` is 2x2.
