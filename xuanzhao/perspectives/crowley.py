#!/usr/bin/env python3
"""
Crowley
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Crowley(Perspective):
    name = "克劳利"
    title = "泰勒玛意志法则"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        th = a["tiaohou"]
        
        score = 50
        
        # 意志力（七杀=执行力）
        ss = a["raw_bazi"].get("shishen", {})
        if "七杀" in ss.get("time", ""):
            score += 20
        if "七杀" in ss.get("month", ""):
            score += 10
        
        # 变通力（食伤=创造力）
        if ts.get("食伤", 0) >= 2:
            score += 10
        
        # 仪式感（印星）
        if ts.get("印星", 0) >= 2:
            score += 10
        
        # 水火平衡（克劳利偏重）
        water = wx.get("水", 0)
        fire = wx.get("火", 0)
        if abs(water - fire) < 15:
            score += 5
        
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "意志力",
                "score": min(100, 50 + (20 if "七杀" in ss.get("time","") else 0) + 10),
                "detail": f"{'七杀透干=强大意志力' if '七杀' in ss.get('time','') else '意志力一般，需要仪式感来增强'}"
            },
            {
                "name": "神圣守护",
                "score": min(100, 30 + 15 * ts.get("印星", 0)),
                "detail": f"印星{ts.get('印星',0)}个——{'有内在精神秩序' if ts.get('印星',0) >= 2 else '需要在外部建立仪式'}"
            },
            {
                "name": "元素平衡",
                "score": min(100, 60 - int(abs(wx.get('水',0) - wx.get('火',0)))),
                "detail": f"水火差{abs(wx.get('水',0)-wx.get('火',0)):.1f}%——{'元素平衡=灵活与稳定的统一' if abs(wx.get('水',0)-wx.get('火',0)) < 15 else '一元素过强需注意平衡'}"
            },
        ]
        
        insights = []
        if "七杀" in ss.get("time", ""):
            insights.append("七杀透干=强大的意志力基础——克劳利会说是'真正的意志'的天然土壤")
        if th.get("yongshen"):
            insights.append(f"用神{th['yongshen']}=你的魔法对应物——在做重要决定前呼唤其能量")
        
        warnings = []
        if "七杀" in ss.get("time", "") and wx.get("水", 0) < 15:
            warnings.append("七杀强而水弱——意志力可能变成强迫性，需要柔性调和")
        
        advice = []
        advice.append(f"建立个人仪式——每天固定时间做同一件事，这是强化意志力的基础训练")
        if wx.get("火", 0) > wx.get("水", 0):
            advice.append("火元素偏旺——需要用水元素柔化意志的刚性")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.55,
            "summary": f"意志法则评分{score}分。{'七杀透干=强大意志' if '七杀' in ss.get('time','') else '意志力适中'}。{'水火' + ('平衡' if abs(wx.get('水',0)-wx.get('火',0)) < 15 else '失衡')}。",
            "dimensions": dimensions,
            "key_insights": insights or ["克劳利视角更适合有明确意志挑战的具体问题"],
            "warnings": warnings or [],
            "advice": advice,
        }
