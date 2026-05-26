#!/usr/bin/env python3
"""
Munger
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Munger(Perspective):
    name = "芒格"
    title = "逆向思维多元模型"
    

    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        dm = a["daymaster"]
        ts = a["tenshen"]
        
        # 芒格式：先看坑（Inversion — "Invert, always invert"）
        pitfalls = []
        if not f['th'].get('yongshen'):
            pitfalls.append("调候用神不显——容易在不适合自己的方向上死磕。『Invert, always invert』——先排除会让你完蛋的路")
        if f["chong"]:
            pitfalls.append(f"{f['chong'][0]}——内耗是最大成本。芒格说『All I want to know is where I'm going to die, so I'll never go there』——先避开这个冲突")
        if ts.get("财星", 0) == 0 and ts.get("食伤", 0) == 0:
            pitfalls.append("财星食伤皆不显——对市场/外部环境的感知力偏弱。『I'd rather be generally right than precisely wrong』——感知方向比精确数据更重要")
        if dm.get("strength") == "身弱" and ts.get("印星", 0) == 0:
            pitfalls.append("身弱无印——『自我』边界不清晰，容易被外界带偏。这是Lollapalooza效应的土壤：多种偏误叠加形成恶性循环")
        
        if pitfalls:
            p1 = f"逆向思考（Inversion）：先不看这个命局能做什么，先看它容易在哪摔跤。\n「Invert, always invert」——Jacob说的，我照做。\n我发现了{len(pitfalls)}个潜在陷阱："
            for p in pitfalls:
                p1 += f"\n- {p}"
            # Lollapalooza check
            if len(pitfalls) >= 3:
                p1 += "\n\n⚠️ 多重陷阱叠加，这就是芒格说的Lollapalooza效应——多个偏误同时作用、相互强化。遇到这种情况，最佳策略是：什么都别做。"
        else:
            p1 = "逆向检查没有发现明显陷阱——命局结构合理。但这本身就是一种风险：没有明显问题的人往往对问题缺乏警觉。\n『The big money is not in the buying and selling, but in the waiting.』"
        
        p2 = ""
        if ts.get("印星", 0) >= 1:
            p2 = f"好，现在来看你的多元思维模型工具箱（Latticework of Mental Models）。印星显现有{ts['印星']}处——这就是你的跨学科工具箱。\n『You must have a latticework of models in your head』——学科越多，盲区越少。印星是你从不同学科提取模型的能力。"
        else:
            p2 = "印星不显——缺少天然的『学习习惯』。芒格说『The best way to get what you want is to deserve what you want』——先去建立一个跨学科的知识框架，你配得上更好的判断力。"
        
        p3 = ""
        if f["dayun"].get("ganzhi"):
            d = f["dayun"]
            if d.get('gan_wuxing','') == dm.get('wuxing','') or d.get('zhi_wuxing','') == dm.get('wuxing',''):
                p3 = f"当前{f['dayun_str']}——这个运帮身，是少犯错、多积累的好时机。芒格一辈子只做了几个重大决策：See's Candy、可口可乐、Costco、BYD。\n『It is remarkable how much long-term advantage we have gotten by trying to be consistently not stupid, instead of trying to be very intelligent.』"
            else:
                p3 = f"当前{f['dayun_str']}——运势不帮身，更要慢下来、少犯错。逆向思考的应用：不问『怎么变好』，问『怎么确保不变得更差』，然后避开那些路。\n『All I want to know is where I'm going to die, so I'll never go there.』"
        
        return f"{p1}\n\n{p2}\n\n{p3}"
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        features = a["features"]
        ts = a["tenshen"]
        combos = a["combinations"]
        
        # 逆向：先找最可能踩的坑
        pitfalls = []
        
        # 印星过多=纸上谈兵
        if ts.get("印星", 0) >= 3:
            pitfalls.append("印星过旺——理论与实践脱节的风险")
        # 食伤过旺=不切实际
        if ts.get("食伤", 0) >= 3:
            pitfalls.append("食伤过旺——创意丰富但落地困难")
        # 财星旺但比劫弱=守不住
        if ts.get("财星", 0) >= 2 and ts.get("比劫", 0) == 0:
            pitfalls.append("财旺无劫——有机会但不一定能守住")
        # 官杀混杂
        if ts.get("官杀", 0) >= 2:
            pitfalls.append("官杀混杂——多重压力下的决策瘫痪风险")
        
        score = 50
        if len(pitfalls) <= 1:
            score += 20  # 坑少=明智
        elif len(pitfalls) <= 2:
            score += 10
        
        # 印星=学习能力（芒格看重这个）
        if ts.get("印星", 0) >= 2:
            score += 15
        elif ts.get("印星", 0) == 1:
            score += 5
        
        # 冲=冒险倾向（双刃剑）
        if any("冲" in c for c in combos):
            score += 5  # 勇气加分
            score -= 5  # 冲动减分
        
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "逆向思维力",
                "score": min(100, 50 + 15 * (len(pitfalls) > 0)),
                "detail": f"识别{len(pitfalls)}个潜在陷阱——{'知道避什么比知道追什么更重要' if pitfalls else '命局无明显陷阱'}"
            },
            {
                "name": "跨学科学习力",
                "score": min(100, 40 + 15 * ts.get("印星", 0)),
                "detail": f"印星{ts.get('印星',0)}个——{'多元思维模型的基础不错' if ts.get('印星',0) >= 2 else '需要刻意拓展知识面' if ts.get('印星',0) == 1 else '亟待建立跨学科框架'}"
            },
            {
                "name": "情绪管理",
                "score": max(10, 70 - 10 * ts.get("官杀", 0)),
                "detail": f"官杀{ts.get('官杀',0)}个——{'心理压力可能影响判断' if ts.get('官杀',0) >= 2 else '情绪相对稳定'}"
            },
        ]
        
        insights = []
        if pitfalls:
            insights.append(f"最值得避开的是：{pitfalls[0]}")
        if ts.get("印星", 0) >= 2:
            insights.append("印星有力=学习能力强——芒格会说这是最好的优势")
        
        warnings = pitfalls
        
        advice = []
        advice.append("「如果知道自己会死在哪里，就永远不去那里」——先避开错误再做对的事")
        if ts.get("官杀", 0) >= 2:
            advice.append("压力是判断力的大敌——在高压力下暂停决策")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.75,
            "summary": f"芒格式分析：先看坑——发现{len(pitfalls)}个潜在陷阱。{'命局明智' if len(pitfalls) <= 1 else '需谨慎行'}。{'学习特质突出' if ts.get('印星',0) >= 2 else '建议建立系统学习框架'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["命局无明显典型陷阱，决策质量更多取决于后天习惯"],
            "warnings": warnings,
            "advice": advice,
        }
