#!/usr/bin/env python3
"""
GuiGuZi
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class GuiGuZi(Perspective):
    name = "鬼谷子"
    title = "捭阖之道攻心为上"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]

        score = 50
        dm_wx = dm.get("wuxing", "")

        # 捭（开放）：食伤=表达能力
        if ts.get("食伤", 0) >= 2:
            score += 15
        elif ts.get("食伤", 0) >= 1:
            score += 8
        # 阖（闭合）：印星=沉默观察
        if ts.get("印星", 0) >= 2:
            score += 15
        elif ts.get("印星", 0) >= 1:
            score += 8
        # 飞箝（说服力）：财星=资源洞察
        if ts.get("财星", 0) >= 1:
            score += 10
        # 反应术（洞察力）：水元素=感知
        if wx.get("水", 0) >= 20:
            score += 10
        # 抵巇（抓裂缝）：有冲=有可以利用的矛盾
        if any("冲" in c for c in a["combinations"]):
            score += 5

        score = max(10, min(95, score))

        # 性格倾向判断
        if ts.get("食伤", 0) >= ts.get("印星", 0):
            style = "捭（开放型）——善于表达，需要学会闭嘴"
        else:
            style = "阖（内敛型）——善于观察，需要学会开口"

        dimensions = [
            {"name": "捭阖平衡",
             "score": min(100, 50 + 10 * abs(ts.get("食伤",0) - ts.get("印星",0))),
             "detail": style},
            {"name": "洞察人心",
             "score": min(100, 30 + 15 * ts.get("财星",0) + int(wx.get('水',0))),
             "detail": f"{'水元素'+str(wx.get('水',0))+'%'+'=感知力' if wx.get('水',0)>=20 else '感知力一般'}，{'财星透出=对资源流动敏感' if ts.get('财星',0)>=1 else '资源洞察需要训练'}"},
            {"name": "说服力",
             "score": min(100, 40 + 15 * ts.get("食伤",0) + 10 * ts.get("财星",0)),
             "detail": f"食伤{ts.get('食伤',0)}个+财星{ts.get('财星',0)}个——{'有说服他人的天然武器' if ts.get('食伤',0)+ts.get('财星',0)>=2 else '说服力来自信息优势'}"},
            {"name": "随机应变",
             "score": min(100, 50 + 10 * ts.get("食伤",0) - 5 * ts.get("印星",0)),
             "detail": f"{'灵活性高' if ts.get('食伤',0)>ts.get('印星',0) else '稳定性强' if ts.get('印星',0)>ts.get('食伤',0) else '灵活与稳定均衡'}"},
        ]

        insights = []
        if ts.get("食伤", 0) >= 1 and ts.get("印星", 0) >= 1:
            insights.append("食伤印星兼备——天生的纵横家，既能说也能藏")
        if wx.get("水", 0) >= 20:
            insights.append(f"水性足({wx['水']}%)——鬼谷子会说你天生会'反应术'，善于从对方话中读信息")

        warnings = []
        if ts.get("印星", 0) >= 3 and ts.get("食伤", 0) == 0:
            warnings.append("过阖不捭——容易把自己藏太深，别人看不透你也就无法信任你")

        advice = []
        advice.append(f"你的风格是{style}")
        if wx.get("水", 0) < 15:
            advice.append("水性偏弱——可以刻意练习倾听，水主智也主柔")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.65,
            "summary": f"捭阖评分{score}分。{style}。{'洞察力敏锐' if wx.get('水',0)>=20 else '说服力可后天培养'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["捭阖之道需结合具体场景应用"],
            "warnings": warnings or [], "advice": advice,
        }
