"""MatrixScript - a tiny visual compiler for matrix arithmetic."""

from .compiler import compile_source, CompilationResult, PHASES

__all__ = ["compile_source", "CompilationResult", "PHASES"]
