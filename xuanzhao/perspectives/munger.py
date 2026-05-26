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
        
        # 芒格式：先看坑
        pitfalls = []
        if not f['th'].get('yongshen'):
            pitfalls.append("调候用神不显——容易在不适合自己的方向上死磕")
        if f["chong"]:
            pitfalls.append(f"{f['chong'][0]}——内耗是最大成本，得花时间处理内在矛盾")
        if ts.get("财星", 0) == 0 and ts.get("食伤", 0) == 0:
            pitfalls.append("财星食伤皆不显——对市场/外部环境的感知力偏弱")
        if dm.get("strength") == "身弱" and ts.get("印星", 0) == 0:
            pitfalls.append("身弱无印——'自我'的边界不够清晰，容易被外界带偏")
        
        if pitfalls:
            p1 = f"逆向思考：先不看这个命局能做什么，先看它容易在哪摔跤。我发现了{len(pitfalls)}个潜在陷阱："
            for p in pitfalls:
                p1 += f"\n- {p}"
        else:
            p1 = "逆向检查没有发现明显陷阱——命局结构合理，但这本身也是一种风险：没有明显问题的人往往对问题缺乏警觉。"
        
        p2 = ""
        if ts.get("印星", 0) >= 1:
            p2 = f"好在印星显现有{ts['印星']}处——学习能力是你的护城河。芒格说的'多学科思维模型'，印星就是你的工具箱。"
        else:
            p2 = "印星不显——缺少天然的'学习习惯'。这不是致命伤，但意味着你需要刻意建立知识框架。"
        
        p3 = ""
        if f["dayun"].get("ganzhi"):
            d = f["dayun"]
            if d.get('gan_wuxing','') == dm.get('wuxing','') or d.get('zhi_wuxing','') == dm.get('wuxing',''):
                p3 = f"当前{f['dayun_str']}——这个运帮身，是少犯错、多积累的好时机。芒格说一辈子只需做对几次关键决策就够了。"
            else:
                p3 = f"当前{f['dayun_str']}——运势不帮身，更要慢下来少犯错。记住：不做什么比做什么重要。"
        
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
