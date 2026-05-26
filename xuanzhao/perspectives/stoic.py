#!/usr/bin/env python3
"""
Stoic
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Stoic(Perspective):
    name = "斯多葛"
    title = "控制二分法"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        combos = a["combinations"]
        
        score = 50
        
        # 可控部分：印星（认知）+ 比劫（行动）
        controllable = ts.get("印星", 0) * 10 + ts.get("比劫", 0) * 10
        # 不可控部分：官杀（外界压力）+ 财星（物质波动）
        uncontrollable = ts.get("官杀", 0) * 10 + ts.get("财星", 0) * 10
        
        if controllable >= uncontrollable:
            score += 15
        else:
            score -= 5
        
        # 消极想象（印星越强越能做）
        if ts.get("印星", 0) >= 2:
            score += 10
        
        # 逆境即磨炼
        if "七杀" in str(a["raw_bazi"].get("shishen", {})):
            score += 10
        
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "控制边界清晰度",
                "score": min(100, 50 + int(controllable - uncontrollable)),
                "detail": f"可控力{controllable}分 vs 外力{uncontrollable}分——{'清楚什么在自己掌控之内' if controllable > uncontrollable else '容易为不可控的事情焦虑'}"
            },
            {
                "name": "逆境承受力",
                "score": min(100, 50 + 15 * int("七杀" in str(a['raw_bazi'].get('shishen',{})))),
                "detail": f"{'七杀透干=逆境经验丰富' if '七杀' in str(a['raw_bazi'].get('shishen',{})) else '逆境经历相对较少'}"
            },
            {
                "name": "内心自由",
                "score": max(10, 70 - 10 * ts.get("官杀", 0)),
                "detail": f"官杀{ts.get('官杀',0)}个——{'外界压力可能侵蚀内心自由' if ts.get('官杀',0) >= 2 else '内心相对自主'}"
            },
        ]
        
        insights = []
        if controllable > uncontrollable:
            insights.append("你的命局中，可控因素多于不可控——斯多葛会说你天生适合理性生活")
        if "七杀" in str(a["raw_bazi"].get("shishen", {})):
            insights.append("七杀是斯多葛的黄金训练——逆境是磨炼灵魂的土壤")
        
        warnings = []
        if uncontrollable > controllable * 2:
            warnings.append("外部约束过多——需要在不可控中找回自己的判断主权")
        
        advice = []
        advice.append("控制二分法练习：列出你担心的所有事，划掉你控制不了的")
        if ts.get("官杀", 0) >= 2:
            advice.append("外界压力大时，记住：'人不是被事情本身困扰，而是被对事情的看法困扰'")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.65,
            "summary": f"控制二分法评分{score}分。{'可控>不可控' if controllable > uncontrollable else '需重新识别控制的边界'}。{'七杀=逆境磨炼' if '七杀' in str(a['raw_bazi'].get('shishen',{})) else '建议主动制造适度挑战'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["控制二分法练习对大多数人都有帮助，不依赖命局"],
            "warnings": warnings or [],
            "advice": advice,
        }
