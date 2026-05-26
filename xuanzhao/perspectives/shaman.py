#!/usr/bin/env python3
"""
Shaman
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Shaman(Perspective):
    name = "萨满"
    title = "灵魂旅行与能量"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        combos = a["combinations"]
        
        score = 50
        
        # 水元素=灵性通道
        if wx.get("水", 0) >= 25:
            score += 15
        # 木元素=成长与连接
        if wx.get("木", 0) >= 20:
            score += 10
        # 印星=与更智慧的连接
        if ts.get("印星", 0) >= 2:
            score += 10
        
        # 冲=能量通道不通
        if any("冲" in c for c in combos):
            score -= 5
        # 合=能量整合
        if any("合" in c for c in combos):
            score += 10
        
        score = max(10, min(95, score))
        
        # 力量动物
        animal_map = {
            "木": "鹿（柔韧适应）",
            "火": "狐狸（敏锐机警）",
            "土": "熊（稳重守护）",
            "金": "鹰（高瞻远瞩）",
            "水": "蛇（深沉蜕皮）",
        }
        power_animal = animal_map.get(dm.get("wuxing", ""), "鹿")
        shadow_animal = animal_map.get(min(wx, key=wx.get) if wx else "土", "熊")
        
        dimensions = [
            {
                "name": "灵性通道", "score": min(100, 30 + int(wx.get('水',0))),
                "detail": f"水元素占{wx.get('水',0)}%——{'灵性感知力强' if wx.get('水',0) >= 25 else '灵性通道需要更安静的状态打开'}"
            },
            {
                "name": "能量整合",
                "score": min(100, 50 + (10 if any('合' in c for c in combos) else 0) - (5 if any('冲' in c for c in combos) else 0)),
                "detail": f"命局{'有合有冲=能量在整合与冲突之间' if any('合' in c for c in combos) and any('冲' in c for c in combos) else '有合=能量和谐' if any('合' in c for c in combos) else '有冲=能量有裂痕' if any('冲' in c for c in combos) else '能量相对平稳'}"
            },
            {
                "name": "动物能量",
                "score": min(100, 50 + int(wx.get(max(wx, key=wx.get),0) - wx.get(min(wx, key=wx.get),0)) if wx else 0),
                "detail": f"力量动物：{power_animal}；影子动物：{shadow_animal}"
            },
        ]
        
        insights = []
        if wx.get("水", 0) >= 25:
            insights.append(f"水元素{wx['水']}%——灵性天赋，适合冥想、梦境工作")
        if ts.get("印星", 0) >= 2:
            insights.append("印星=与先祖/更高智慧有天然连接")
        
        warnings = []
        if any("冲" in c for c in combos):
            warnings.append("命局有冲——能量有裂口需要修复仪式")
        
        advice = []
        advice.append(f"与你的力量动物「{power_animal}」连接——在冥想中想象它，学习它的品质")
        if wx.get("水", 0) < 20:
            advice.append("水元素偏弱——多亲近水域（泡澡、游泳、听雨）来加强灵性通道")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.5,
            "summary": f"萨满视角评分{score}分。力量动物：{power_animal}。{'灵性天赋突出' if wx.get('水',0) >= 25 else '灵性需后天开发'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["萨满视角是补充视角，不强依赖命局先天数据"],
            "warnings": warnings or [],
            "advice": advice,
        }
