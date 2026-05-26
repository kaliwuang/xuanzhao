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
        
        # 面具与阴影：最强五行=面具，最弱=阴影
        mask = f['strongest']
        shadow = f['weakest']
        
        mask_desc = {
            "木": "发散、生长、向上——这个人格面具让你看起来永远在追逐新目标",
            "火": "热烈、表达、照亮——你的面具是表演者，总在向外释放能量",
            "土": "厚重、承载、稳定——你展示给世界的是一座山",
            "金": "锐利、决定、边界——你的面具是法官，爱下判断",
            "水": "流动、渗透、适应——你的面具是变色龙，与环境融为一体",
        }
        shadow_desc = {
            "木": "你没有活出来的内在是一棵沉寂的树——需要被看见、被承认才能生长",
            "火": "你压抑的火苗在梦里燃烧——愤怒、热情、原始的创造力被关在笼子里",
            "土": "你拒绝承认自己对稳定和安全的需要——假装飘忽，其实渴望扎根",
            "金": "被你压抑的那部分想要斩断——它需要说'不'",
            "水": "你内在的暗河在涌动——情绪和直觉远比你以为的强大",
        }
        
        mask_text = mask_desc.get(mask, f"面具是「{mask}」")
        shadow_text = shadow_desc.get(shadow, f"阴影是「{shadow}」")
        
        chong_text = ""
        if f["chong"]:
            chong_text = f"再看看これらの冲象——{f['chong'][0]}。这不是坏事，是自性的邀请：只有通过冲突，你才能整合对立面。个体化的道路从来都不是平坦的。"
        else:
            chong_text = f"命局无冲——整合的道路不是通过外部冲突，而是通过内在觉察开始的。"
        
        mm_text = ""
        if f["liuyao_str"]:
            mm_text = f" {f['liuyao_str']}——卦象与原型意象的呼应绝非巧合。"
        
        return f"让我用分析心理学的方式来看这个命盘。\n\n{mask_text}。{shadow_text}。这个人的个体化课题就在面具与阴影之间——不是在两者之间选择，而是在对立中找到超越。\n\n{chong_text}{mm_text}"
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
