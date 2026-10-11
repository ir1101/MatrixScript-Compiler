# Bonus: Several operations in one line -> several TAC temporaries
matrix A[2][2] = {1, 2, 3, 4}
matrix B[2][2] = {0, 1, 1, 0}
matrix C[2][2] = {10, 10, 10, 10}
matrix D[2][2]
D = A * B + C
print D
