#!/usr/bin/env python3
"""
Freud
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Freud(Perspective):
    name = "弗洛伊德"
    title = "潜意识与本能冲动"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        hg = a["raw_bazi"].get("hidden_gans", {})
        ss = a["raw_bazi"].get("shishen", {})

        score = 50

        # 本我（id）：藏干=隐藏的欲望
        hidden_count = sum(len(v) if isinstance(v, list) else 1 for v in hg.values())
        if hidden_count >= 4:
            score += 15  # 藏干多=潜意识丰富
        elif hidden_count >= 2:
            score += 8

        # 自我（ego）：日主=显意识
        dm_wx = dm.get("wuxing", "")
        if dm.get("strength") in ("身强", "中和"):
            score += 10

        # 超我（superego）：官杀=道德约束
        if ts.get("官杀", 0) >= 2:
            score += 10  # 道德感重
        if ts.get("印星", 0) >= 2:
            score += 5  # 教化

        # 压抑：冲=内心冲突
        if any("冲" in c for c in a["combinations"]):
            score += 10
        if any("害" in c for c in a["combinations"]):
            score += 5

        # 力比多：水旺=性/创造力
        if wx.get("水", 0) >= 20:
            score += 10

        score = max(10, min(95, score))

        # 防御机制识别
        defenses = []
        if ts.get("印星", 0) >= 2:
            defenses.append("理智化——用思考隔离情感")
        if ts.get("比劫", 0) >= 2:
            defenses.append("投射——把自己不喜欢的特质归因于他人")
        if "七杀" in ss.get("time", ""):
            defenses.append("反向形成——表面的温和掩盖内在的攻击性")
        if wx.get("水", 0) >= 25 and ts.get("食伤", 0) >= 2:
            defenses.append("升华——创造性的出口")

        dimensions = [
            {"name": "潜意识丰富度",
             "score": min(100, 30 + 15 * hidden_count),
             "detail": f"藏干{hidden_count}个——{'内心世界丰富' if hidden_count >= 4 else '潜意识内容一般'}"},
            {"name": "自我力量",
             "score": min(100, 50 + 15 * int(dm.get('strength') in ('身强','中和'))),
             "detail": f"日主{dm.get('strength','?')}——{'自我功能强健' if dm.get('strength') in ('身强','中和') else '自我边界较弱'}"},
            {"name": "压抑程度",
             "score": max(0, 50 - 10 * sum(1 for c in a['combinations'] if '冲' in c)),
             "detail": f"{'有冲=内心冲突需要表达' if any('冲' in c for c in a['combinations']) else '内心相对平静'}"},
            {"name": "升华潜力",
             "score": min(100, 40 + 15 * ts.get("食伤",0) + 10 * (wx.get('水',0) >= 20)),
             "detail": f"{'食伤+水=强大的创造性能量' if ts.get('食伤',0)>=1 and wx.get('水',0)>=20 else '创造力潜力需要释放'}"},
        ]

        insights = []
        if hidden_count >= 4:
            insights.append(f"藏干丰富（{hidden_count}个）——你的潜意识像冰山，海面下远比表面大")
        if defenses:
            insights.append(f"可能的防御机制：{defenses[0]}")
        if "七杀" in ss.get("time", "") and wx.get("水", 0) >= 20:
            insights.append("七杀透干+水旺——力比多能量强大，需要在创造性的活动中释放")

        warnings = []
        if ts.get("官杀", 0) >= 3 and ts.get("食伤", 0) == 0:
            warnings.append("超我过强——道德约束压倒了本能，可能有强迫性人格倾向")

        advice = []
        advice.append("记录梦境——弗洛伊德认为梦是'通往潜意识的皇家大道'")
        if wx.get("水", 0) >= 20 and ts.get("食伤", 0) >= 1:
            advice.append("你的力比多能量适合创造性工作——写作、艺术、研究都可以成为升华的出口")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.6,
            "summary": f"潜意识评分{score}分。{'内心世界丰富' if hidden_count >= 4 else '潜意识相对平静'}。{'有创造性升华通道' if ts.get('食伤',0)>=1 and wx.get('水',0)>=20 else '压抑需要出口'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["弗洛伊德视角更适用于有具体心理困扰的场景"],
            "warnings": warnings or [], "advice": advice,
        }
