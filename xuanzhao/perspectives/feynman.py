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
        
        # 「What I cannot create, I do not understand」——费曼
        # 先找到核心机制，其他都是细节
        core = ""
        if "子午冲" in str(features) or "午子冲" in str(features):
            core = "好，这个命的核心矛盾我可以用一句话说清楚：吸收和表达在打架。子午冲——水和火在你身体里来回窜，一边想安静地吸收（就像我在研究一个物理问题时的状态），一边想冲出去表达（像我在黑板上对着学生画图）。顺便一提，物理上说水火不相容，但核聚变就是在极端条件下让它们融合——你的命运也一样。"
        else:
            core = f"让我试着用一个简单的说法来解释这个命局：这是一个「{dm.get('wuxing','?')}」气质的人。最强的五行是「{f['strongest']}」，最弱的是「{f['weakest']}」。就像我常对我的学生说的——如果你不能用简单的语言解释一件事，就说明你还没有真正理解它。所以我的解读也要遵守这个原则。"
        
        balance = ""
        wx_vals = sorted(f['wx'].values(), reverse=True)
        if len(wx_vals) >= 2 and wx_vals[0] - wx_vals[-1] > 40:
            balance = f"五个维度极度不均衡。这让我想起我在《别闹了，费曼先生》里说过的一个故事——我在实验室花了十年研究一个课题，所有人都觉得我疯了。极端不是坏事，不均衡可能就是你的天赋所在。关键要看你能不能找到那个「不均衡中的平衡点」，就像电磁学里的麦克斯韦方程组一样优雅。"
        elif len(wx_vals) >= 2 and wx_vals[0] - wx_vals[-1] < 20:
            balance = "五行分布很均衡。这让你很难被归类，但你也要小心——过于均衡可能意味着你什么都能做一点，但什么都不特别精。我在《费曼物理学讲义》里讲过，一个系统如果所有部分都一样强，那它一定缺乏特征。你需要找到自己真正在乎的东西，然后在那个方向上深入。"
        else:
            balance = "五行有偏但不极端。中性性格的好处是能适应各种环境，坏处是容易随波逐流。记住我常说的一句话：「我不知道」——承认自己不知道，才是一切真正学习的开始。别怕你的命局不特别，特别不特别不是重点，重点是你怎么用它。"
        
        dayun_p = ""
        if f["dayun"].get("ganzhi"):
            d = f["dayun"]
            if d.get('gan_wuxing','') == dm.get('wuxing','') or d.get('zhi_wuxing','') == dm.get('wuxing',''):
                dayun_p = f"当前{f['dayun_str']}，这个运在帮你——就像我在研究曼哈顿计划时那种「状态对了」的感觉。能量在往正确的方向流，适合把之前积累的东西用出来。别浪费，就像别浪费一个好问题一样。"
            else:
                dayun_p = f"当前{f['dayun_str']}，运势不算助身。但你知道吗？我在从事挑战号航天飞机事故调查时，面对的是最糟糕的局势——然而那恰恰是我学到最多东西的时候。逆风局里赢面小，但学到的东西多。这本身就是一种回报。"
        
        mm_p = ""
        if f["liuyao_str"]:
            mm_p = f"哦对了，{f['liuyao_str']}——这个卦象和八字说的其实是同一件事。我在《物理定律的本性》里提到过，自然界在不同尺度上呈现出惊人的相似性。玄学领域也有类似的模式。"
        
        # 加入费曼标志性的"I don't know"诚实
        disclaimer = "当然，以上只是我的解读。我可能全错了。但就像我在加州理工常对学生说的：『科学的价值就在于它可以被证伪。』所以——把我说的一切都当作一个假说，然后用你的生活去检验它。"
        
        return f"{core}\n\n{balance}\n\n{dayun_p}\n\n{mm_p}\n\n{disclaimer}"
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
