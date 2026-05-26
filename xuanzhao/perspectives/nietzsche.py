#!/usr/bin/env python3
"""
Nietzsche
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Nietzsche(Perspective):
    name = "尼采"
    title = "权力意志重估一切"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        combos = a["combinations"]
        ss = a["raw_bazi"].get("shishen", {})

        score = 50

        # 权力意志：七杀=斗志
        if "七杀" in ss.get("time", ""):
            score += 20
        elif "七杀" in ss.get("month", ""):
            score += 15
        if ts.get("官杀", 0) >= 2:
            score += 5

        # 创造与毁灭：食伤=创造，官杀=破坏
        if ts.get("食伤", 0) >= 2:
            score += 10
        if ts.get("官杀", 0) >= 2:
            score += 5

        # 重估一切：冲=打破旧秩序
        if any("冲" in c for c in combos):
            score += 10
        if any("害" in c for c in combos):
            score += 5

        # 超人倾向：比劫=独立，印星=自我超越
        if ts.get("比劫", 0) >= 1:
            score += 5
        if ts.get("印星", 0) >= 2:
            score += 5

        # 酒神精神：食伤+水=迷狂创造力
        if ts.get("食伤", 0) >= 1 and wx.get("水", 0) >= 20:
            score += 10

        score = max(10, min(95, score))

        # 超人评语
        if score >= 75:
            ubermensch = "超人潜力——不以常人的标准衡量自己"
        elif score >= 50:
            ubermensch = "凡人之上——有超越的欲望但还不够彻底"
        else:
            ubermensch = "骆驼阶段——还需要先背负传统才能成为狮子"

        dimensions = [
            {"name": "权力意志",
             "score": min(100, 40 + 20 * int("七杀" in ss.get("time","") or "七杀" in ss.get("month",""))),
             "detail": f"{'七杀透干=强大的权力意志' if '七杀' in ss.get('time','') or '七杀' in ss.get('month','') else '权力意志需激发'}"},
            {"name": "日神与酒神",
             "score": min(100, 40 + 15 * ts.get("食伤",0) + 10 * (wx.get('水',0) >= 20)),
             "detail": f"{'酒神精神占优——直觉和创造力是主要力量' if ts.get('食伤',0)>=1 and wx.get('水',0)>=20 else '日神精神为主——理性和秩序是安全感来源'}"},
            {"name": "超越等级",
             "score": score,
             "detail": ubermensch},
        ]

        insights = []
        if "七杀" in ss.get("time", ""):
            insights.append("七杀透干——尼采会说'成为你自己'不是温和的邀请，而是激烈的战斗")
        if ts.get("食伤", 0) >= 2 and any("冲" in c for c in combos):
            insights.append("食伤旺+有冲——你有砸碎旧价值的冲动，问题是用什么来取代")
        if ts.get("印星", 0) >= 2 and ts.get("官杀", 0) >= 2:
            insights.append("印与杀对峙——这是'骆驼'与'狮子'的角力，先服从再反抗的经典路径")

        warnings = []
        if ts.get("印星", 0) >= 3 and ts.get("食伤", 0) == 0:
            warnings.append("过度理智化——尼采会提醒'太多的学问会扼杀行动的力量'")
        if "七杀" in ss.get("time", "") and ts.get("印星", 0) == 0:
            warnings.append("有毁灭倾向而无创造力——注意不要为了反抗而反抗")

        advice = []
        advice.append(f"你的超人阶段：{ubermensch}")
        if ts.get("食伤", 0) >= 2:
            advice.append("用创造代替抱怨——创造自己的价值体系比摧毁现有的更有力量")
        if wx.get("水", 0) >= 25:
            advice.append("水性深——适合在思想的深渊中探索，'当你凝视深渊，深渊也凝视着你'")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.65,
            "summary": f"权力意志评分{score}分。{ubermensch}。{'酒神VS日神' + ('——酒神更强' if ts.get('食伤',0)>=1 and wx.get('水',0)>=20 else '——日神为主')}。",
            "dimensions": dimensions,
            "key_insights": insights or ["尼采视角更适合有存在性困惑或面临价值抉择的场景"],
            "warnings": warnings or [], "advice": advice,
        }
