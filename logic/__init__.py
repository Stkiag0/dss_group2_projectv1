"""
Logic module for Student DSS
Contains both experta rules and traditional rule functions
"""

from .decision_rules import (
    compute_total_risk,
    classify_risk,
    recommend_intervention
)

from .experta_rules import evaluate_risk

__all__ = [
    'compute_total_risk',
    'classify_risk', 
    'recommend_intervention',
    'evaluate_risk'
]