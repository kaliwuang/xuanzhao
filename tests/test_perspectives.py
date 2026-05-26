"""Tests for DeepPerspectiveEngine and PerspectiveEngine."""

import pytest


@pytest.mark.unit
class TestDeepPerspectiveEngine:
    """Unit tests for DeepPerspectiveEngine."""

    def test_loads_96_plus_frameworks(self, deep_engine):
        """DeepPerspectiveEngine loads 96+ frameworks."""
        frameworks = deep_engine.list()
        assert len(frameworks) >= 96

    def test_list_structure(self, deep_engine):
        """list() returns entries with id, name, title."""
        frameworks = deep_engine.list()
        for fw in frameworks:
            assert "id" in fw
            assert "name" in fw
            assert "title" in fw

    def test_known_frameworks_present(self, deep_engine):
        """Specific known perspectives are present."""
        ids = {fw["id"] for fw in deep_engine.list()}
        for expected in ["zhuge-liang", "feynman", "jung", "laozi", "sun-tzu"]:
            assert expected in ids, f"Missing perspective: {expected}"


@pytest.mark.integration
class TestDeepPerspectiveAnalysis:
    """Tests for perspective analysis on real destiny data."""

    PERSPECTIVE_KEYS = {
        "score", "confidence", "summary", "dimensions",
        "key_insights", "warnings", "advice", "monologue",
        "perspective", "title", "id",
    }

    def test_analyze_single_perspective(self, deep_engine, sample_destiny):
        """Analyzing a single perspective returns correct structure."""
        result = deep_engine.analyze(sample_destiny, ["zhuge-liang"])
        assert "zhuge-liang" in result
        data = result["zhuge-liang"]

        # Check required fields
        assert isinstance(data["score"], (int, float))
        assert 0 <= data["score"] <= 100
        assert isinstance(data["confidence"], (int, float))
        assert 0 <= data["confidence"] <= 1
        assert isinstance(data["summary"], str) and data["summary"]
        assert isinstance(data["dimensions"], list)
        assert len(data["dimensions"]) > 0

    def test_dimension_structure(self, deep_engine, sample_destiny):
        """Each dimension has name, score, detail."""
        result = deep_engine.analyze(sample_destiny, ["zhuge-liang"])
        for dim in result["zhuge-liang"]["dimensions"]:
            assert "name" in dim
            assert "score" in dim
            assert "detail" in dim

    def test_multiple_perspectives(self, deep_engine, sample_destiny):
        """Requested subset of perspectives is returned."""
        ids = ["zhuge-liang", "feynman", "laozi"]
        result = deep_engine.analyze(sample_destiny, ids)
        assert set(result.keys()) == set(ids)

    def test_all_perspectives_required_fields(self, deep_engine, sample_destiny):
        """All perspective results have required fields."""
        # Limit to first 5 for speed
        all_ids = [fw["id"] for fw in deep_engine.list()[:5]]
        result = deep_engine.analyze(sample_destiny, all_ids)
        for pid, data in result.items():
            for key in self.PERSPECTIVE_KEYS:
                assert key in data, f"{pid} missing key: {key}"

    def test_error_handling_invalid_id(self, deep_engine, sample_destiny):
        """Invalid perspective IDs are silently ignored."""
        result = deep_engine.analyze(sample_destiny, ["non-existent-id"])
        assert result == {}

    def test_analyze_missing_bazi(self, deep_engine):
        """Analyzing data without bazi returns error result gracefully."""
        result = deep_engine.analyze({"foo": "bar"}, ["zhuge-liang"])
        if "zhuge-liang" in result:
            data = result["zhuge-liang"]
            assert isinstance(data["score"], (int, float))
            assert isinstance(data["summary"], str)
