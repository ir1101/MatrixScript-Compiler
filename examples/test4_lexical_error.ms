# Test 4: Lexical error ($ is not a MatrixScript symbol)
matrix A[2][2] = {1, 2, 3, 4}
matrix B[2][2] = {5, 6, 7, 8}
matrix C[2][2]
C = A $ B
print C
