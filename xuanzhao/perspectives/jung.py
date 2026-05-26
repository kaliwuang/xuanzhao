#!/usr/bin/env python3
"""
Jung
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)

class Jung(Perspective):
    name = "荣格"
    title = "阴影整合与个体化"
    

    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        dm = a["daymaster"]
        ts = a["tenshen"]
        
        # 「Until you make the unconscious conscious, it will direct your life and you will call it fate」——荣格
        # 面具与阴影：最强五行=面具，最弱=阴影
        mask = f['strongest']
        shadow = f['weakest']
        
        mask_desc = {
            "木": "发散、生长、向上。我在《红书》中写过，树象征个体化进程——深入地下的根系是你的本能，伸向天空的枝叶是你的意识。这个人格面具让你看起来永远在追逐新目标，但别忘了：树的生长是缓慢的。",
            "火": "热烈、表达、照亮。你的面具是表演者，总在向外释放能量。荣格在《人格的整合》中提到过，外向型人格的面具往往是他们最自豪的部分，但也恰恰是离自性最远的部分——小心火焰烧伤真实的自己。",
            "土": "厚重、承载、稳定——你展示给世界的是一座山。我在《荣格全集》第七卷中阐述过，土元素对应的是母性原型。你的强大支撑能力让人依赖你，但你自己呢？谁来支撑你？",
            "金": "锐利、决定、边界。你的面具是法官，爱下判断。我在《心理类型》中将这种特质归为思维功能——清晰但有风险：过度的评判会成为你认识自己的障碍。",
            "水": "流动、渗透、适应——你的面具是变色龙，与环境融为一体。但正如我在《人及其象征》中说的：适应能力越强的人，越容易丢失自己的身份。你的自性在哪里？",
        }
        shadow_desc = {
            "木": "你没有活出来的内在是一棵沉寂的树。《红书》中有一章专门讲这棵树——它被遗忘在森林深处，需要被看见、被承认才能生长。和你的阴影对话吧，它比你想象的更有智慧。",
            "火": "你压抑的火苗在梦里燃烧。愤怒、热情、原始的创造力都被关在笼子里。荣格谈过阴影的整合——它不是要你变成火，而是要你承认火的存在。就像我在《回忆·梦·思考》中说的：『孤单并不是因为身边没有人，而是因为无法传达自己内心最重要的东西。』",
            "土": "你拒绝承认自己对稳定和安全的需要——假装飘忽，其实渴望扎根。这是典型的阴影投射。我在分析中发现，最强烈否认的东西，往往就是阴影最深的地方。",
            "金": "被你压抑的那部分想要斩断——它需要说『不』。我在《移情心理学》中描述过，这种阴影往往以破坏性的方式浮现，除非你主动接纳它。金的力量不是用来伤害，而是用来划定边界。",
            "水": "你内在的暗河在涌动。《白乌鸦》中荣格写道：『谁在外部看，就在梦中；谁在内部看，就会醒来。』你的情绪和直觉远比你以为的强大——别怕它们。",
        }
        
        mask_text = mask_desc.get(mask, f"面具是「{mask}」——但在你意识到它之前，它只是命运。")
        shadow_text = shadow_desc.get(shadow, f"阴影是「{shadow}」——荣格说：『人不是通过想象光明的形象而变得开明，而是通过让黑暗变得有意识。』")
        
        chong_text = ""
        if f["chong"]:
            chong_text = f"命局中的沖——{f['chong'][0]}。这恰好印证了我提出的共时性（synchronicity）原理：不是因果关系，而是有意义的巧合。这不是坏事，是自性的邀请。我在《金花的秘密》中说过——只有通过冲突与对立，你才能达到更高的整合。个体化的道路从来不是平坦的康庄大道，而是穿过阴影的险峻山路。"
        else:
            chong_text = "命局无冲——但这不意味着没有阴影工作要做。我在《分析心理学的基本假设》中强调过：整合的道路不一定通过外部冲突，但内在的觉知是必经之路。『你的潜意识就是你的命运。』深究那些让你不舒服的性格特质，那里藏着你的宝藏。"
        
        # 共时性原理
        synchronicity_note = ""
        if f["liuyao_str"]:
            synchronicity_note = f" 我注意到{f['liuyao_str']}——卦象与八字之间的呼应绝非偶然。正如我在《易经》的心理学解读中所说的：『易经的智慧不在于算命，而在于揭示潜意识和外部事件之间的共时性关联。』这本身就是一个有意义的巧合。"
        
        # 加入荣格经典名言
        quote = "最后，让我以《红书》中的一句话作为结语：『每个人背负的阴影越深，他携带的光明也就越强。』"
        
        return f"让我用分析心理学的方式来理解这个命盘——我想引用我在《回忆·梦·思考》中的一段话：『你的潜意识指引着你的人生，而你却称之为命运。』\n\n{mask_text}\n\n{shadow_text}\n\n这个人的个体化课题就在面具与阴影之间——不是在两者之间选择，而是在对立中找到超越。共时的是，这个过程正如《易》所言：『一阴一阳之谓道。』\n\n{chong_text}{synchronicity_note}\n\n{quote}"
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        features = a["features"]
        ts = a["tenshen"]
        
        # 阴影识别：最弱的五行和最强的十神
        max_wx = max(wx, key=wx.get) if wx else "?"
        min_wx = min(wx, key=wx.get) if wx else "?"
        
        # 人格面具（显性性格）
        dm_wx = dm.get("wuxing", "?")
        # 阴影（被压抑的部分）
        shadow = min_wx
        
        score = 50
        # 冲=阴影浮现的契机
        if any("冲" in c for c in a["combinations"]):
            score += 20  # 冲=整合契机
        if any("害" in c for c in a["combinations"]):
            score += 10  # 害=内心冲突
        # 印星=内省能力
        if ts.get("印星", 0) >= 1:
            score += 10
        
        score = max(10, min(95, score))
        
        # 原型识别
        archetypes_map = {
            "木": "探索者/创造者——成长导向，但容易扎根不深",
            "火": "战士/表演者——热情外显，但容易消耗自己",
            "土": "守护者/支撑者——稳定可靠，但容易僵化",
            "金": "智者/审判者——结构清晰，但容易冷漠",
            "水": "疗愈者/追寻者——深度感知，但容易迷失",
        }
        archetype = archetypes_map.get(dm_wx, "未知原型")
        
        dimensions = [
            {
                "name": "阴影整合度",
                "score": min(100, 40 + int(max_wx != min_wx) * 15 + (20 if any("冲" in c for c in a["combinations"]) else 0)),
                "detail": f"人格面具为「{dm_wx}」（显性），阴影为「{shadow}」（被压抑的部分），{'命局有冲=整合契机' if any('冲' in c for c in a['combinations']) else '阴影尚未浮现，需主动探索'}"
            },
            {
                "name": "个体化进程",
                "score": min(100, 30 + int(ts.get("印星",0))*15 + (10 if a['daymaster']['support_ratio'] > 40 else 0)),
                "detail": f"印星{'有力' if ts.get('印星',0) >= 1 else '不足'}，{'内省能力强=个体化进程加速' if ts.get('印星',0) >= 1 else '需更多独处与反思来加速个体化'}"
            },
            {
                "name": "原型能量",
                "score": min(100, 50 + int(wx.get(dm_wx,0) - wx.get(shadow,0))/2),
                "detail": f"当前原型：{archetype}"
            },
        ]
        
        insights = []
        if dm_wx and shadow:
            insights.append(f"人格面具是「{dm_wx}」，但阴影「{shadow}」才是未被活出的潜能——整合这两个对立面是个体化的核心")
        if "子午冲" in str(features):
            insights.append("子午冲象征意识与无意识的激烈碰撞——这正是荣格所说的'英雄与阴影的相遇'")
        
        warnings = []
        if any("害" in c for c in a["combinations"]):
            warnings.append("有六害——内心可能存在自我否定或内耗，需要面对而非逃避")
        
        advice = []
        advice.append(f"试着发展你的阴影「{shadow}」——那是你未活出的力量")
        if ts.get("印星", 0) == 0:
            advice.append("建立定期反思的习惯（日记、冥想、心理咨询），这是个体化的重要工具")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.7,
            "summary": f"人格面具「{dm_wx}」。核心功课：整合阴影「{shadow}」。{'命局冲象=加速个体化' if any('冲' in c for c in a['combinations']) else '个体化需主动探索'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["命局相对和谐，阴影不突出，个体化可循序渐进"],
            "warnings": warnings or [],
            "advice": advice,
        }
