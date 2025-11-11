"""
Models module for embeddings and LLMs
Provides abstraction layer for model interchangeability
"""
from backend.models.embeddings.registry import EmbeddingRegistry
from backend.models.llm.registry import LLMRegistry

__all__ = ["EmbeddingRegistry", "LLMRegistry"]
