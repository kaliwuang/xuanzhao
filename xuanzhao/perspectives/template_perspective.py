#!/usr/bin/env python3
"""
TemplatePerspective
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)
from perspectives_templates import TEMPLATE_PERSPECTIVES

class TemplatePerspective(Perspective):
    """基于模板数据的参数化视角"""

    def __init__(self, pid: str, config: dict):
        self._pid = pid
        self._cfg = config

    @property
    def name(self) -> str:
        return self._cfg["name"]

    @property
    def title(self) -> str:
        return self._cfg["title"]

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        dayun = a["dayun_phase"]
        combos = a["combinations"]
        th = a["tiaohou"]
        c = self._cfg

        score = 50
        for comp in c.get("score_components", []):
            val = self._get_nested(a, comp[0])
            score += val * comp[1]
        if dayun and c.get("boost_dayun"):
            d_wx = dayun.get("gan_wuxing", "")
            dm_wx = dm.get("wuxing", "")
            if d_wx == dm_wx:
                score += 8
            elif d_wx in _WUXING_CYCLE.get(dm_wx, ""):
                score += 5
        if th.get("yongshen") and c.get("boost_yongshen"):
            ys = _GAN_WUXING.get(th["yongshen"][0] if th["yongshen"] else "", "")
            if ys and wx.get(ys, 0) > 20:
                score += 8
        if any("冲" in c2 for c2 in combos) and c.get("boost_chong"):
            score += 8
        if any("合" in c2 for c2 in combos) and c.get("boost_he"):
            score += 8

        score = max(10, min(95, int(score)))

        dimensions = []
        for dim in c.get("dimensions", []):
            dim_score = 50
            for comp in dim.get("components", []):
                dim_score += self._get_nested(a, comp[0]) * comp[1]
            dim_score = max(10, min(100, int(dim_score)))
            dimensions.append({
                "name": dim["name"],
                "score": dim_score,
                "detail": dim.get("high_detail", "").format(**self._fmt(a)) if dim_score >= 60
                          else dim.get("low_detail", "").format(**self._fmt(a))
            })

        insights = []
        insight_key = "high" if score >= 65 else "mid" if score >= 45 else "low"
        insight_templates = c.get("insights", {}).get(insight_key, [])
        if isinstance(insight_templates, str):
            insight_templates = [insight_templates]
        for tpl in insight_templates[:2]:
            try:
                insights.append(tpl.format(**self._fmt(a)))
            except (KeyError, ValueError):
                insights.append(tpl)

        warnings = []
        for warn in c.get("warnings", []):
            field = warn.get("field", "")
            threshold = warn.get("threshold", 20)
            val = self._get_nested(a, field)
            if val < threshold:
                msg = warn.get("msg", "").format(**self._fmt(a))
                warnings.append(msg)

        advice = []
        for adv_tpl in c.get("advice", []):
            try:
                advice.append(adv_tpl.format(**self._fmt(a)))
            except (KeyError, ValueError):
                advice.append(adv_tpl)

        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": c.get("confidence", 0.55),
            "summary": c.get("summary_high", "").format(**self._fmt(a)) if score >= 60
                       else c.get("summary_low", "").format(**self._fmt(a)),
            "dimensions": dimensions[:4],
            "key_insights": insights[:3],
            "warnings": warnings[:2],
            "advice": advice[:2],
        }

    def _get_nested(self, d: dict, path: str):
        parts = path.split(".")
        val = d
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p, 50)
            else:
                return 50
        if isinstance(val, (int, float)):
            return val
        return 50 if val else 0

    def _fmt(self, a: dict) -> dict:
        wx = a["wuxing"]
        ts = a["tenshen"]
        dm = a["daymaster"]
        th = a["tiaohou"]
        dayun = a["dayun_phase"]
        return {
            "日主": dm.get("wuxing", "?"),
            "强弱": dm.get("strength", "中"),
            "用神": th.get("yongshen", "?"),
            "印星": ts.get("印星", 0),
            "比劫": ts.get("比劫", 0),
            "食伤": ts.get("食伤", 0),
            "财星": ts.get("财星", 0),
            "官杀": ts.get("官杀", 0),
            "木": wx.get("木", 0),
            "火": wx.get("火", 0),
            "土": wx.get("土", 0),
            "金": wx.get("金", 0),
            "水": wx.get("水", 0),
            "大运": dayun.get("ganzhi", "?"),
            "大运年": dayun.get("year_index", 1),
        }

    def _build_monologue(self, a: dict) -> str:
        """基于角色的思维框架动态生成独白"""
        f = _fmt_bazi_data(a)
        c = self._cfg
        
        name_prefix = c.get("name_prefix", "以我观之——")
        framework = c.get("framework", "")
        core_q = c.get("core_question", "")
        style = c.get("monologue_style", "哲思")
        quotes = c.get("quotes", [])
        works = c.get("works", [])
        dims = c.get("dimensions", [])
        
        # 维度评分
        dim_lines = []
        for dim in dims[:3]:
            dim_score = 50
            for comp in dim.get("components", []):
                dim_score += self._get_nested(a, comp[0]) * comp[1]
            dim_score = max(10, min(100, int(dim_score)))
            mark = "上" if dim_score >= 70 else "中" if dim_score >= 50 else "下"
            dim_lines.append(f"{dim['name']}（{dim_score}分·{mark}等）")
        dim_str = "；".join(dim_lines)
        
        # 五行/十神数据
        dm_str = f["dm_str"]
        strongest = f["strongest"]
        weakest = f["weakest"]
        yongshen = f["yongshen_str"]
        dayun_str = f["dayun_str"]
        
        # 根据风格生成不同结构的独白
        if style == "君子风":
            body = f"{name_prefix}此命{strongest}盛而{weakest}弱，{dim_str}。{'君子务本，本立而道生——此命根基在此。' if yongshen != '不明' else '修身俟命，无入而不自得。'} "
            if core_q:
                body += f"吾所问者：{core_q} "
            if yongshen != "不明":
                body += f"以{  yongshen}调之，合乎中道。"
                
        elif style == "斗志":
            body = f"{name_prefix}此命{strongest}旺而{weakest}衰。{dim_str}。{'战则胜，守则固' if any('冲' in c2 for c2 in a.get('combinations',[])) else '当先自修而后谋人'}。"
            if core_q:
                body += f"先问：{core_q} "
                
        elif style == "谋略":
            body = f"{name_prefix}观此命局之势——{strongest}盛为阳，{weakest}衰为阴。{dim_str}。{'以奇胜，以正合——谨防一冲之变' if any('冲' in c2 for c2 in a.get('combinations',[])) else '可徐徐图之'}。"
            if core_q:
                body += f"{core_q} 谋定而后动。"
                
        elif style == "哲思":
            body = f"{name_prefix}此命{strongest}之形显，{weakest}之质隐。{dim_str}。{'矛盾乃推动命运之动力' if any('冲' in c2 for c2 in a.get('combinations',[])) else '命理之妙在于平衡'}。"
            if core_q:
                body += f" 我欲追问：{core_q}"
                
        elif style == "务实":
            body = f"{name_prefix}此命{strongest}过{weakest}不及。{dim_str}。{'调候为急' if yongshen != '不明' else '当务之急是补弱扶倾'}。"
            if core_q:
                body += f" 实操之问：{core_q}"
                
        elif style == "预言":
            body = f"{name_prefix}此天命之象已现——{strongest}气盛极，{weakest}气藏渊。{dim_str}。{'冲者变之始也' if any('冲' in c2 for c2 in a.get('combinations',[])) else '静者动之根也'}。"
            if core_q:
                body += f" 我观其兆：{core_q}"
                
        elif style == "狠劲":
            body = f"{name_prefix}{dim_str}。{strongest}太盛则折，{weakest}太弱则废。{'以冰鉴之明，去芜存菁' if yongshen != '不明' else '先活下来再谈别的'}。"
            
        elif style == "激情":
            body = f"{name_prefix}我看到的是——{strongest}在燃烧！{dim_str}。{'这团火，要么烧穿苍穹，要么焚尽自身' if any('冲' in c2 for c2 in a.get('combinations',[])) else '能量需要方向，否则只会照亮虚空'}。"

        elif style == "远见":
            body = f"{name_prefix}立足当下，望向十年后——{strongest}是当下的势，{weakest}是未来的机。{dim_str}。{'冲不可惧，惧在无备' if any('冲' in c2 for c2 in a.get('combinations',[])) else '慢就是快'}。"

        elif style in ("天真", "诗意", "悲悯"):
            body = f"{name_prefix}{dim_str}。{strongest}烈烈如火，{weakest}寂寂如空。{'然则，' + str(core_q) if core_q else ''}"
            
        else:  # 默认
            body = f"{name_prefix}日主{dm_str}，五行{strongest}盛而{weakest}弱。{dim_str}。调候用神{yongshen}。"
        
        # 大运引用
        if f["dayun"].get("ganzhi"):
            body += f"\n\n当前{dayun_str}，顺势而为可也。"
        
        # 引用名言
        if quotes:
            body += f"\n\n如吾所言：「{quotes[0]}」"
        
        # 著作
        if works:
            body += f"\n\n详见{'、'.join(works[:2])}。"
        
        return body

# 生成模板视角
def _load_template_perspectives():
    result = {}
    for pid, cfg in TEMPLATE_PERSPECTIVES.items():
        result[pid] = TemplatePerspective(pid, cfg)
    return result

TEMPLATE_FRAMEWORKS = _load_template_perspectives()

