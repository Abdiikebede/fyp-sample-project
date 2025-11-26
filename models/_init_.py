# This file makes the models directory a Python package
from .embedder import PlagiarismEmbedder
from .vector_db import VectorDatabase
from .decision_engine import DecisionEngine
from .report_generator import ReportGenerator

__all__ = [
    'PlagiarismEmbedder',
    'VectorDatabase', 
    'DecisionEngine',
    'ReportGenerator'
]