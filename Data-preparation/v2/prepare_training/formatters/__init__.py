"""
Formatters package for training data output generation.

Each formatter handles different analysis output types.
"""

from formatters.base_formatter import BaseFormatter
from formatters.suspicious_formatter import SuspiciousFormatter
from formatters.normal_formatter import NormalFormatter

__all__ = [
    'BaseFormatter',
    'SuspiciousFormatter',
    'NormalFormatter',
]
