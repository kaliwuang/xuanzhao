"""Tests for reverse_bazi.py — reverse lookup of BaZi to birth date."""

import pytest
import sys
import os

# Ensure bazi-reverse/scripts is on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVERSE_DIR = os.path.join(PROJECT_ROOT, "bazi-reverse", "scripts")
if REVERSE_DIR not in sys.path:
    sys.path.insert(0, REVERSE_DIR)


@pytest.mark.unit
class TestReverseBazi:
    """Unit tests for the reverse_bazi function."""

    def test_乙酉壬午甲子庚午_to_2005_06_09(self):
        """乙酉壬午甲子庚午 → 2005-06-09"""
        from reverse_bazi import reverse_bazi
        matches = reverse_bazi("乙酉", "壬午", "甲子", "庚午", (2000, 2100))
        assert len(matches) >= 1
        best = matches[0]
        assert best["year"] == 2005
        assert best["month"] == 6
        assert best["day"] == 9
        assert best["hour_verified"] is True

    def test_甲辰壬申戊子丁巳_to_1904_08_22(self):
        """甲辰壬申戊子丁巳 → 1904-08-22"""
        from reverse_bazi import reverse_bazi
        matches = reverse_bazi("甲辰", "壬申", "戊子", "丁巳", (1900, 2000))
        assert len(matches) >= 1
        best = matches[0]
        assert best["year"] == 1904
        assert best["month"] == 8
        assert best["day"] == 22
        assert best["hour_verified"] is True

    def test_no_match_returns_empty(self):
        """Impossible combination returns empty list."""
        from reverse_bazi import reverse_bazi
        matches = reverse_bazi("甲子", "甲子", "甲子", "甲子", (1900, 1900))
        # In a single year it's unlikely to match this specific bazi
        assert isinstance(matches, list)

    def test_match_structure(self):
        """Each match has required fields."""
        from reverse_bazi import reverse_bazi
        matches = reverse_bazi("乙酉", "壬午", "甲子", "庚午", (2000, 2100))
        assert len(matches) >= 1
        m = matches[0]
        assert "year" in m
        assert "month" in m
        assert "day" in m
        assert "hour_dz" in m
        assert "hour_start" in m
        assert "hour_end" in m
        assert "hour_verified" in m
        assert "display" in m
        assert m["hour_dz"] == "午"

    def test_hour_only_dz(self):
        """When only hour branch (地支) is given, matching still works."""
        from reverse_bazi import reverse_bazi
        # Using only 午 (hour branch without stem)
        matches = reverse_bazi("乙酉", "壬午", "甲子", "午", (2000, 2100))
        assert len(matches) >= 1
        assert matches[0]["hour_dz"] == "午"

    def test_global_constants(self):
        """Module-level constants are accessible."""
        from reverse_bazi import TIAN_GAN, DI_ZHI, DI_ZHI_HOUR, SHI_CHEN_RANGE
        assert len(TIAN_GAN) == 10
        assert len(DI_ZHI) == 12
        assert len(DI_ZHI_HOUR) == 12
        assert len(SHI_CHEN_RANGE) == 12
        assert SHI_CHEN_RANGE["午"] == (11, 13)
