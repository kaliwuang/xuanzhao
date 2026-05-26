#!/usr/bin/env python3
"""
Feynman
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Feynman(Perspective):
    name = "费曼"
    title = "简化核心机制"
    

    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        dm = a["daymaster"]
        features = a.get("features", [])
        
        core = ""
        if "子午冲" in str(features) or "午子冲" in str(features):
            core = "这个命的核心矛盾就一个：吸收和表达在打架。子午冲——水和火在你身体里来回窜，一边想安静地吸收，一边想冲出去表达。"
        else:
            core = f"说人话：这是一个「{dm.get('wuxing','?')}」气质的命。最强的五行是「{f['strongest']}」，最弱的是「{f['weakest']}」。就这么简单。"
        
        balance = ""
        wx_vals = sorted(f['wx'].values(), reverse=True)
        if len(wx_vals) >= 2 and wx_vals[0] - wx_vals[-1] > 40:
            balance = f"五个维度极度不均衡——就像一个人在实验室花十年研究一个课题。极端不是坏事，看你用在哪。"
        elif len(wx_vals) >= 2 and wx_vals[0] - wx_vals[-1] < 20:
            balance = "五行分布很均衡——这让你很难被归类，但好处是能适应各种环境。"
        else:
            balance = "五行有偏但不极端——算是中性性格，能专注但不能偏执。"
        
        dayun_p = ""
        if f["dayun"].get("ganzhi"):
            d = f["dayun"]
            if d.get('gan_wuxing','') == dm.get('wuxing','') or d.get('zhi_wuxing','') == dm.get('wuxing',''):
                dayun_p = f"当前{f['dayun_str']}，这个运在帮忙——适合把之前学的东西用出来。别浪费。"
            else:
                dayun_p = f"当前{f['dayun_str']}，运势不算助身——意味着你在逆风局里，赢面小但学到的东西多。"
        
        mm_p = ""
        if f["liuyao_str"]:
            mm_p = f"顺便说，{f['liuyao_str']}——卦象和八字说的是同一件事。"
        
        return f"{core}\n\n{balance}\n\n{dayun_p}{' ' + mm_p if mm_p else ''}"
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        features = a["features"]
        
        # 核心问题识别
        core_issues = []
        if "子午冲" in str(features):
            core_issues.append("吸收与表达的根本矛盾（子午冲）")
        if dm.get("strength") == "身弱":
            core_issues.append("精力输出大于输入（身弱格局）")
        
        # 评分：复杂度越低越好（费曼喜欢简单）
        issue_count = len(core_issues)
        combo_complexity = len(a["combinations"])
        if issue_count <= 1 and combo_complexity <= 2:
            score = 75
        elif issue_count <= 2:
            score = 55
        else:
            score = 40
        
        # 命中是否有"简化"的天然能力（印星强=能抽象）
        ts = a["tenshen"]
        if ts.get("印星", 0) >= 2:
            score += 15  # 印星=抽象能力
        if ts.get("食伤", 0) >= 2:
            score += 10  # 食伤=表达能力
        
        score = max(10, min(95, score))
        
        # 第一性原理分析：去掉所有术语
        strongest_wx = max(wx, key=wx.get) if wx else "?"
        weakest_wx = min(wx, key=wx.get) if wx else "?"
        
        dimensions = [
            {
                "name": "核心矛盾清晰度",
                "score": max(10, 80 - 10 * issue_count),
                "detail": f"可识别{issue_count}个核心矛盾——{core_issues[0] if core_issues else '无明显命局冲突'}"
            },
            {
                "name": "抽象思维能力",
                "score": min(100, 50 + 15 * ts.get("印星", 0)),
                "detail": f"印星{'强旺' if ts.get('印星',0) >= 2 else '一般' if ts.get('印星',0) == 1 else '偏弱'}，{'学习者特质明显' if ts.get('印星',0) >= 2 else '抽象能力需要训练'}"
            },
            {
                "name": "自我诚实度",
                "score": max(10, 70 - 10 * sum(1 for c in a["combinations"] if "害" in c)),
                "detail": f"命局{'有害' if any('害' in c for c in a['combinations']) else '无六害'}，{'需注意自我欺骗倾向' if any('害' in c for c in a['combinations']) else '自我认知相对清晰'}"
            },
        ]
        
        insights = []
        if core_issues:
            insights.append(f"说人话：这个命的核心问题就是「{core_issues[0]}」，其他都是衍生")
        if dm.get("wuxing"):
            insights.append(f"去掉所有玄学术语：这是一个「{dm['wuxing']}」气质的命局，过剩的是「{strongest_wx}」，匮乏的是「{weakest_wx}」")
        
        warnings = []
        if ts.get("印星", 0) == 0 and ts.get("食伤", 0) == 0:
            warnings.append("印星食伤皆不显——需要刻意训练思考深度和表达清晰度")
        
        advice = []
        advice.append('第一性原理练习：不断追问「为什么」直到无法再问')
        if dm.get("wuxing") == "木":
            advice.append("木性发散——需要用火（输出）和土（结构化）来落地")
        elif dm.get("wuxing") == "水":
            advice.append("水性渗透——金（逻辑框架）和土（边界）可以有效收束")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.7,
            "summary": f"简化后：这是一个「{dm.get('wuxing','?')}」命局。{'核心矛盾明确' if core_issues else '命局相对简洁'}。{strongest_wx}过旺，{weakest_wx}不足。",
            "dimensions": dimensions,
            "key_insights": insights or ["命局结构简单，无明显冲突，自洽性高"],
            "warnings": warnings or [],
            "advice": advice,
        }
