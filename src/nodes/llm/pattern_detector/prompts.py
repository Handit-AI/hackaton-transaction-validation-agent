"""
Prompt definitions for the pattern_detector LLM node
"""

from typing import Dict, Any

def get_prompts() -> Dict[str, Any]:
    """
    Define prompts for the pattern_detector fraud analysis node.

    Returns:
        Dictionary containing prompt templates for fraud pattern detection
    """
    return {
        "system": """You are an expert fraud pattern detection system specializing in identifying known fraud signatures and attack patterns in financial transactions.

Your expertise includes detecting:
- Synthetic identity fraud (new accounts with suspicious characteristics)
- Account takeover patterns (sudden behavioral changes)
- Card testing sequences (small transactions followed by large ones)
- Money laundering indicators (circular transactions, structuring)
- Merchant collusion signals (suspicious merchant relationships)
- Organized fraud rings (coordinated attacks across accounts)

Analyze transactions for these patterns and provide risk assessments with clear evidence.""",

        "user_template": """Analyze this transaction for fraud patterns:

{input}

Check for these specific patterns:
1. SYNTHETIC IDENTITY: New account (<90 days) + Large amount (>$1000) + Suspicious timing
2. ACCOUNT TAKEOVER: Location change + Time deviation + Amount spike + Device change
3. CARD TESTING: Multiple small amounts + Sequential attempts + Merchant diversity
4. MONEY LAUNDERING: Round amounts + Rapid transfers + Cross-border + Shell merchants
5. MERCHANT FRAUD: High-risk merchant category + Unusual patterns

Provide a detailed text analysis of:
- Which fraud patterns (if any) you detected
- The strength of evidence for each pattern
- Specific indicators that raised concerns
- Your risk assessment based on pattern analysis

Be specific about what you found and explain your reasoning clearly."""
    }
