#!/usr/bin/env python3
"""
Laozi
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Laozi(Perspective):
    name = "老子"
    title = "道法自然"
    

    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        dm = a["daymaster"]
        
        natural = ""
        if f['th'].get('yongshen'):
            ys_wx = ''
            ys_char = f['th']['yongshen'][0] if f['th']['yongshen'] else ''
            for k, v in {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}.items():
                if ys_char == k:
                    ys_wx = v
                    break
            if ys_wx and f['wx'].get(ys_wx, 0) > 20:
                is_water = (ys_wx == '水')
                if is_water:
                    water_line = "此命天然近道——水之德，柔而克刚、弱而胜强。"
                else:
                    water_line = f"虽非水，但{ys_wx}气已足，「知足者富，强行者有志」——顺其自然即可。"
                natural = (
                    f"调候用神{f['yongshen_str']}，此乃大道在身。"
                    f"{ys_wx}气充盈，不刻意而为，自然顺势。\n\n"
                    f"老子曰：「上善若水。水善利万物而不争，处众人之所恶，故几于道。」\n"
                    f"{water_line}"
                )
            else:
                natural = (
                    f"调候用神{f['yongshen_str']}虽有，但力量{'不充' if ys_wx and f['wx'].get(ys_wx, 0) > 10 else '偏弱'}——\n\n"
                    f"老子曰：「为学日益，为道日损，损之又损，以至于无为。」\n"
                    f"当下最重要的不是加法，而是减法。减去那些不属于你的执念，道自现。"
                )
        else:
            natural = (
                "用神不明——老子摇头曰：「五色令人目盲，五音令人耳聋，五味令人口爽。」\n"
                "现在你面前的路太多，反而是最大的问题。"
                "「少则得，多则惑」——大道至简，回到根本上去。"
            )
        
        water_approach = ""
        water_pct = f['wx'].get('水', 0)
        if water_pct >= 20:
            water_approach = (
                f"水性为{water_pct}%——此命有近道之资。\n"
                f"「天下莫柔弱于水，而攻坚强者莫之能胜」——\n"
                f"水不争而利万物，不争就是最好的争。柔软比刚硬更有力量。"
            )
        else:
            water_approach = (
                f"水性仅{water_pct}%——刚多柔少。\n"
                f"老子云：「天下之至柔，驰骋天下之至坚。无有入无间。」\n"
                f"学会柔软是此生的功课。"
            )
        
        dayun_p = ""
        if f["dayun"].get("ganzhi"):
            d = f["dayun"]
            if d.get('gan_wuxing','') == '水' or d.get('zhi_wuxing','') == '水':
                dayun_p = (
                    f"当前{f['dayun_str']}——此运带水，正是修炼「不争之德」的好时期。\n"
                    f"「反者道之动，弱者道之用」——"
                    f"低谷与高谷本是一体，无常即常。"
                )
            else:
                dayun_p = (
                    f"当前{f['dayun_str']}——\n"
                    f"老子曰：「祸兮福之所倚，福兮祸之所伏。」\n"
                    f"此运非助身也好、助身也罢，皆是大道运行的一环。"
                    f"「致虚极，守静笃」——以不变应万变。"
                )
        else:
            dayun_p = (
                "大运未动。老子曰：「合抱之木，生于毫末；九层之台，起于累土。」\n"
                "千里之行，始于足下。当下即是全部。"
            )
        
        return f"观此命盘，如观流水。\n\n{natural}\n\n{water_approach}\n\n{dayun_p}"
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        combos = a["combinations"]
        ts = a["tenshen"]
        
        score = 50
        
        # 顺势（用神到位）
        th = a["tiaohou"]
        if th.get("yongshen"):
            ys = _GAN_WUXING.get(th["yongshen"][0] if th["yongshen"] else "", "")
            if ys and wx.get(ys, 0) > 20:
                score += 20
        
        # 无为（冲中有静）
        if any("合" in c for c in combos):
            score += 10  # 合=和谐
        
        # 水=上善若水
        if wx.get("水", 0) >= 25:
            score += 10
        if wx.get("水", 0) >= 40:
            score += 5
        
        # 反者道之动（最弱的五行是最大的潜力）
        if wx:
            min_wx = min(wx, key=wx.get)
            if wx.get(min_wx, 0) < 10:
                score += 5
        
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "顺其自然度",
                "score": min(100, 40 + (20 if th.get('yongshen') and wx.get(_GAN_WUXING.get(th['yongshen'][0] if th['yongshen'] else '',''), 0) > 20 else 0)),
                "detail": f"调候用神{'到位=人生阻力小' if th.get('yongshen') and wx.get(_GAN_WUXING.get(th['yongshen'][0] if th['yongshen'] else '',''), 0) > 20 else '偏弱=需主动调整'}"
            },
            {
                "name": "反者道之动",
                "score": min(100, 40 + int(wx.get(min(wx, key=wx.get), 0) < 10) * 20 + 15 * (wx.get("水", 0) >= 25)),
                "detail": f"{'最弱的五行是未来潜力所在' if wx.get(min(wx, key=wx.get), 0) < 10 else '五行相对均衡'}，{'水性特质增加柔韧' if wx.get('水',0) >= 25 else '建议培养水的品质'}"
            },
            {
                "name": "内在平和",
                "score": max(10, 60 - 10 * sum(1 for c in combos if "冲" in c) + 10 * sum(1 for c in combos if "合" in c)),
                "detail": f"命局{'有冲有合，动中有静' if any('冲' in c for c in combos) and any('合' in c for c in combos) else '以合为主，自然和谐' if any('合' in c for c in combos) else '冲象为主，内心不静'}"
            },
        ]
        
        insights = []
        if wx.get("水", 0) >= 25:
            insights.append(f"水性不弱（占{wx['水']}%）——上善若水，这是你最自然的道")
        if th.get("yongshen"):
            insights.append(f"用神{th['yongshen']}——顺势的方向已经很明确了")
        
        warnings = []
        if ts.get("官杀", 0) >= 3:
            warnings.append('官杀过旺——压力太大时会忘掉「无为」的本质')
        
        advice = []
        advice.append(f"反者道之动——你目前最弱的「{min(wx, key=wx.get) if wx else '?'}」反而是未来最大的成长空间")
        if any("冲" in c for c in combos):
            advice.append('内心有冲突时，找到「中」的位置而非选择一方')
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.7,
            "summary": f"道法自然评分{score}分。{'用神得力=顺势而为' if th.get('yongshen') and wx.get(_GAN_WUXING.get(th['yongshen'][0] if th['yongshen'] else '',''), 0) > 20 else '需寻找上善若水的路径'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["命局中庸，不强求是最高明的策略"],
            "warnings": warnings or [],
            "advice": advice,
        }
