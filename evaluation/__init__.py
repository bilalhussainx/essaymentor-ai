"""
Evaluation Module for EssayMentor AI

This module provides tools to:
- Compare essay quality with and without RAG
- Score essays using objective rubrics
- Measure improvement from RAG integration
"""

from evaluation.rag_comparison import RAGEvaluator

__all__ = ['RAGEvaluator']
