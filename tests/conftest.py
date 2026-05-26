"""Shared fixtures for xuanzhao tests."""

import sys
import os
import pytest

# Ensure project root is on sys.path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Add bazi-reverse/scripts for reverse_bazi imports
REVERSE_DIR = os.path.join(PROJECT_ROOT, "bazi-reverse", "scripts")
if os.path.isdir(REVERSE_DIR) and REVERSE_DIR not in sys.path:
    sys.path.insert(0, REVERSE_DIR)


@pytest.fixture(scope="session")
def sample_destiny():
    """Return a full destiny dict for 2005-06-09 11:50 呼和浩特 男."""
    from xuanzhao.analyzer import DestinyAnalyzer
    da = DestinyAnalyzer()
    return da.analyze("2005-06-09 11:50", "呼和浩特", "男")


@pytest.fixture(scope="session")
def sample_destiny_female():
    """Return a full destiny dict for 2001-07-07 11:30 通辽 女."""
    from xuanzhao.analyzer import DestinyAnalyzer
    da = DestinyAnalyzer()
    return da.analyze("2001-07-07 11:30", "通辽", "女")


@pytest.fixture(scope="session")
def deep_engine():
    """Return a DeepPerspectiveEngine instance."""
    from perspectives_engine import DeepPerspectiveEngine
    return DeepPerspectiveEngine()
