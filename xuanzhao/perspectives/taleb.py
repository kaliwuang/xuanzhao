#!/usr/bin/env python3
"""
Taleb
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Taleb(Perspective):
    name = "Taleb"
    title = "反脆弱与黑天鹅"
    

    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        dm = a["daymaster"]
        ts = a["tenshen"]
        
        p1 = f"用反脆弱思维来压力测试这个命盘。日主{f['dm_str']}，五行{f['strongest']}最旺、{f['weakest']}最弱。这告诉我两件事：一是你有明确的脆弱面——{f['weakest']}的不足是你的阿喀琉斯之踵；二是你的抗压机制——{f['strongest']}是你的冗余储备。"
        
        chong_taleb = ""
        if f["chong"]:
            chong_taleb = f"命局有{f['chong'][0]}——我喜欢这个。冲象意味着系统在波动中可能实现跃迁。大多数人害怕不确定性，但反脆弱系统的特点恰恰是：越冲击，越强大。"
        else:
            chong_taleb = "命局无冲——稳定是好的，但稳定也是一种脆弱。因为没有经过压力测试的系统，你不知道它什么时候会突然崩溃。"
        
        strategy = ""
        if ts.get("七杀", 0) >= 1 or ts.get("官杀", 0) >= 1:
            strategy = "七杀透干——你的命局自带压力测试仪。过度补偿策略：在七杀所代表的领域主动加码，让压力成为你的训练场。"
        elif ts.get("印星", 0) >= 2:
            strategy = "印星厚重——你有足够的缓冲区。但注意：缓冲区不是护城河，真正的反脆弱来自从错误中获利，而不是躲在安全区。"
        else:
            strategy = "中庸之局——没有突出优势，也没有致命弱点。在这种情况下，巴菲特的建议反而更有用：用冗余对抗黑天鹅。"
        
        return f"{p1}\n\n{chong_taleb}\n\n{strategy}"
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        combos = a["combinations"]
        ts = a["tenshen"]
        
        # 反脆弱性评估
        score = 50
        
        # 先天反脆弱特质
        # 冲=暴露于波动=可能反脆弱
        if any("冲" in c for c in combos):
            score += 15  # 冲=脆弱的反面是反脆弱
        # 合局=稳定性=反脆弱能力弱
        if any("合" in c for c in combos):
            score -= 5
        
        # 印星=保护层
        if ts.get("印星", 0) >= 2:
            score += 10
        elif ts.get("印星", 0) == 0:
            score -= 10  # 无印=缺乏保护
        
        # 七杀=压力测试
        ss = a["raw_bazi"].get("shishen", {})
        if "七杀" in ss.get("time", "") or "七杀" in ss.get("month", ""):
            score += 10  # 七杀=反脆弱训练
        
        # 五行均衡度
        wx_vals = sorted(wx.values(), reverse=True)
        if len(wx_vals) >= 2:
            gap = wx_vals[0] - wx_vals[-1]
            if gap < 15:
                score += 10  # 均衡=冗余大
            elif gap > 50:
                score -= 5  # 偏枯=脆弱
        
        score = max(10, min(95, score))
        
        # 杠铃策略
        has_redundancy = ts.get("比劫", 0) >= 1 or ts.get("印星", 0) >= 1
        
        dimensions = [
            {
                "name": "反脆弱指数",
                "score": score,
                "detail": f"命局{'频繁暴露于冲突' if any('冲' in c for c in combos) else '相对平稳'}，{'有从波动中获利' if any('冲' in c for c in combos) else '更善于在稳定中发展'}的特质"
            },
            {
                "name": "冗余保护",
                "score": min(100, 40 + 20 * int(has_redundancy)),
                "detail": f"{'有冗余保护（比劫/印星）' if has_redundancy else '缺乏冗余——遇到极端事件时缓冲空间小'}"
            },
            {
                "name": "凸性策略空间",
                "score": min(100, 50 + (15 if "七杀" in ss.get("time","") else 0) + (10 if ts.get("食伤",0) >= 2 else 0)),
                "detail": f"{'七杀压力=凸性训练' if '七杀' in ss.get('time','') else '压力不足，需主动制造适度风险'}"
            },
        ]
        
        insights = []
        if any("冲" in c for c in combos):
            insights.append("命局有冲=脆弱的反面——这正是反脆弱的土壤，适合在压力中进化")
        if ts.get("印星", 0) == 0:
            insights.append("缺乏印星保护——这是最大的脆弱点，需要建立外部支持系统")
        
        warnings = []
        if ts.get("印星", 0) == 0:
            warnings.append("无印星支持=抗冲击能力弱——需建立安全垫")
        
        advice = []
        advice.append("杠铃策略：90%稳定+10%高风险高回报——不要把中间地带")
        if any("冲" in c for c in combos):
            advice.append("利用冲突区——别人恐惧时就是你的机会")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.7,
            "summary": f"反脆弱评分{score}分。{'有从波动中获利的潜力' if score > 60 else '更适应稳定环境'}。{'七杀透干=高压测试通过' if '七杀' in ss.get('time','') else '反脆弱训练不足'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["命局反脆弱特质不突出，后天选择比先天更重要"],
            "warnings": warnings or [],
            "advice": advice,
        }
