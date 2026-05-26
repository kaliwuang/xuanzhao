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
    
    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        dm = a["daymaster"]
        ts = a["tenshen"]
        
        # 心即理——先看本心格局
        dm_strength = dm.get("strength", "?")
        if dm_strength in ("身强", "中和"):
            heart = (
                f"阳明先生曰：观此命盘，先格其心。"
                f"日主{f['dm_str']}，{dm_strength}之格——"
                f"「心即理也。天下又有心外之事、心外之理乎？」\n\n"
                f"此命本心具足，不假外求。"
                f"{f['strongest']}气虽盛，然「破山中贼易，破心中贼难」——"
                f"最大的敌人不在命局中，而在你的本心里。"
            )
        else:
            heart = (
                f"阳明先生曰：观此命盘，先格其心。"
                f"日主{f['dm_str']}，{dm_strength}之格——\n\n"
                f"「心外无物，心外无事，心外无理。」\n"
                f"身弱不是缺陷，而是提醒你向内求。"
                f"「志不立，天下无可成之事」——格局不在五行强弱，而在立志之大小。"
            )
        
        # 知行合一
        knowledge = ts.get("印星", 0) * 15 + 30
        action = ts.get("比劫", 0) * 10 + ts.get("财星", 0) * 10 + 30
        gap = abs(knowledge - action)
        
        if gap < 20:
            zhixing = (
                f"知行差距仅{gap}分——「知是行之始，行是知之成。」\n"
                f"此命知行已然合一，难能可贵。"
                f"「知而不行，只是未知」——你已迈过这道坎。"
            )
        elif knowledge > action:
            zhixing = (
                f"知行差距{gap}分，知({knowledge})大于行({action})。\n"
                f"「未有知而不行者。知而不行，只是未知。」\n"
                f"先生在此提醒：你所谓的「知道」，怕还不是真知。"
                f"「事上练」——在具体事上磨练，方是真学问。"
            )
        else:
            zhixing = (
                f"知行差距{gap}分，行({action})大于知({knowledge})。\n"
                f"「行之明觉精察处便是知，知之真切笃实处便是行。」\n"
                f"实干型是好的，但需在行动中提炼真知，否则行之不远。"
            )
        
        # 致良知——大运中的本心指引
        dayun_p = ""
        if f["dayun"].get("ganzhi"):
            d = f["dayun"]
            dayun_p = (
                f"当前{f['dayun_str']}——「尔那一点良知，是尔自家底准则。」\n"
                f"此运之中，外有{f['dayun_str']}之气牵引，内有日主{f['dm_str']}呼应。\n"
                f"「是非之心，不虑而知，不学而能，所谓良知也。」\n"
                f"无需外求，你的良知自会告诉你方向。"
            )
        else:
            dayun_p = (
                "大运未动。「人须在事上磨，方立得住。」\n"
                "当下正是磨练心性的时机——"
                "「静处体悟，事上磨练」——在无事之时致良知，有事之时行良知。"
            )
        
        return f"{heart}\n\n{zhixing}\n\n{dayun_p}"

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
