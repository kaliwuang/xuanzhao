#!/usr/bin/env python3
"""
Buffett
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Buffett(Perspective):
    name = "巴菲特"
    title = "价值投资安全边际"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        dayun = a["dayun_phase"]

        score = 50

        # 内在价值（日主强度）
        support = a["daymaster"]["support_ratio"]
        if support >= 50:
            score += 20  # 基本面扎实
        elif support >= 35:
            score += 10

        # 安全边际（印星+比劫=保护层）
        protection = ts.get("印星", 0) * 10 + ts.get("比劫", 0) * 10
        if protection >= 30:
            score += 15
        elif protection >= 15:
            score += 8

        # 护城河（财星=持久竞争优势）
        if ts.get("财星", 0) >= 1:
            score += 10
        if ts.get("印星", 0) >= 2:
            score += 5  # 印星=可复用的知识

        # 管理层（官杀=决断力）
        if ts.get("官杀", 0) >= 1:
            score += 5

        # 周期判断（大运）
        if dayun:
            d_wx = dayun.get("gan_wuxing", "")
            dm_wx = dm.get("wuxing", "")
            if d_wx == dm_wx:
                score += 10  # 顺周期
            elif _WUXING_CONQUER.get(d_wx) == dm_wx:
                score -= 5  # 逆周期

        score = max(10, min(95, score))

        # 价值判断
        if score >= 70:
            valuation = "低估——市场错了，现在是最好的买入时机"
        elif score >= 50:
            valuation = "合理估值——持有等待价值释放"
        else:
            valuation = "高估——需要更多安全边际"

        dimensions = [
            {"name": "内在价值",
             "score": min(100, int(support)),
             "detail": f"生扶力度{support}%——{'基本面扎实' if support >= 50 else '需要积累更多资本'}"},
            {"name": "安全边际",
             "score": min(100, 30 + protection),
             "detail": f"{'保护充足' if protection >= 30 else '安全边际不足'}"},
            {"name": "护城河",
             "score": min(100, 30 + 20 * ts.get("财星",0) + 10 * ts.get("印星",0)),
             "detail": f"{'财星+印星=有复利根基' if ts.get('财星',0)>=1 and ts.get('印星',0)>=1 else '护城河需要后天建立'}"},
            {"name": "周期位置",
             "score": min(100, 50 + (10 if dayun and (dayun.get('gan_wuxing','')==dm.get('wuxing','')) else 0) - (5 if dayun and (_WUXING_CONQUER.get(dayun.get('gan_wuxing',''))==dm.get('wuxing','')) else 0)),
             "detail": f"当前{'顺周期' if dayun and (dayun.get('gan_wuxing','')==dm.get('wuxing','')) else '逆周期' if dayun and (_WUXING_CONQUER.get(dayun.get('gan_wuxing',''))==dm.get('wuxing','')) else '中性周期'}" if dayun else "周期判断需大运数据"
            },
        ]

        insights = []
        if support >= 50:
            insights.append(f"基本面评分{support}%——巴菲特会说'价格是你支付的，价值是你得到的'")
        if ts.get("印星", 0) >= 2:
            insights.append(f"印星{ts.get('印星',0)}个=复利机器——知识是最佳投资标的")
        if dayun and (dayun.get('gan_wuxing','') == dm.get('wuxing','')):
            insights.append(f"当前{dayun['ganzhi']}运顺周期——是建立护城河的好时机")

        warnings = []
        if protection < 15:
            warnings.append("安全边际不足——不要加杠杆，保持现金储备")

        advice = []
        advice.append(f"价值判断：{valuation}")
        advice.append("最重要的投资是投资自己——印星=自我教育是最好的长期资产")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.65,
            "summary": f"价值投资评分{score}分。{valuation}。{'护城河' + ('已形成' if ts.get('财星',0)>=1 and ts.get('印星',0)>=1 else '待建立')}。",
            "dimensions": dimensions,
            "key_insights": insights or ["巴菲特视角更适合财富管理方面的具体问题"],
            "warnings": warnings or [], "advice": advice,
        }
