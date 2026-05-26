#!/usr/bin/env python3
"""
WangYangming
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class WangYangming(Perspective):
    name = "王阳明"
    title = "知行合一"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        features = a["features"]
        
        # 知（印星=认知能力）
        knowledge = ts.get("印星", 0) * 15 + 30
        # 行（比劫=行动力 + 财星=实践）
        action = ts.get("比劫", 0) * 10 + ts.get("财星", 0) * 10 + 30
        
        gap = abs(knowledge - action)
        balance = max(0, 100 - gap * 2)
        
        score = int(balance)
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "知", "score": min(100, knowledge),
                "detail": f"认知层面评分{min(100, knowledge)}——{'印星有力=善于思考' if ts.get('印星',0) >= 2 else '思考深度需训练'}"
            },
            {
                "name": "行", "score": min(100, action),
                "detail": f"行动层面评分{min(100, action)}——{'执行力不俗' if action > 50 else '行动力需加强'}"
            },
            {
                "name": "知行落差", "score": score,
                "detail": f"知行差距{gap}分——{'知行合一' if gap < 20 else '想得多做得少' if knowledge > action else '行动快于思考'}"
            },
        ]
        
        insights = []
        if gap < 20:
            insights.append("知行基本合一——这是最难得的素质")
        elif knowledge > action:
            insights.append(f"知({knowledge})大于行({action})——王阳明会说'知道却做不到=不知道'")
        else:
            insights.append(f"行({action})大于知({knowledge})——实干型，但需要在实践中提炼理论")
        
        warnings = []
        if ts.get("印星", 0) >= 3 and ts.get("比劫", 0) == 0:
            warnings.append("纯思型——容易陷入空想，事上练是唯一的出路")
        
        advice = []
        advice.append("事上练——所有道理都要在具体事上验证")
        if gap > 30:
            advice.append(f"知行差距过大，建议选一件小事做到极致，先缩小差距再谈大方向")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.7,
            "summary": f"知行合一评分{score}分。{'知行基本平衡' if gap < 20 else '知大于行' if knowledge > action else '行大于知'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["命局知行差距不明显，后天习惯决定知行合一程度"],
            "warnings": warnings or [],
            "advice": advice,
        }
