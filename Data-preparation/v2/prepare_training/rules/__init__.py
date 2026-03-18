"""
Rules package for log analysis patterns.

Contains pattern definitions for suspicious and normal behaviors.
"""

import rules.suspicious_patterns as suspicious_patterns
import rules.normal_patterns as normal_patterns

__all__ = ['suspicious_patterns', 'normal_patterns']
