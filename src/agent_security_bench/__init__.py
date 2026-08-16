"""Agent Security Bench — ML coding-agent eval and agent-security receipts."""

from .scoring import BENCH_VERSION, score_security_suite, score_task
from .cli import main

__all__ = ["main", "score_task", "score_security_suite", "__version__"]
__version__ = BENCH_VERSION
