"""
BehavioralAnalizer LLM node package
"""

from .processor import BehavioralAnalizerLLMNode
from .prompts import get_prompts

__all__ = [
    "BehavioralAnalizerLLMNode",
    "get_prompts",
]
