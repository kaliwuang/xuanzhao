"""Tests for BaziEngine and DestinyAnalyzer."""

import pytest
from xuanzhao.analyzer import BaziEngine, DestinyAnalyzer


@pytest.mark.unit
class TestBaziEngine:
    """Unit tests for BaziEngine.analyze()."""

    def test_known_case_male(self):
        """2005-06-09 11:50 呼和浩特 男 → 乙酉 壬午 甲子 庚午"""
        engine = BaziEngine()
        result = engine.analyze(2005, 6, 9, 11, 50, 1)
        bazi = result["bazi"]
        assert bazi["year"] == "乙酉"
        assert bazi["month"] == "壬午"
        assert bazi["day"] == "甲子"
        assert bazi["time"] == "庚午"

    def test_known_case_female(self):
        """2001-07-07 11:30 通辽 女 → 辛巳 乙未 辛未 甲午"""
        engine = BaziEngine()
        result = engine.analyze(2001, 7, 7, 11, 30, 0)
        bazi = result["bazi"]
        assert bazi["year"] == "辛巳"
        assert bazi["month"] == "乙未"
        assert bazi["day"] == "辛未"
        assert bazi["time"] == "甲午"

    def test_output_structure(self):
        """Result dict has expected keys."""
        engine = BaziEngine()
        result = engine.analyze(2005, 6, 9, 11, 50, 1)
        assert "bazi" in result
        assert "nayin" in result
        assert "hidden_gans" in result
        assert "shishen" in result
        assert "xunkong" in result
        assert "minggong" in result
        assert "taiyuan" in result
        assert "shengong" in result
        assert "day_master" in result
        assert "dayun" in result

    def test_day_master_fields(self):
        """day_master contains gan and wuxing."""
        engine = BaziEngine()
        result = engine.analyze(2005, 6, 9, 11, 50, 1)
        dm = result["day_master"]
        assert "gan" in dm
        assert "wuxing" in dm
        assert dm["gan"] == "甲"
        assert dm["wuxing"] == "木"

    def test_dayun_is_list(self):
        """dayun is a list of decade-long luck cycles."""
        engine = BaziEngine()
        result = engine.analyze(2005, 6, 9, 11, 50, 1)
        assert isinstance(result["dayun"], list)
        if result["dayun"]:
            d = result["dayun"][0]
            assert "start" in d
            assert "end" in d
            assert "ganzhi" in d
            assert d["end"] == d["start"] + 9


@pytest.mark.integration
class TestDestinyAnalyzer:
    """Integration tests for DestinyAnalyzer."""

    def test_analyze_male(self, sample_destiny):
        """Full DestinyAnalyzer output for male case."""
        d = sample_destiny
        assert "bazi" in d
        assert "features" in d
        assert "tiaohou" in d

        ba = d["bazi"]["bazi"]
        assert ba["year"] == "乙酉"
        assert ba["month"] == "壬午"
        assert ba["day"] == "甲子"
        assert ba["time"] == "庚午"

    def test_analyze_female(self, sample_destiny_female):
        """Full DestinyAnalyzer output for female case."""
        d = sample_destiny_female
        assert "bazi" in d
        assert "features" in d
        assert "tiaohou" in d

        ba = d["bazi"]["bazi"]
        assert ba["year"] == "辛巳"
        assert ba["month"] == "乙未"
        assert ba["day"] == "辛未"
        assert ba["time"] == "甲午"

    def test_features_is_list(self, sample_destiny):
        """features key contains a list."""
        assert isinstance(sample_destiny["features"], list)

    def test_tiaohou_has_fields(self, sample_destiny):
        """tiaohou has day_gan, month_zhi, yongshen."""
        th = sample_destiny["tiaohou"]
        assert "day_gan" in th
        assert "month_zhi" in th
        assert "yongshen" in th

    def test_birth_info(self, sample_destiny):
        """Birth metadata is preserved."""
        d = sample_destiny
        assert d["birth"] == "2005-06-09 11:50"
        assert d["location"] == "呼和浩特"
        assert d["gender"] == "男"
