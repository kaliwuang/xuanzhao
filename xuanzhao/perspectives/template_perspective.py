#!/usr/bin/env python3
"""
TemplatePerspective
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)
from perspectives_templates import TEMPLATE_PERSPECTIVES

class TemplatePerspective(Perspective):
    """基于模板数据的参数化视角"""

    def __init__(self, pid: str, config: dict):
        self._pid = pid
        self._cfg = config

    @property
    def name(self) -> str:
        return self._cfg["name"]

    @property
    def title(self) -> str:
        return self._cfg["title"]

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        dayun = a["dayun_phase"]
        combos = a["combinations"]
        th = a["tiaohou"]
        c = self._cfg

        score = 50
        for comp in c.get("score_components", []):
            val = self._get_nested(a, comp[0])
            score += val * comp[1]
        if dayun and c.get("boost_dayun"):
            d_wx = dayun.get("gan_wuxing", "")
            dm_wx = dm.get("wuxing", "")
            if d_wx == dm_wx:
                score += 8
            elif d_wx in _WUXING_CYCLE.get(dm_wx, ""):
                score += 5
        if th.get("yongshen") and c.get("boost_yongshen"):
            ys = _GAN_WUXING.get(th["yongshen"][0] if th["yongshen"] else "", "")
            if ys and wx.get(ys, 0) > 20:
                score += 8
        if any("冲" in c2 for c2 in combos) and c.get("boost_chong"):
            score += 8
        if any("合" in c2 for c2 in combos) and c.get("boost_he"):
            score += 8

        score = max(10, min(95, int(score)))

        dimensions = []
        for dim in c.get("dimensions", []):
            dim_score = 50
            for comp in dim.get("components", []):
                dim_score += self._get_nested(a, comp[0]) * comp[1]
            dim_score = max(10, min(100, int(dim_score)))
            dimensions.append({
                "name": dim["name"],
                "score": dim_score,
                "detail": dim.get("high_detail", "").format(**self._fmt(a)) if dim_score >= 60
                          else dim.get("low_detail", "").format(**self._fmt(a))
            })

        insights = []
        insight_key = "high" if score >= 65 else "mid" if score >= 45 else "low"
        insight_templates = c.get("insights", {}).get(insight_key, [])
        if isinstance(insight_templates, str):
            insight_templates = [insight_templates]
        for tpl in insight_templates[:2]:
            try:
                insights.append(tpl.format(**self._fmt(a)))
            except (KeyError, ValueError):
                insights.append(tpl)

        warnings = []
        for warn in c.get("warnings", []):
            field = warn.get("field", "")
            threshold = warn.get("threshold", 20)
            val = self._get_nested(a, field)
            if val < threshold:
                msg = warn.get("msg", "").format(**self._fmt(a))
                warnings.append(msg)

        advice = []
        for adv_tpl in c.get("advice", []):
            try:
                advice.append(adv_tpl.format(**self._fmt(a)))
            except (KeyError, ValueError):
                advice.append(adv_tpl)

        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": c.get("confidence", 0.55),
            "summary": c.get("summary_high", "").format(**self._fmt(a)) if score >= 60
                       else c.get("summary_low", "").format(**self._fmt(a)),
            "dimensions": dimensions[:4],
            "key_insights": insights[:3],
            "warnings": warnings[:2],
            "advice": advice[:2],
        }

    def _get_nested(self, d: dict, path: str):
        parts = path.split(".")
        val = d
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p, 50)
            else:
                return 50
        if isinstance(val, (int, float)):
            return val
        return 50 if val else 0

    def _fmt(self, a: dict) -> dict:
        wx = a["wuxing"]
        ts = a["tenshen"]
        dm = a["daymaster"]
        th = a["tiaohou"]
        dayun = a["dayun_phase"]
        return {
            "日主": dm.get("wuxing", "?"),
            "强弱": dm.get("strength", "中"),
            "用神": th.get("yongshen", "?"),
            "印星": ts.get("印星", 0),
            "比劫": ts.get("比劫", 0),
            "食伤": ts.get("食伤", 0),
            "财星": ts.get("财星", 0),
            "官杀": ts.get("官杀", 0),
            "木": wx.get("木", 0),
            "火": wx.get("火", 0),
            "土": wx.get("土", 0),
            "金": wx.get("金", 0),
            "水": wx.get("水", 0),
            "大运": dayun.get("ganzhi", "?"),
            "大运年": dayun.get("year_index", 1),
        }

# 生成模板视角
def _load_template_perspectives():
    result = {}
    for pid, cfg in TEMPLATE_PERSPECTIVES.items():
        result[pid] = TemplatePerspective(pid, cfg)
    return result

TEMPLATE_FRAMEWORKS = _load_template_perspectives()

