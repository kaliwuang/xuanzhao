#!/usr/bin/env python3
"""
Naval
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Naval(Perspective):
    name = "Naval"
    title = "长期主义与杠杆"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        features = a["features"]
        
        score = 50
        
        # 特定知识（印星=学习能力）
        if ts.get("印星", 0) >= 2:
            score += 20
        elif ts.get("印星", 0) == 1:
            score += 10
        
        # 杠杆能力（财星=资源配置）
        if ts.get("财星", 0) >= 1:
            score += 10
        
        # 长期主义（大运判断）
        dm_wx = dm.get("wuxing", "")
        dayun_phase = a["dayun_phase"]
        if dayun_phase:
            d_g = dayun_phase.get("gan_wuxing", "")
            if d_g == dm_wx:
                score += 10  # 大运帮身=长期在正轨
            elif d_g and wx.get(d_g, 0) > 20:
                score += 5
        
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "特定知识",
                "score": min(100, 40 + 20 * ts.get("印星", 0)),
                "detail": f"印星{ts.get('印星',0)}个——{'学什么都能深' if ts.get('印星',0) >= 2 else '需要找到真正热爱的领域深耕'}"
            },
            {
                "name": "杠杆能力",
                "score": min(100, 50 + 15 * ts.get("财星", 0)),
                "detail": f"财星{ts.get('财星',0)}个——{'有资源运作的直觉' if ts.get('财星',0) >= 1 else '杠杆思维需要刻意训练'}"
            },
            {
                "name": "复利耐心",
                "score": min(100, 40 + int(a['daymaster']['support_ratio'])),
                "detail": a["daymaster"]["detail"]
            },
        ]
        
        insights = []
        if ts.get("印星", 0) >= 2:
            insights.append(f"印星{ts.get('印星',0)}个=获取特定知识的天赋——Naval说这是最好的护城河")
        if ts.get("财星", 0) >= 1:
            insights.append("财星透干=对杠杆有直觉——代码/媒体/资本三条路都可以考虑")
        
        warnings = []
        if ts.get("比劫", 0) >= 2 and ts.get("财星", 0) == 0:
            warnings.append("比劫旺而无财——需要警惕杠杆带来的债务风险")
        
        advice = []
        advice.append(f"核心建议：找到你的「特定知识」——{'你已经有了学习的天赋，缺的是选对方向' if ts.get('印星',0) >= 2 else '先深耕一个领域再谈杠杆'}")
        if ts.get("财星", 0) == 0:
            advice.append("财富不是目的，创造价值才是——先聚焦在自己能提供什么稀缺价值")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.65,
            "summary": f"长期主义评分{score}分。{'印星有力=学习类特定知识' if ts.get('印星',0) >= 2 else '需先建立深度专长'}。{'有杠杆直觉' if ts.get('财星',0) >= 1 else '杠杆是选修课'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["Naval式分析更适用于具体问题，先有专业再有杠杆"],
            "warnings": warnings or [],
            "advice": advice,
        }
