# Test 3: Invalid multiplication (A has 3 columns, B has only 2 rows)
matrix A[2][3] = {1, 2, 3, 4, 5, 6}
matrix B[2][2] = {1, 0, 0, 1}
matrix C[2][2]
C = A * B
print C
