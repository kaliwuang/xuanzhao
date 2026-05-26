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
    
    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        dm = a["daymaster"]
        ts = a["tenshen"]
        
        # Naval式分析：特定知识 × 杠杆 × 复利 × 问责制
        p1 = ""
        if ts.get("印星", 0) >= 2:
            p1 = f"先看你的『特定知识』（Specific Knowledge）。印星{ts['印星']}处——你在学习方面有天然优势，能在某个领域做到极深。\n\nNaval说：『Specific knowledge is knowledge you cannot be trained for. If society can train you, it can train someone else and replace you.』\n\n印星是你的特定知识天赋——那些你学得快、学得深、别人替代不了的东西。找到它，深耕它，让它成为你的护城河。"
        elif ts.get("印星", 0) == 1:
            p1 = f"印星1处——你有一个学习引擎，但需要找到正确的方向。Naval说你必须找到那些你『天生就比别人做得轻松』的事。\n\n『If you can't explain it simply, you don't understand it well enough』——先确保你真正理解了某个领域，再谈深耕。深度比广度更有复利效应。"
        else:
            p1 = "印星不显——你的特定知识不在书本学习，而可能在实践领域。Naval本人就不是学院派，他的特定知识来自创业和投资实践。\n\n『The most important skill for getting rich is becoming a perpetual learner.』——如果你不擅长从书本学，就从实战中学。"
        
        p2 = ""
        if ts.get("财星", 0) >= 1:
            p2 = "财星透干——你对『杠杆』（Leverage）有直觉。Naval说现代财富的三大杠杆是：劳动（最古老）、资本（最强大）、代码与媒体（最新且零边际成本）。\n\n『Give me a lever long enough and a place to stand, and I will move the earth.』——你的财星就是你的杠杆支点。建议优先使用代码或媒体杠杆：写代码、做内容、建系统，把你的财星能量放大到无限。"
        else:
            p2 = "财星不显——杠杆不是你的本能，但可以被习得。Naval说杠杆是现代人致富的必经之路。三条路：资本（需要别人信任你的判断）、代码（需要学点编程）、媒体（需要持续输出）。\n\n『You want to own equity: assets, businesses, intellectual property. That's where wealth comes from.』——先从拥有可复用的资产开始。"
        
        p3 = ""
        dm_wx = dm.get("wuxing", "")
        dayun_phase = a["dayun_phase"]
        if dayun_phase:
            d_g = dayun_phase.get("gan_wuxing", "")
            if d_g == dm_wx:
                p3 = f"当前{dayun_phase['ganzhi']}运——大运帮身，处于复利窗口期。Naval说复利不仅适用于金钱，也适用于知识和关系。\n\n『Compound interest is the eighth wonder of the world.』——在这个运里，你每天的知识积累、社会连接、技能提升都会产生复利效应。别浪费这个窗口。"
            else:
                p3 = f"当前{dayun_phase['ganzhi']}运——运势不在高峰，但Naval式思维告诉我们：财富 = 特定知识 × 杠杆 × 复利 × 问责制（Accountability）。问责制是最容易被忽视的一环——把你的声誉和你做的事绑定。\n\n『You get rich by giving society what it wants but doesn't yet know how to get. At scale.』——即使不顺，持续创造价值总有回报。"
        else:
            p3 = "大运数据不足，但Naval的财富原则依然适用：财富不是靠忙碌赚来的，是靠成为比特流通的节点。\n\n『Escape competition through authenticity.』——没人能比你更好地做你自己。唯一真正的竞争是和你自己的昨日。"
        
        # 财富 vs 地位
        p4 = ""
        if ts.get("财星", 0) >= 1 and ts.get("印星", 0) >= 1:
            p4 = "财印俱全——Naval会说你站在了正确的一边。财富创造（财星）和知识积累（印星）是正和游戏，而地位游戏是零和的。\n\n『The best way to get rich is to create wealth, not play status games.』——你的命局暗示你更适合做财富创造者，这不是偶然。"
        
        return f"{p1}\n\n{p2}\n\n{p3}\n\n{p4}" if p4 else f"{p1}\n\n{p2}\n\n{p3}"

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
