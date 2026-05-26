#!/usr/bin/env python3
"""
Hermes
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Hermes(Perspective):
    name = "赫尔墨斯"
    title = "七原则如其在上"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        combos = a["combinations"]
        th = a["tiaohou"]

        score = 50

        # 1. 心物对应（mentalism）：印星=思维覆盖现实
        if ts.get("印星", 0) >= 2:
            score += 10
        # 2. 对应原则（correspondence）：五行平衡=宏观微观一致
        wx_vals = sorted(wx.values(), reverse=True)
        if len(wx_vals) >= 2 and wx_vals[0] - wx_vals[-1] < 20:
            score += 15
        # 3. 振动原则（vibration）：食伤=能量向外辐射
        if ts.get("食伤", 0) >= 2:
            score += 10
        # 4. 极性原则（polarity）：冲=对立统一
        if any("冲" in c for c in combos):
            score += 10
        # 5. 节奏原则（rhythm）：大运=生命节奏
        if a["dayun_phase"]:
            score += 10
        # 6. 因果原则（causality）：用神=关键因素
        if th.get("yongshen"):
            score += 5
        # 7. 性别原则（gender）：阴阳平衡
        if wx.get("水", 0) >= 20 and wx.get("火", 0) >= 20:
            score += 10

        score = max(10, min(95, score))

        # 七原则分析
        principles = [
            f"心物法则——{'印星有力=思维能量强' if ts.get('印星',0)>=2 else '心物连接一般'}",
            f"对应法则——{'五行均衡=天地人三才对应良好' if len(wx_vals)>=2 and wx_vals[0]-wx_vals[-1]<20 else '五行偏枯=需要更多调和'}",
            f"振动法则——{'食伤透干=能量向外辐射' if ts.get('食伤',0)>=1 else '能量内敛'}",
            f"极性法则——{'有冲=对立统一的原动力' if any('冲' in c for c in combos) else '极性相对平衡'}",
            f"节奏法则——{'大运流转=生命节奏清晰' if a['dayun_phase'] else '节奏待显化'}",
            f"因果法则——{'用神明确=因果链条清晰' if th.get('yongshen') else '因果需探索'}",
            f"性别法则——{'水火并存=阴阳俱足' if wx.get('水',0)>=20 and wx.get('火',0)>=20 else '阴阳有偏'}"
        ]

        dimensions = [
            {"name": "七原则共振",
             "score": score,
             "detail": f"七原则中{sum(1 for p in [ts.get('印星',0)>=2, len(wx_vals)>=2 and wx_vals[0]-wx_vals[-1]<20, ts.get('食伤',0)>=2, any('冲' in c for c in combos), bool(a['dayun_phase']), bool(th.get('yongshen')), wx.get('水',0)>=20 and wx.get('火',0)>=20])}条活跃"},
            {"name": "如其在上",
             "score": min(100, 40 + 15 * ts.get("印星",0) + 15),
             "detail": f"微观八字对应宏观人生——{'有良好的抽象对应能力' if ts.get('印星',0)>=2 else '对应关系需练习发现'}"},
            {"name": "阴阳调和",
             "score": min(100, 50 + int(abs(wx.get('水',0)-wx.get('火',0)) < 15) * 20),
             "detail": f"水火差{abs(wx.get('水',0)-wx.get('火',0)):.0f}%——{'阴阳平衡' if abs(wx.get('水',0)-wx.get('火',0)) < 15 else '阴' + ('盛' if wx.get('水',0) > wx.get('火',0) else '弱') + '阳' + ('盛' if wx.get('火',0) > wx.get('水',0) else '弱')}"},
        ]

        insights = []
        insights.append(f"七原则核心：{principles[1]}")
        if ts.get("印星", 0) >= 2 and any("冲" in c for c in combos):
            insights.append("心物法则+极性法则=你有通过改变思维来转化对立面的能力")

        warnings = []
        if abs(wx.get('水',0) - wx.get('火',0)) > 30:
            warnings.append("阴阳偏颇——对应法则提醒你需要平衡生命中的对立力量")

        advice = []
        advice.append("如其在上，如其在下——你遇到的问题往往反映了更大的格局问题")
        advice.append("观察最近生活中的'巧合'——赫尔墨斯认为同步性是有意义的")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.55,
            "summary": f"七原则评分{score}分。{'天地人三才对应良好' if len(wx_vals)>=2 and wx_vals[0]-wx_vals[-1]<20 else '对应关系有待调和'}。{'阴阳' + ('平衡' if abs(wx.get('水',0)-wx.get('火',0)) < 15 else '有偏')}。",
            "dimensions": dimensions,
            "key_insights": insights or ["赫尔墨斯视角更偏向哲学诠释，是对其他视角的补充"],
            "warnings": warnings or [], "advice": advice,
        }
