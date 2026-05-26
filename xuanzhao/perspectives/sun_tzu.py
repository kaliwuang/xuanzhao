#!/usr/bin/env python3
"""
SunTzu
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class SunTzu(Perspective):
    name = "孙子"
    title = "知己知彼五事七计"


    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        dm = a["daymaster"]
        ts = a["tenshen"]
        combos = a["combinations"]
        
        # 五事评估
        ys_ok = '到位' if f['th'].get('yongshen') else '未显'
        dy_ok = (f['dayun'].get('ganzhi') and 
                 (f['dayun'].get('gan_wuxing','')==f['dm_wx'] or f['dayun'].get('zhi_wuxing','')==f['dm_wx']))
        dao = f"道：调候用神{ys_ok}，方向{'已明' if f['th'].get('yongshen') else '待定'}"
        tian = f"天：当前{'运势可借' if dy_ok else '宜待时而动'}"
        
        wx_vals = sorted(f['wx'].values(), reverse=True)
        if len(wx_vals) >= 2 and wx_vals[0] - wx_vals[-1] < 30:
            di = "地：五行均衡，攻守兼备，适应多线作战"
        else:
            di = f"地：五行偏枯，{f['strongest']}过旺而{f['weakest']}不足——环境选择决定成败"
        
        has_bi = ts.get('比劫',0) >= 1
        has_guan = ts.get('官杀',0) >= 1
        if has_bi and has_guan:
            general = "将：比劫官杀俱全，可为大将"
        elif has_bi or has_guan:
            general = "将：有统兵之资，尚需磨炼"
        else:
            general = "将：统兵之力待磨炼，宜先为副手"
        rule = f"法：{'纪律为本' if ts.get('印星',0)>=1 else '纪律柔性，需以战养战'}"
        
        p1 = f"用孙子五事七计来推演此命。\n\n{dao}。\n{tian}。\n{di}。\n{general}。\n{rule}。"
        
        strategy = ""
        if f["chong"]:
            strategy = f"命局有冲——兵法云：'先为不可胜，以待敌之可胜'。当前宜守不宜攻，让矛盾消耗对手而不是消耗自己。"
        elif ts.get("食伤", 0) >= 2:
            strategy = "食伤旺而出奇——'以正合，以奇胜'是你的天然打法。"
        else:
            strategy = "五事之中无一短板，也无突出长板——当以'不战而屈人之兵'为最高原则。"
        
        mm_text = ""
        if f["liuyao_str"]:
            mm_text = f" {f['liuyao_str']}——卦象与兵法的契合，不是巧合。"
        
        return f"{p1}\n\n{strategy}\n\n{mm_text}" if mm_text else f"{p1}\n\n{strategy}"
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        combos = a["combinations"]
        dayun = a["dayun_phase"]

        # 五事：道(方向)天(时机)地(环境)将(能力)法(纪律)
        score = 50
        # 道：用神到位
        th = a["tiaohou"]
        if th.get("yongshen"):
            ys = _GAN_WUXING.get(th["yongshen"][0] if th["yongshen"] else "", "")
            if ys and wx.get(ys, 0) > 20:
                score += 15
        # 天：大运配合
        if dayun:
            d_wx = dayun.get("gan_wuxing", "")
            dm_wx = dm.get("wuxing", "")
            if d_wx == dm_wx:
                score += 10
            elif d_wx in _WUXING_CYCLE.get(dm_wx, ""):
                score += 5
        # 地：五行均衡
        wx_vals = sorted(wx.values(), reverse=True)
        if len(wx_vals) >= 2 and wx_vals[0] - wx_vals[-1] < 30:
            score += 10
        # 将：比劫+官杀=领导力
        if ts.get("比劫", 0) >= 1:
            score += 5
        if ts.get("官杀", 0) >= 1:
            score += 5
        # 法：印星=纪律
        if ts.get("印星", 0) >= 1:
            score += 5

        score = max(10, min(95, score))

        # 七计评估
        seven_items = []
        seven_items.append(f"道（方向）：{'用神' + th['yongshen'] + '到位，方向明确' if th.get('yongshen') and wx.get(_GAN_WUXING.get(th['yongshen'][0] if th['yongshen'] else '',''), 0) > 20 else '方向待定'}")
        seven_items.append(f"天（时机）：{'当前' + dayun['ganzhi'] + '运助身' if dayun and (dayun.get('gan_wuxing','')==dm.get('wuxing','') or dayun.get('zhi_wuxing','')==dm.get('wuxing','')) else '大运势平，待时而动' if dayun else '天时未至'}")
        seven_items.append(f"地（环境）：{'五行均衡，适应力强' if len(sorted(wx.values(), reverse=True)) >= 2 and sorted(wx.values(), reverse=True)[0]-sorted(wx.values(), reverse=True)[-1] < 30 else '五行偏枯，环境选择很重要'}")
        seven_items.append(f"将（能力）：{'比劫官杀俱全，文武兼备' if ts.get('比劫',0)>=1 and ts.get('官杀',0)>=1 else '领导力'+('有' if ts.get('比劫',0)>=1 or ts.get('官杀',0)>=1 else '待锻炼')}")
        seven_items.append(f"法（纪律）：{'有印星，能守规矩' if ts.get('印星',0)>=1 else '纪律性需要后天培养'}")

        dimensions = [
            {"name": "战略位置", "score": score,
             "detail": f"五事评分{score}分——{'天时地利人和俱全' if score >= 70 else '有优势也有短板'}"},
            {"name": "进攻能力", "score": min(100, 40 + 15*ts.get("官杀",0) + 10*int(dayun and (dayun.get('gan_wuxing','')==dm.get('wuxing','') or dayun.get('zhi_wuxing','')==dm.get('wuxing','')))),
             "detail": f"{'七杀有力=进攻型' if ts.get('官杀',0)>=1 else '需加强出击力度'}"},
            {"name": "防守能力", "score": min(100, 40 + 15*ts.get("印星",0) + 15*ts.get("比劫",0)),
             "detail": f"{'比印有根=防守稳固' if ts.get('印星',0)>=1 or ts.get('比劫',0)>=1 else '防守薄弱，需建立防线'}"},
            {"name": "知彼能力", "score": min(100, 30 + 15*ts.get("财星",0) + 15*ts.get("食伤",0)),
             "detail": f"{'财食有透=容易洞察外部信息' if ts.get('财星',0)>=1 or ts.get('食伤',0)>=1 else '外部感知需提升'}"},
        ]

        insights = []
        if any("冲" in c for c in combos):
            insights.append("命局有冲——孙子会说'避实击虚'，不要在冲突中心硬碰硬，找对方的弱点打")
        if ts.get("官杀", 0) >= 2 and ts.get("印星", 0) == 0:
            insights.append("官杀重而无印——身陷重围之势，需要'先为不可胜以待敌之可胜'")

        warnings = []
        if ts.get("印星", 0) == 0 and ts.get("比劫", 0) == 0:
            warnings.append("无印无比——孤军奋战，切记'不战而屈人之兵'才是上策")

        advice = []
        advice.append(f"孙子五事：{seven_items[0]}")
        if ts.get("食伤", 0) >= 2:
            advice.append("食伤旺——适合以奇胜，出奇制胜是你的优势打法")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.7,
            "summary": f"五事评分{score}分。{'可战' if score >= 60 else '宜守'}之势。{'知彼知己' if ts.get('财星',0)>=1 or ts.get('食伤',0)>=1 else '先修内功再出击'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["五事综合评价，宜结合具体问题深入分析"],
            "warnings": warnings or [], "advice": advice,
        }
