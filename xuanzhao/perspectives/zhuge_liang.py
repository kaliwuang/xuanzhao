#!/usr/bin/env python3
"""
ZhugeLiang
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class ZhugeLiang(Perspective):
    name = "诸葛亮"
    title = "隆中对全局推演"
    
    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        liuyao = f.get("liuyao_str", "")
        planets = "; ".join(f.get("planet_refs", []))
        
        p1 = (
            f"臣观此命盘，如临隆中论天下大势。日主{f['dm_str']}坐于{f['dm_wx']}，"
            f"五行之中{f['strongest']}气最盛、{f['weakest']}气最弱，"
            f"恰似曹孙刘三方之势——各有根基，各有不足。"
            f"调候用神{f['yongshen_str']}，此乃天时，如借得东风便有成事之基。"
        )
        
        chong_text = ""
        if f["chong"]:
            chong_text = (
                f"然观其命局有{f['chong'][0]}，此事非坦途。"
                "冲者，荆州之争也——不可不争，不可恋战。"
                "先取荆州为家、再图益州成业，此臣之策。"
            )
        else:
            chong_text = "命局无冲，根基稳固，如成都已定，可徐徐图之。"
        
        dayun_text = ""
        if f["dayun"].get("ganzhi"):
            d = f["dayun"]
            dayun_text = (
                f"当前{f['dayun_str']}，{'所行与日主同气，此乃借势之时' if d.get('gan_wuxing','')==f['dm_wx'] or d.get('zhi_wuxing','')==f['dm_wx'] else '此运非帮身之运，当以守为主、以逸待劳'}。"
            )
        else:
            dayun_text = "大运未动，如隆中未出——当务之急是等待时机。"
        
        mm_text = ""
        if f["liuyao_str"]:
            mm_text = f"兼观{f['liuyao_str']}，{'与命盘相合，多算者胜' if '合' in f['liuyao_str'] else '卦象提醒——此命不可轻举妄动'}。"
        if planets:
            mm_text += f" 西学观星亦有印证：{planets}。天象地命，合而观之。"
        
        return f"{p1}\n\n{chong_text}\n\n{dayun_text}{' ' + mm_text if mm_text else ''}"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        features = a["features"]
        dayun = a["dayun_phase"]
        combos = a["combinations"]
        
        # 评分逻辑
        score = 50
        
        # 全局视野：五行是否均衡
        wx_vals = sorted(wx.values(), reverse=True)
        balance = wx_vals[0] - wx_vals[-1] if len(wx_vals) >= 2 else 100
        if balance < 20:
            score += 20  # 五行均衡=战略视野开阔
        elif balance < 40:
            score += 10
        
        # 借势能力：月令是否用神到位
        th = a["tiaohou"]
        if th.get("yongshen"):
            yongshen = _GAN_WUXING.get(th["yongshen"][0] if th["yongshen"] else "", "")
            if yongshen and wx.get(yongshen, 0) > 20:
                score += 15  # 用神得力=能借势
            elif yongshen:
                score += 5
        
        # 风险管理：冲刑多=变数多=需谨慎
        if any("冲" in c for c in combos):
            score -= 5  # 有冲=需更多计算变量
        
        # 大运配合
        if dayun:
            d_wx = dayun.get("gan_wuxing", "")
            if d_wx == dm.get("wuxing", ""):
                score += 10  # 大运帮身=顺势
            elif d_wx and wx.get(d_wx, 0) > 15:
                score += 5
        
        score = max(10, min(95, score))
        
        # 维度分析
        dimensions = [
            {
                "name": "格局视野",
                "score": min(100, 50 + int((100 - balance) / 1.5)),
                "detail": f"五行极差{balance:.1f}%——{'多极均衡' if balance < 20 else '一行为主' if balance > 50 else '略有偏重'}，{'全局视野开阔' if balance < 20 else '需有意识地拓展认知边界'}"
            },
            {
                "name": "借势能力",
                "score": min(100, 50 + (15 if th.get("yongshen") and wx.get(_GAN_WUXING.get(th['yongshen'][0] if th['yongshen'] else '',''), 0) > 20 else 0) + (10 if dayun else 0)),
                "detail": f"调候用神{'得力' if th.get('yongshen') and wx.get(_GAN_WUXING.get(th['yongshen'][0] if th['yongshen'] else '',''), 0) > 20 else '偏弱'}，{'大运相助' if dayun else '当前大运待机'}"
            },
            {
                "name": "风险管理",
                "score": max(0, 70 - (10 * sum(1 for c in combos if "冲" in c))),
                "detail": f"命局{'有冲' if any('冲' in c for c in combos) else '无冲'}，{'需多算一层风险' if any('冲' in c for c in combos) else '风险可控'}"
            },
            {
                "name": "持久力",
                "score": min(100, 40 + int(a['daymaster']['support_ratio'])),
                "detail": a['daymaster']['detail']
            },
        ]
        
        # 洞察
        insights = []
        if "子午冲" in str(features) or "午子冲" in str(features):
            insights.append("命局核心矛盾在子午相冲——水火交战，以逸待劳是最好的策略，不要正面硬碰")
        if dm.get("strength") == "身弱":
            insights.append("身弱格局——隆中对式借势而非硬拼，寻找外部杠杆比自我奋斗更重要")
        if any("合" in c for c in combos):
            insights.append("有合局存在——可在联盟与合作中找到突破口，符合'借势而为'原则")
        
        warnings = []
        if any("冲" in c for c in combos):
            warnings.append("冲局如战场——决策需谨慎，避免在矛盾集中领域轻易出手")
        if dm.get("strength") == "身弱" and not dayun:
            warnings.append("身弱而大运未至——当前是积蓄期，不宜大规模出击")
        
        advice = []
        advice.append(f"全局视野评分{score}分——{'借势布局' if score > 60 else '先谋后动'}，当前最优先的是{'抓住' + dayun['ganzhi'] + '运的机会' if dayun else '等待大运转变时的战略窗口'}")
        if any("冲" in c for c in combos):
            advice.append("建议采用'以逸待劳'策略——让矛盾双方消耗，你坐收其利")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.75,
            "summary": f"此命{'格局清晰' if score > 65 else '格局待定'}，{'宜借势布局' if score > 60 else '宜积蓄守势'}。{'多算胜少算' if any('冲' in c for c in combos) else '顺势而为即可'}",
            "dimensions": dimensions,
            "key_insights": insights or ["命局中正，需结合具体问题深入分析"],
            "warnings": warnings or [],
            "advice": advice,
        }

