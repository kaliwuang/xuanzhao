#!/usr/bin/env python3
"""
ZhangYiming
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class ZhangYiming(Perspective):
    name = "张一鸣"
    title = "认知迭代信息效率"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        dayun = a["dayun_phase"]
        combos = a["combinations"]

        score = 50

        # 信息处理能力（印星=吸收，食伤=输出）
        absorb = ts.get("印星", 0) * 15
        output = ts.get("食伤", 0) * 15
        info_score = absorb + output
        if info_score >= 40:
            score += 20
        elif info_score >= 20:
            score += 10

        # 延迟满足（财星+印星=长期思维）
        if ts.get("财星", 0) >= 1 and ts.get("印星", 0) >= 1:
            score += 15
        elif ts.get("印星", 0) >= 2:
            score += 10

        # 认知迭代速度（有冲=认知冲突=迭代契机）
        if any("冲" in c for c in combos):
            score += 10

        # 信息效率（木火=生长与表达）
        if wx.get("木", 0) >= 20 and wx.get("火", 0) >= 20:
            score += 10

        # 大运节奏
        if dayun and dayun.get("year_index", 1) <= 3:
            score += 5  # 新运=加速器

        score = max(10, min(95, score))

        dimensions = [
            {"name": "信息吸收力",
             "score": min(100, 30 + absorb),
             "detail": f"印星{ts.get('印星',0)}个={'信息输入能力强' if ts.get('印星',0)>=1 else '需建立稳定输入渠道'}"},
            {"name": "信息输出力",
             "score": min(100, 30 + output),
             "detail": f"食伤{ts.get('食伤',0)}个={'善于表达和输出' if ts.get('食伤',0)>=1 else '输出能力可培养'}"},
            {"name": "延迟满足",
             "score": min(100, 30 + 20 * int(ts.get('财星',0)>=1 and ts.get('印星',0)>=1) + 10 * int(ts.get('印星',0)>=2)),
             "detail": f"{'财印俱全=有长期主义的特质' if ts.get('财星',0)>=1 and ts.get('印星',0)>=1 else '延迟满足是需要刻意练习的'}"},
            {"name": "认知跃迁概率",
             "score": min(100, 40 + 15 * int(any('冲' in c for c in combos)) + 10 * int(wx.get('木',0)>=20 and wx.get('火',0)>=20)),
             "detail": f"{'有冲=认知冲突=跃迁契机' if any('冲' in c for c in combos) else '认知迭代偏渐进式'}"},
        ]

        insights = []
        if ts.get("印星", 0) >= 1 and ts.get("食伤", 0) >= 1:
            insights.append(f"印食兼具——输入输出平衡，有信息飞轮的潜质")
        if ts.get("财星", 0) >= 1 and ts.get("印星", 0) >= 1:
            insights.append("财印皆有——张一鸣式'不做表面功夫'的底层算法")
        if dayun and dayun.get("year_index", 1) <= 3:
            insights.append(f"刚进入{dayun['ganzhi']}运——认知迭代速度应该乘2")

        warnings = []
        if ts.get("印星", 0) >= 3 and ts.get("食伤", 0) == 0:
            warnings.append("信息过载风险——输入太多不输出会形成认知便秘")

        advice = []
        advice.append("建立信息筛选机制——输入质量决定输出质量")
        if wx.get("火", 0) < 15:
            advice.append("火弱——表达需要刻意练习，写作或演讲是认知迭代的加速器")
        if ts.get("财星", 0) >= 1 and ts.get("印星", 0) >= 1:
            advice.append("你的商业模式底色：做那些可以被复利的事——知识产品、数字资产")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.6,
            "summary": f"认知迭代评分{score}分。{'信息飞轮已启动' if ts.get('印星',0)>=1 and ts.get('食伤',0)>=1 else '需建立信息循环'}。{'长期主义底色' if ts.get('财星',0)>=1 and ts.get('印星',0)>=1 else '短期导向'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["张一鸣视角更适合职业发展和认知成长方面的具体问题"],
            "warnings": warnings or [], "advice": advice,
        }
