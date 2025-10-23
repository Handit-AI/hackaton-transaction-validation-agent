"""
PatternDetector LLM node package
"""

from .processor import PatternDetectorLLMNode
from .prompts import get_prompts

__all__ = [
    "PatternDetectorLLMNode",
    "get_prompts",
]
