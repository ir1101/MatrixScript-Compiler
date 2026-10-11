"""
Automated tests for the MatrixScript compiler.

Run them from the project folder with:

    python -m unittest discover -s tests -v

The first four tests are the four demo programs from the viva guide.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from matrixscript import compile_source                      # noqa: E402
from matrixscript.compiler import STATUS_FAILED, STATUS_OK, STATUS_SKIPPED  # noqa: E402
from matrixscript.errors import PHASE_LEXER, PHASE_PARSER, PHASE_SEMANTIC   # noqa: E402

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


def load_example(name):
    with open(os.path.join(EXAMPLES, name), encoding="utf-8") as f:
        return f.read()


def tac_text(result):
    return [str(ins) for ins in result.tac]


class TestFourRequiredCases(unittest.TestCase):
    """The four programs you demonstrate in the viva."""

    def test1_valid_declaration_and_print(self):
        r = compile_source(load_example("test1_valid_declaration_print.ms"))
        self.assertTrue(r.success)
        self.assertEqual(r.output[0].matrix, [[1, 2], [3, 4]])
        self.assertEqual(tac_text(r), ["declare A[2][2]", "A = {1, 2, 3, 4}", "print A"])

    def test2_valid_addition(self):
        r = compile_source(load_example("test2_valid_addition.ms"))
        self.assertTrue(r.success)
        self.assertEqual(r.output[0].matrix, [[6, 8], [10, 12]])
        self.assertIn("T1 = A + B", tac_text(r))
        self.assertIn("C = T1", tac_text(r))

    def test3_dimension_mismatch_in_multiplication(self):
        r = compile_source(load_example("test3_dimension_mismatch.ms"))
        self.assertFalse(r.success)
        self.assertEqual(r.failed_phase, PHASE_SEMANTIC)
        self.assertEqual(len(r.errors), 1)
        self.assertEqual(r.errors[0].line, 5)
        self.assertIn("Cannot multiply A (2x3) by B (2x2)", r.errors[0].message)
        self.assertEqual(r.tac, [])                       # no code for a bad program
        self.assertEqual(r.status["TAC Generator"], STATUS_SKIPPED)

    def test4_lexical_error(self):
        r = compile_source(load_example("test4_lexical_error.ms"))
        self.assertFalse(r.success)
        self.assertEqual(r.failed_phase, PHASE_LEXER)
        self.assertEqual(r.errors[0].line, 5)
        self.assertEqual(r.errors[0].column, 7)
        self.assertIn("Unexpected character '$'", r.errors[0].message)
        self.assertEqual(r.status["Parser"], STATUS_SKIPPED)


class TestValidPrograms(unittest.TestCase):
    def test_multiplication_of_non_square_matrices(self):
        r = compile_source(load_example("bonus_valid_multiplication.ms"))
        self.assertTrue(r.success)
        self.assertEqual(r.output[0].matrix, [[58, 64], [139, 154]])

    def test_chain_makes_one_temporary_per_operation(self):
        r = compile_source(load_example("bonus_chained_expression.ms"))
        self.assertTrue(r.success)
        self.assertEqual(r.output[0].matrix, [[12, 11], [14, 13]])
        self.assertEqual(tac_text(r)[-4:], ["T1 = A * B", "T2 = T1 + C", "D = T2", "print D"])

    def test_multiplication_binds_tighter_than_addition(self):
        src = ("matrix A[2][2]\nmatrix B[2][2]\nmatrix C[2][2]\nmatrix D[2][2]\n"
               "D = A + B * C\n")
        r = compile_source(src)
        self.assertTrue(r.success)
        self.assertEqual(tac_text(r)[-3:], ["T1 = B * C", "T2 = A + T1", "D = T2"])

    def test_plain_copy_has_no_temporary(self):
        r = compile_source("matrix A[1][2] = {1, 2}\nmatrix B[1][2]\nB = A\nprint B\n")
        self.assertTrue(r.success)
        self.assertIn("B = A", tac_text(r))
        self.assertEqual(r.output[0].matrix, [[1, 2]])

    def test_copy_is_independent_of_the_source_matrix(self):
        r = compile_source("matrix A[1][1] = {5}\nmatrix B[1][1]\nB = A\nprint B\nprint A\n")
        self.assertEqual([o.matrix for o in r.output], [[[5]], [[5]]])

    def test_negative_and_decimal_numbers(self):
        r = compile_source("matrix A[1][3] = {-1, 2.5, 3}\nprint A\n")
        self.assertTrue(r.success)
        self.assertEqual(r.output[0].matrix, [[-1, 2.5, 3]])

    def test_comments_blank_lines_and_empty_program(self):
        self.assertTrue(compile_source("").success)
        self.assertTrue(compile_source("# only a comment\n\n   \n").success)
        r = compile_source("# note\nmatrix A[1][1] = {1}  # trailing\nprint A\n")
        self.assertTrue(r.success)

    def test_uninitialised_matrix_is_all_zeros(self):
        r = compile_source("matrix Z[2][2]\nprint Z\n")
        self.assertEqual(r.output[0].matrix, [[0, 0], [0, 0]])

    def test_vector_times_vector_shapes(self):
        # (1x3) * (3x1) = 1x1
        src = ("matrix R[1][3] = {1, 2, 3}\nmatrix K[3][1] = {4, 5, 6}\n"
               "matrix S[1][1]\nS = R * K\nprint S\n")
        r = compile_source(src)
        self.assertTrue(r.success)
        self.assertEqual(r.output[0].matrix, [[32]])


class TestLexicalErrors(unittest.TestCase):
    def test_all_bad_characters_are_reported(self):
        r = compile_source("matrix A[2][2]\nA = A @ A $ A\n")
        self.assertEqual(len(r.errors), 2)
        self.assertEqual([e.line for e in r.errors], [2, 2])

    def test_minus_gets_a_special_hint(self):
        r = compile_source("matrix A[1][1]\nA = A - A\n")
        self.assertIn("no subtraction", r.errors[0].hint)

    def test_name_cannot_start_with_a_digit(self):
        r = compile_source("matrix 2A[2][2]\n")
        self.assertEqual(r.failed_phase, PHASE_LEXER)
        self.assertIn("'2A'", r.errors[0].message)

    def test_non_ascii_digits_and_letters_do_not_crash(self):
        r = compile_source("matrix A[²][2]\nprint é\n")
        self.assertEqual(r.failed_phase, PHASE_LEXER)

    def test_keywords_are_case_sensitive(self):
        r = compile_source("Matrix A[2][2]\n")
        self.assertFalse(r.success)


class TestSyntaxErrors(unittest.TestCase):
    def assert_parser_error(self, src, fragment, line):
        r = compile_source(src)
        self.assertEqual(r.failed_phase, PHASE_PARSER, src)
        self.assertEqual(r.errors[0].line, line, src)
        self.assertIn(fragment, r.errors[0].message, src)

    def test_missing_bracket(self):
        self.assert_parser_error("matrix A[2 2]\n", "Expected ']'", 1)

    def test_missing_operand(self):
        self.assert_parser_error("matrix A[2][2]\nA = A +\n", "Expected a matrix name", 3)

    def test_missing_equals(self):
        self.assert_parser_error("matrix A[2][2]\nA A\n", "Expected '=' after 'A'", 2)

    def test_two_statements_on_one_line(self):
        self.assert_parser_error("matrix A[1][1] print A\n", "Unexpected 'print'", 1)

    def test_statement_starting_with_a_number(self):
        self.assert_parser_error("5 = 5\n", "cannot start with '5'", 1)

    def test_unclosed_value_list(self):
        self.assert_parser_error("matrix A[1][2] = {1, 2\nprint A\n", "Expected '}' or ','", 2)

    def test_parser_recovers_and_reports_each_bad_line(self):
        r = compile_source("matrix A[2 2]\nmatrix B[2][2]\nB = B +\nprint B\n")
        self.assertEqual([e.line for e in r.errors], [1, 4])


class TestSemanticErrors(unittest.TestCase):
    def one_error(self, src):
        r = compile_source(src)
        self.assertEqual(r.failed_phase, PHASE_SEMANTIC, src)
        self.assertEqual(len(r.errors), 1, [str(e) for e in r.errors])
        return r.errors[0]

    def test_addition_with_different_sizes(self):
        e = self.one_error("matrix A[2][2]\nmatrix B[2][3]\nmatrix C[2][2]\nC = A + B\n")
        self.assertIn("Cannot add A (2x2) and B (2x3)", e.message)
        self.assertEqual(e.line, 4)

    def test_result_does_not_fit_target(self):
        e = self.one_error("matrix A[2][3]\nmatrix B[3][2]\nmatrix C[3][3]\nC = A * B\n")
        self.assertIn("Cannot store a 2x2 result in 'C'", e.message)

    def test_undeclared_matrix_on_right_side(self):
        e = self.one_error("matrix A[2][2]\nmatrix C[2][2]\nC = A + Q\n")
        self.assertIn("Matrix 'Q' is used here, but it was never declared", e.message)

    def test_undeclared_target(self):
        e = self.one_error("matrix A[2][2]\nC = A\n")
        self.assertIn("'C'", e.message)

    def test_print_of_undeclared_matrix(self):
        e = self.one_error("print Q\n")
        self.assertIn("never declared", e.message)

    def test_use_before_declaration(self):
        e = self.one_error("print A\nmatrix A[1][1]\n")
        self.assertEqual(e.line, 1)

    def test_redeclaration(self):
        e = self.one_error("matrix A[2][2]\nmatrix A[3][3]\n")
        self.assertIn("already declared on line 1", e.message)

    def test_wrong_number_of_initial_values(self):
        e = self.one_error("matrix A[2][2] = {1, 2, 3}\n")
        self.assertIn("needs exactly 4 values, but 3 were given", e.message)

    def test_invalid_sizes(self):
        for size in ("[0][2]", "[2][0]", "[2.5][2]", "[-1][2]", "[11][2]"):
            e = self.one_error(f"matrix A{size}\n")
            self.assertIn("invalid size", e.message, size)

    def test_error_in_chain_is_found_in_the_right_operator(self):
        src = ("matrix A[2][3]\nmatrix B[2][2]\nmatrix C[2][2]\nmatrix D[2][2]\n"
               "D = A * B + C\n")
        e = self.one_error(src)
        self.assertIn("Cannot multiply A (2x3) by B (2x2)", e.message)

    def test_error_names_a_sub_expression(self):
        src = ("matrix A[2][2]\nmatrix B[2][2]\nmatrix C[3][3]\nmatrix D[2][2]\n"
               "D = A * B + C\n")
        e = self.one_error(src)
        self.assertIn("Cannot add (A * B) (2x2) and C (3x3)", e.message)

    def test_every_bad_statement_is_reported(self):
        r = compile_source("matrix A[2][3]\nmatrix B[2][2]\nmatrix C[2][2]\n"
                           "C = A * B\nC = A + B\n")
        self.assertEqual([e.line for e in r.errors], [4, 5])

    def test_multiplication_hint_suggests_swapping_when_it_helps(self):
        e = self.one_error("matrix A[2][3]\nmatrix B[2][2]\nmatrix C[2][2]\nC = A * B\n")
        self.assertIn("B * A would be valid", e.hint)

    def test_semantic_log_marks_the_failing_check(self):
        r = compile_source(load_example("test3_dimension_mismatch.ms"))
        failing = [c for c in r.checks if not c.ok]
        self.assertEqual(len(failing), 1)
        self.assertEqual(failing[0].line, 5)


class TestPipelineStatus(unittest.TestCase):
    def test_status_of_a_good_program(self):
        r = compile_source("matrix A[1][1]\n")
        self.assertEqual(set(r.status.values()), {STATUS_OK})

    def test_phases_after_a_failure_are_skipped(self):
        r = compile_source("matrix A[2 2]\n")
        self.assertEqual(r.status["Lexer"], STATUS_OK)
        self.assertEqual(r.status["Parser"], STATUS_FAILED)
        self.assertEqual(r.status["Semantic Analyzer"], STATUS_SKIPPED)
        self.assertEqual(r.status["TAC Generator"], STATUS_SKIPPED)


if __name__ == "__main__":
    unittest.main()
