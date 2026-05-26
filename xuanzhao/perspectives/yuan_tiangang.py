#!/usr/bin/env python3
"""
YuanTiangang
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class YuanTiangang(Perspective):
    name = "袁天罡"
    title = "骨相推命运分段"
    
    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        dm = a["daymaster"]
        
        p1 = (
            f"老夫以骨相法推此命。日主{f['dm_str']}，{dm.get('strength','?')}之格。"
            f"五行{f['strongest']}旺而{f['weakest']}弱，"
            f"此乃{'烈焰外显' if f['strongest'] == '火' else '刚锐外露' if f['strongest'] == '金' else '内秀其中' if f['strongest'] in ('水','木') else '厚德载物'}之相。"
        )
        
        dayun_text = ""
        if f["dayun"].get("ganzhi"):
            d = f["dayun"]
            y = d.get("year_index", 0)
            seg_quality = "黄金期" if 2 <= y <= 5 else "初入期" if y <= 2 else "尾段期"
            dayun_text = (
                f"当前行{f['dayun_str']}，正值此运{seg_quality}。"
                f"{f['dayun_str'].split('运')[0]}气{'助身，顺风顺水' if d.get('gan_wuxing','')==f['dm_wx'] else '非助身之气，需谨慎行事'}。"
            )
        else:
            dayun_text = "大运尚未开启，如璞玉未琢。少年之运，奠基为重。"
        
        mm_text = ""
        if f["liuyao_str"]:
            mm_text = f" 老夫再观{f['liuyao_str']}卦象，{'与骨相相合' if '合' in str(f['combos']) else '以卦象印证骨相之论'}。"
        
        return f"{p1}\n\n{dayun_text}{mm_text}"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        dayun = a["dayun_phase"]
        features = a["features"]
        
        score = 50
        
        # 少年看骨（八字结构质量）
        if dm.get("strength") in ("身强", "中和"):
            score += 15
        if any("合" in c for c in a["combinations"]):
            score += 10
        score -= 5 * sum(1 for c in a["combinations"] if "冲" in c)
        
        # 中年看气（当前大运）
        if dayun:
            d_g = dayun.get("gan_wuxing", "")
            d_z = dayun.get("zhi_wuxing", "")
            dm_wx = dm.get("wuxing", "")
            if d_g == dm_wx or d_z == dm_wx:
                score += 15  # 大运帮身
            elif d_g in _WUXING_CYCLE.get(dm_wx, "") or d_z in _WUXING_CYCLE.get(dm_wx, ""):
                score += 10  # 大运生身
            elif _WUXING_CONQUER.get(d_g) == dm_wx or _WUXING_CONQUER.get(d_z) == dm_wx:
                score -= 10  # 大运克身
                
            # 大运阶段
            yi = dayun.get("year_index", 1)
            if yi <= 3:
                score += 5  # 刚入大运
            elif yi >= 7:
                score -= 3  # 大运末
        
        score = max(10, min(95, score))
        
        # 大运分段分析
        dayun_segments = []
        raw_dayun = a["raw_bazi"].get("dayun", [])
        for d in raw_dayun:
            gz = d["ganzhi"]
            seg = f"{gz}运({d['start']}-{d['end']})"
            if dayun and d["ganzhi"] == dayun["ganzhi"]:
                seg += " ←当前"
            dayun_segments.append(seg)
        
        dimensions = [
            {
                "name": "先天骨相",
                "score": min(100, 50 + (15 if dm.get("strength") in ("身强","中和") else 0) + 10 * sum(1 for c in a["combinations"] if "合" in c)),
                "detail": f"八字{dm.get('strength','?')}格局{'有合' if any('合' in c for c in a['combinations']) else '无特殊合局'}"
            },
            {
                "name": "中年气运",
                "score": min(100, 50 + (15 if dayun and (dayun['gan_wuxing']==dm.get('wuxing','') or dayun['zhi_wuxing']==dm.get('wuxing','')) else 0) - (10 if dayun and (_WUXING_CONQUER.get(dayun.get('gan_wuxing',''))==dm.get('wuxing','') or _WUXING_CONQUER.get(dayun.get('zhi_wuxing',''))==dm.get('wuxing','')) else 0)),
                "detail": f"当前{dayun['ganzhi']}运({dayun['start']}-{dayun['end']})第{dayun['year_index']}年，{'吉' if (dayun.get('gan_wuxing','')==dm.get('wuxing','') or dayun.get('zhi_wuxing','')==dm.get('wuxing','')) else '凶' if (_WUXING_CONQUER.get(dayun.get('gan_wuxing',''))==dm.get('wuxing','') or _WUXING_CONQUER.get(dayun.get('zhi_wuxing',''))==dm.get('wuxing','')) else '平'}运" if dayun else "大运未启动"
            },
            {
                "name": "晚年修为",
                "score": min(100, 30 + int(a["daymaster"]["support_ratio"])),
                "detail": f"当前积累{'充足' if a['daymaster']['support_ratio'] > 50 else '不足'}，{'晚年可享其成' if a['daymaster']['support_ratio'] > 50 else '需早做规划'}"
            },
        ]
        
        insights = []
        if dayun:
            insights.append(f"当前处于{dayun['ganzhi']}运的黄金/关键期（第{dayun['year_index']}年），此运主题为{dayun['gan_wuxing']}气主导")
        if "子午冲" in str(features):
            insights.append("少年至中年为命运转折期——子午冲在日月的格局，25-35岁之间会有重大抉择")
        
        warnings = []
        if dayun and (_WUXING_CONQUER.get(dayun.get('gan_wuxing','')) == dm.get('wuxing','')):
            warnings.append(f"当前{dayun['ganzhi']}运克制日主——宜守不宜攻")
        
        advice = []
        if dayun:
            advice.append(f"{dayun['ganzhi']}运还有{10-dayun['year_index']+1}年——抓紧做与{dayun['gan_wuxing']}五行相关的事")
        advice.append(f"命运分段：少年{('已立骨' if score > 60 else '待重建')}，中年{('正在旺运' if dayun and (dayun.get('gan_wuxing','')==dm.get('wuxing','') or dayun.get('zhi_wuxing','')==dm.get('wuxing','')) else '积蓄期')}")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.8,
            "summary": f"此命{dayun_segments[0] if dayun_segments else '大运未详'}，{'青年发力' if dm.get('strength') in ('中和','身强') else '中年转运'}格局",
            "dimensions": dimensions,
            "key_insights": insights or ["命运分段清晰需结合大运具体分析"],
            "warnings": warnings or [],
            "advice": advice,
        }

