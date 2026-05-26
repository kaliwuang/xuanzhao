#!/usr/bin/env python3
"""
LiuBowen
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class LiuBowen(Perspective):
    name = "刘伯温"
    title = "天人合一微兆预警"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        combos = a["combinations"]
        ts = a["tenshen"]
        dayun = a["dayun_phase"]

        score = 50

        # 微兆识别：天干地支的微妙组合
        subtle_signals = []

        # 天克地冲=大信号
        for c in combos:
            if "冲" in c:
                subtle_signals.append(c)

        # 害=隐藏矛盾
        for c in combos:
            if "害" in c:
                subtle_signals.append(f"六害{c}——隐藏的矛盾")

        # 空亡=机会与陷阱
        xk = a["raw_bazi"].get("xunkong", {})
        xk_info = f"年柱空亡{xk.get('year','?')}，日柱空亡{xk.get('day','?')}" if xk else ""

        # 大运转换=关键节点
        if dayun:
            yi = dayun.get("year_index", 1)
            if yi <= 2:
                subtle_signals.append(f"刚入{dayun['ganzhi']}运（第{yi}年）——运势转换期，微兆最为关键")
            elif yi >= 8:
                subtle_signals.append(f"{dayun['ganzhi']}运末（第{yi}年）——准备迎接下一个大运的变化")

        # 信号越多分越高
        signal_count = len(subtle_signals)
        if signal_count >= 3:
            score += 20
        elif signal_count >= 1:
            score += 10

        # 印星=留心观察
        if ts.get("印星", 0) >= 2:
            score += 10
        # 水=洞察力
        if wx.get("水", 0) >= 20:
            score += 10
        # 冲=变量
        if any("冲" in c for c in combos):
            score += 5

        score = max(10, min(95, score))

        dimensions = [
            {"name": "微兆识别力",
             "score": min(100, 40 + 15 * signal_count),
             "detail": f"识别{signal_count}个潜在信号——{'机会藏在细节中' if signal_count >= 2 else '目前无明显异常信号'}"},
            {"name": "天人感应",
             "score": min(100, 40 + int(wx.get('水',0)) + 10 * ts.get("印星", 0)),
             "detail": f"{'水元素'+str(wx.get('水',0))+'%'+'=感应通道开放' if wx.get('水',0)>=20 else '感应通道一般'}，{'印星=有内观能力' if ts.get('印星',0)>=1 else '内观能力需培养'}"},
            {"name": "周期意识",
             "score": min(100, 30 + (20 if dayun else 0) + 10 * int(dayun and dayun.get('year_index',1)<=2)),
             "detail": f"当前{'在' + dayun['ganzhi'] + '运关键期' if dayun and dayun.get('year_index',1)<=2 else dayun['ganzhi']+'运' if dayun else '大运未详'}——{'刘伯温强调察微知著' if signal_count >= 2 else '运势平稳期'}"},
        ]

        insights = []
        if subtle_signals:
            insights.append(f"最值得关注的信号：{subtle_signals[0]}")
        if xk_info:
            insights.append(f"{xk_info}——空亡之处藏玄机，可能是意外之喜也可能是陷阱")

        warnings = []
        if any("害" in c for c in combos):
            warnings.append("六害入局——小人暗算或内部矛盾，是最大的隐性风险")

        advice = []
        advice.append("训练观察微兆的习惯——每天记录三个被忽略的小事，慢慢就会看出规律")
        if any("冲" in c for c in combos):
            advice.append("冲局如大潮——提前半年准备而非临时应对")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.6,
            "summary": f"微兆预警评分{score}分。识别{signal_count}个信号。{'水木有灵' if wx.get('水',0)>=20 and wx.get('木',0)>=20 else '感应通道一般'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["目前命局没有突出的大信号，小信号需要细心捕捉"],
            "warnings": warnings or [], "advice": advice,
        }
