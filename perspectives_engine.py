#!/usr/bin/env python3
"""
玄照 · 深度视角引擎
将每个视角从 prompt 模板升级为基于真实命盘数据的结构化分析。

每个视角分析协议：
{
  perspective: str,      # 视角名
  title: str,            # 副标题
  score: int,            # 0-100 综合评分
  confidence: float,     # 0-1 置信度
  summary: str,          # 一句核心判断
  dimensions: [{name, score, detail}],  # 分析维度
  key_insights: [str],   # 关键洞察
  warnings: [str],       # 风险预警
  advice: [str]          # 行动建议
}
"""

from typing import Optional
from abc import ABC, abstractmethod

# 模板视角数据（78个批量生成视角）
from perspectives_templates import TEMPLATE_PERSPECTIVES


# ==========================================
# 公用分析函数
# ==========================================

def safe_get(d: dict, *keys, default=""):
    """安全嵌套取值"""
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, {})
        else:
            return default
    return d if d else default


_GAN_WUXING = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
               "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
_ZHI_WUXING = {"寅":"木","卯":"木","巳":"火","午":"火",
               "辰":"土","戌":"土","丑":"土","未":"土",
               "申":"金","酉":"金","亥":"水","子":"水"}
_WUXING_CYCLE = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
_WUXING_CONQUER = {"木":"土","土":"水","水":"火","火":"金","金":"木"}
_WUXING_COLORS = {"木":"绿色","火":"红色","土":"黄色","金":"白色","水":"黑色"}


def calc_wuxing_distribution(bazi: dict) -> dict:
    """计算五行分布百分比（含藏干 weighting 0.5）"""
    counts = {"木":0.0, "火":0.0, "土":0.0, "金":0.0, "水":0.0}
    pillars = ["year", "month", "day", "time"]
    ba = bazi.get("bazi", {})
    hg = bazi.get("hidden_gans", {})

    for p in pillars:
        pillar = ba.get(p, "")
        if len(pillar) >= 2:
            g, z = pillar[0], pillar[1]
            if g in _GAN_WUXING:
                counts[_GAN_WUXING[g]] += 1.0
            if z in _ZHI_WUXING:
                counts[_ZHI_WUXING[z]] += 1.0
        # 藏干
        h = hg.get(p, [])
        if isinstance(h, list):
            for ch in h:
                if ch in _GAN_WUXING:
                    counts[_GAN_WUXING[ch]] += 0.5
        elif isinstance(h, str) and h:
            for ch in h.replace(" ", "").replace(",", ""):
                if ch in _GAN_WUXING:
                    counts[_GAN_WUXING[ch]] += 0.5

    total = sum(counts.values())
    if total <= 0:
        return {k:0.0 for k in counts}
    return {k: round(v/total*100, 1) for k, v in counts.items()}


def calc_tenshen_strength(bazi: dict) -> dict:
    """计算十神力量分布"""
    ss = bazi.get("shishen", {})
    result = {"比劫":0, "印星":0, "食伤":0, "财星":0, "官杀":0}
    pillars = ["year", "month", "day", "time"]
    for p in pillars:
        v = ss.get(p, "")
        if "比" in v or "劫" in v:
            result["比劫"] += 1
        if "印" in v:
            result["印星"] += 1
        if "食" in v or "伤" in v:
            result["食伤"] += 1
        if "财" in v:
            result["财星"] += 1
        if "官" in v or "杀" in v:
            result["官杀"] += 1
    return result


def check_dayun_phase(dayun: list, current_year: int = 2026) -> dict:
    """分析当前大运阶段"""
    for d in dayun:
        if d["start"] <= current_year <= d["end"]:
            gz = d["ganzhi"]
            g = gz[0] if gz else ""
            z = gz[1] if len(gz) > 1 else ""
            return {
                "ganzhi": gz,
                "start": d["start"],
                "end": d["end"],
                "year_index": current_year - d["start"] + 1,
                "gan_wuxing": _GAN_WUXING.get(g, "?"),
                "zhi_wuxing": _ZHI_WUXING.get(z, "?"),
            }
    return {}


def check_combinations(bazi: dict) -> list:
    """检测冲刑害合"""
    result = []
    ba = bazi.get("bazi", {})
    pillars = [("year", "月"), ("month", "月"), ("day", "日"), ("time", "时")]
    zhi_map = {}
    for key, label in pillars:
        v = ba.get(key, "")
        if len(v) > 1:
            zhi_map[label] = v[1]

    # 六冲
    chong_pairs = [
        ("子","午"), ("丑","未"), ("寅","申"),
        ("卯","酉"), ("辰","戌"), ("巳","亥"),
    ]
    for (a, b) in chong_pairs:
        positions = [k for k, v in zhi_map.items() if v in (a, b)]
        if len(positions) >= 2:
            result.append(f"{a}{b}冲：{'与'.join(positions)}相冲")

    # 三合/半合
    he_groups = [
        (["寅","午","戌"], "火局"), (["巳","酉","丑"], "金局"),
        (["申","子","辰"], "水局"), (["亥","卯","未"], "木局"),
    ]
    zhi_list = list(zhi_map.values())
    for trio, name in he_groups:
        present = [z for z in trio if z in zhi_list]
        if len(present) >= 2:
            result.append(f"{''.join(present)}半合{name}")

    # 六合
    liuhe = {
        "子丑":"土","寅亥":"木","卯戌":"火",
        "辰酉":"金","巳申":"水","午未":"日月合"
    }
    for (a, b), element in liuhe.items():
        if a in zhi_list and b in zhi_list:
            result.append(f"{a}{b}六合{''.join(element)}")

    return result




def _fmt_bazi_data(a: dict) -> dict:
    """从 analytics 中提取格式化后的八字关键数据，供视角独白引用"""
    wx = a.get("wuxing", {})
    dm = a.get("daymaster", {})
    ts = a.get("tenshen", {})
    combos = a.get("combinations", [])
    dayun = a.get("dayun_phase", {})
    th = a.get("tiaohou", {})
    features = a.get("features", [])
    mm = a.get("multi_metaphysics", {})
    
    # 五行排序
    wx_sorted = sorted(wx.items(), key=lambda x: -x[1])
    strongest = wx_sorted[0][0] if wx_sorted else "?"
    weakest = wx_sorted[-1][0] if len(wx_sorted) > 1 else "?"
    
    # 冲刑合简写
    chong = [c for c in combos if "冲" in c]
    he = [c for c in combos if "合" in c]
    
    # 用神
    ys = th.get("yongshen", "")
    yongshen_str = f"《{ys}》" if ys else "不明"
    
    # 日主
    dm_wx = dm.get("wuxing", "?")
    dm_gan = a.get("raw_bazi", {}).get("day_master", {}).get("gan", "?")
    dm_str = f"{dm_gan}{dm_wx}"
    
    # 大运
    if dayun and dayun.get("ganzhi"):
        dayun_str = f"{dayun['ganzhi']}运（{dayun.get('start','?')}-{dayun.get('end','?')}）第{dayun.get('year_index','?')}年"
    else:
        dayun_str = "大运尚未启动"
    
    # 七术引用
    liuyao = mm.get("liuyao", {})
    liuren = mm.get("liuren", {})
    qimen = mm.get("qimen", {})
    astrology = mm.get("astrology", {})
    
    liuyao_str = f"六爻得《{liuyao.get('hexagram','?')}》卦" if liuyao and "error" not in liuyao and liuyao.get("hexagram") else ""
    liuren_str = f"大六壬{liuren.get('day','?')}日课" if liuren and "error" not in liuren else ""
    
    # 占星关键行星
    planet_refs = []
    if astrology and "error" not in astrology:
        planets = astrology.get("planets", {})
        for pname in ["太阳", "月亮", "水星", "金星", "火星", "木星", "土星"]:
            if pname in planets:
                p = planets[pname]
                planet_refs.append(f"{pname}在{p['sign']}{p['degree']}°")
    
    return {
        "wx": wx, "dm": dm, "ts": ts, "combos": combos,
        "dayun": dayun, "th": th, "features": features,
        "strongest": strongest, "weakest": weakest,
        "yongshen_str": yongshen_str, "dm_str": dm_str, "dm_wx": dm_wx,
        "dayun_str": dayun_str,
        "liuyao_str": liuyao_str, "liuren_str": liuren_str,
        "planet_refs": planet_refs[:3],  # 最多3个行星
        "chong": chong, "he": he,
        "mm": mm,
    }

def calc_daymaster_rating(bazi: dict) -> dict:
    """评断日主强弱"""
    wuxing = calc_wuxing_distribution(bazi)
    dm = bazi.get("day_master", {})
    dm_wuxing = dm.get("wuxing", "?")
    
    if dm_wuxing not in wuxing:
        return {"strength": "不明", "self_ratio": 0, "enemy_ratio": 0}
    
    # 同我生者（比劫+印）vs 克我耗我（官杀+财+食伤）
    # 简化：看我五行占比
    self_ratio = wuxing.get(dm_wuxing, 0)
    
    # 生我的五行
    mother = {v:k for k,v in _WUXING_CYCLE.items()}.get(dm_wuxing, "?")
    mother_ratio = wuxing.get(mother, 0) if mother != "?" else 0
    
    total = self_ratio + mother_ratio
    
    if total >= 50:
        strength = "身强"
    elif total >= 35:
        strength = "中和"
    else:
        strength = "身弱"
    
    return {
        "strength": strength,
        "self_ratio": round(self_ratio, 1),
        "support_ratio": round(total, 1),
        "wuxing": dm_wuxing,
        "detail": f"日主{dm_wuxing}占比{self_ratio}%，生扶五行共{total}%" if dm_wuxing != "?" else "日主不明"
    }


def get_all_analytics(destiny: dict) -> dict:
    """获取所有分析数据，供各视角使用"""
    bazi = destiny.get("bazi", {})
    features = destiny.get("features", [])
    tiaohou = destiny.get("tiaohou", {})
    dayun = bazi.get("dayun", [])

    result = {
        "wuxing": calc_wuxing_distribution(bazi),
        "tenshen": calc_tenshen_strength(bazi),
        "dayun_phase": check_dayun_phase(dayun),
        "combinations": check_combinations(bazi),
        "daymaster": calc_daymaster_rating(bazi),
        "features": features,
        "tiaohou": tiaohou,
        "raw_bazi": bazi,
        "multi_metaphysics": {},
    }

    # 集成七术
    try:
        from multi_metaphysics import get_metaphysics
        meta = get_metaphysics(
            destiny.get("birth", ""),
            destiny.get("location", ""),
            destiny.get("gender", "男"),
        )
        # 只保留非八字部分
        for k in ["liuyao", "liuren", "qimen", "taiyi", "astrology"]:
            if k in meta and isinstance(meta[k], dict) and "error" not in meta[k]:
                result["multi_metaphysics"][k] = meta[k]
    except Exception:
        pass

    return result


# ==========================================
# 抽象视角基类
# ==========================================

class Perspective(ABC):
    """视角基类——每个视角实现自己的analyze方法"""
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def title(self) -> str: ...
    
    @abstractmethod
    def analyze(self, data: dict, analytics: dict) -> dict:
        """返回分析结果字典"""
        ...
    
    def _build_monologue(self, a: dict) -> str:
        """默认独白生成器——子类可覆盖以提供更个性化的口吻"""
        f = _fmt_bazi_data(a)
        combos = a.get("combinations", [])
        dm = a.get("daymaster", {})
        
        # 从视角名称判断风格前缀
        name_style = {
            "老子": "观此命盘，如观流水。",
            "王阳明": "格物致知，此命可格。",
            "斯多葛": "控制二分法看此命——",
            "克劳利": "以意志法则审视此命盘——",
            "弗洛伊德": "让我潜入潜意识的深海。",
            "萨满": "灵眼初开，观此命之灵魂能量——",
            "尼采": "用锤子检验此命盘——",
            "巴菲特": "用价值投资的眼光看这个命局——",
            "巴菲特": "用价值投资的眼光看这个命局——",
            "赫尔墨斯": "上下呼应——此命暗合赫尔墨斯七原则。",
            "张一鸣": "用算法思维拆解这个命局——",
        }
        
        prefix = "待我详观此命——"
        for k, v in name_style.items():
            if k in self.name:
                prefix = v
                break
        
        dm_wx = dm.get("wuxing", "?")
        dm_str = f["dm_str"]
        # get gan from raw data for the prefix
        dm_gan_raw = a.get("raw_bazi", {}).get("day_master", {}).get("gan", "?")
        strength = dm.get("strength", "?")
        
        p1 = f"{prefix}日主{dm_str}，{strength}格局。五行{f['strongest']}旺而{f['weakest']}弱，{'冲合并见' if f['chong'] and f['he'] else '有冲无合' if f['chong'] else '有合无冲' if f['he'] else '无特殊冲合'}。调候用神{f['yongshen_str']}，{'得力' if f['th'].get('yongshen') else '偏弱'}。"
        
        p2 = ""
        if f["dayun"].get("ganzhi"):
            p2 = f"当前{f['dayun_str']}，{'运势助身' if f['dayun'].get('gan_wuxing','') == dm_wx or f['dayun'].get('zhi_wuxing','') == dm_wx else '运势平缓，蓄力待发'}。"
        
        p3 = ""
        if f["liuyao_str"]:
            p3 = f"此外，{f['liuyao_str']}，卦象在此可作为辅助印证。"
        
        return f"{p1}\n\n{p2}\n\n{p3}"


# ==========================================
# 视角一：诸葛亮 · 全局战略推演
# ==========================================

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


# ==========================================
# 视角二：袁天罡 · 命运分段论
# ==========================================

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


# ==========================================
# 视角三：费曼 · 简化核心机制
# ==========================================

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


# ==========================================
# 视角四：荣格 · 阴影与个体化
# ==========================================

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


# ==========================================
# 视角五：芒格 · 逆向思维与误判
# ==========================================

class Munger(Perspective):
    name = "芒格"
    title = "逆向思维多元模型"
    

    def _build_monologue(self, a: dict) -> str:
        f = _fmt_bazi_data(a)
        dm = a["daymaster"]
        ts = a["tenshen"]
        
        # 芒格式：先看坑
        pitfalls = []
        if not f['th'].get('yongshen'):
            pitfalls.append("调候用神不显——容易在不适合自己的方向上死磕")
        if f["chong"]:
            pitfalls.append(f"{f['chong'][0]}——内耗是最大成本，得花时间处理内在矛盾")
        if ts.get("财星", 0) == 0 and ts.get("食伤", 0) == 0:
            pitfalls.append("财星食伤皆不显——对市场/外部环境的感知力偏弱")
        if dm.get("strength") == "身弱" and ts.get("印星", 0) == 0:
            pitfalls.append("身弱无印——'自我'的边界不够清晰，容易被外界带偏")
        
        if pitfalls:
            p1 = f"逆向思考：先不看这个命局能做什么，先看它容易在哪摔跤。我发现了{len(pitfalls)}个潜在陷阱："
            for p in pitfalls:
                p1 += f"\n- {p}"
        else:
            p1 = "逆向检查没有发现明显陷阱——命局结构合理，但这本身也是一种风险：没有明显问题的人往往对问题缺乏警觉。"
        
        p2 = ""
        if ts.get("印星", 0) >= 1:
            p2 = f"好在印星显现有{ts['印星']}处——学习能力是你的护城河。芒格说的'多学科思维模型'，印星就是你的工具箱。"
        else:
            p2 = "印星不显——缺少天然的'学习习惯'。这不是致命伤，但意味着你需要刻意建立知识框架。"
        
        p3 = ""
        if f["dayun"].get("ganzhi"):
            d = f["dayun"]
            if d.get('gan_wuxing','') == dm.get('wuxing','') or d.get('zhi_wuxing','') == dm.get('wuxing',''):
                p3 = f"当前{f['dayun_str']}——这个运帮身，是少犯错、多积累的好时机。芒格说一辈子只需做对几次关键决策就够了。"
            else:
                p3 = f"当前{f['dayun_str']}——运势不帮身，更要慢下来少犯错。记住：不做什么比做什么重要。"
        
        return f"{p1}\n\n{p2}\n\n{p3}"
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        features = a["features"]
        ts = a["tenshen"]
        combos = a["combinations"]
        
        # 逆向：先找最可能踩的坑
        pitfalls = []
        
        # 印星过多=纸上谈兵
        if ts.get("印星", 0) >= 3:
            pitfalls.append("印星过旺——理论与实践脱节的风险")
        # 食伤过旺=不切实际
        if ts.get("食伤", 0) >= 3:
            pitfalls.append("食伤过旺——创意丰富但落地困难")
        # 财星旺但比劫弱=守不住
        if ts.get("财星", 0) >= 2 and ts.get("比劫", 0) == 0:
            pitfalls.append("财旺无劫——有机会但不一定能守住")
        # 官杀混杂
        if ts.get("官杀", 0) >= 2:
            pitfalls.append("官杀混杂——多重压力下的决策瘫痪风险")
        
        score = 50
        if len(pitfalls) <= 1:
            score += 20  # 坑少=明智
        elif len(pitfalls) <= 2:
            score += 10
        
        # 印星=学习能力（芒格看重这个）
        if ts.get("印星", 0) >= 2:
            score += 15
        elif ts.get("印星", 0) == 1:
            score += 5
        
        # 冲=冒险倾向（双刃剑）
        if any("冲" in c for c in combos):
            score += 5  # 勇气加分
            score -= 5  # 冲动减分
        
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "逆向思维力",
                "score": min(100, 50 + 15 * (len(pitfalls) > 0)),
                "detail": f"识别{len(pitfalls)}个潜在陷阱——{'知道避什么比知道追什么更重要' if pitfalls else '命局无明显陷阱'}"
            },
            {
                "name": "跨学科学习力",
                "score": min(100, 40 + 15 * ts.get("印星", 0)),
                "detail": f"印星{ts.get('印星',0)}个——{'多元思维模型的基础不错' if ts.get('印星',0) >= 2 else '需要刻意拓展知识面' if ts.get('印星',0) == 1 else '亟待建立跨学科框架'}"
            },
            {
                "name": "情绪管理",
                "score": max(10, 70 - 10 * ts.get("官杀", 0)),
                "detail": f"官杀{ts.get('官杀',0)}个——{'心理压力可能影响判断' if ts.get('官杀',0) >= 2 else '情绪相对稳定'}"
            },
        ]
        
        insights = []
        if pitfalls:
            insights.append(f"最值得避开的是：{pitfalls[0]}")
        if ts.get("印星", 0) >= 2:
            insights.append("印星有力=学习能力强——芒格会说这是最好的优势")
        
        warnings = pitfalls
        
        advice = []
        advice.append("「如果知道自己会死在哪里，就永远不去那里」——先避开错误再做对的事")
        if ts.get("官杀", 0) >= 2:
            advice.append("压力是判断力的大敌——在高压力下暂停决策")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.75,
            "summary": f"芒格式分析：先看坑——发现{len(pitfalls)}个潜在陷阱。{'命局明智' if len(pitfalls) <= 1 else '需谨慎行'}。{'学习特质突出' if ts.get('印星',0) >= 2 else '建议建立系统学习框架'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["命局无明显典型陷阱，决策质量更多取决于后天习惯"],
            "warnings": warnings,
            "advice": advice,
        }


# ==========================================
# 视角六：Taleb · 反脆弱
# ==========================================

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


# ==========================================
# 视角七：Naval · 长期主义与杠杆
# ==========================================

class Naval(Perspective):
    name = "Naval"
    title = "长期主义与杠杆"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        features = a["features"]
        
        score = 50
        
        # 特定知识（印星=学习能力）
        if ts.get("印星", 0) >= 2:
            score += 20
        elif ts.get("印星", 0) == 1:
            score += 10
        
        # 杠杆能力（财星=资源配置）
        if ts.get("财星", 0) >= 1:
            score += 10
        
        # 长期主义（大运判断）
        dm_wx = dm.get("wuxing", "")
        dayun_phase = a["dayun_phase"]
        if dayun_phase:
            d_g = dayun_phase.get("gan_wuxing", "")
            if d_g == dm_wx:
                score += 10  # 大运帮身=长期在正轨
            elif d_g and wx.get(d_g, 0) > 20:
                score += 5
        
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "特定知识",
                "score": min(100, 40 + 20 * ts.get("印星", 0)),
                "detail": f"印星{ts.get('印星',0)}个——{'学什么都能深' if ts.get('印星',0) >= 2 else '需要找到真正热爱的领域深耕'}"
            },
            {
                "name": "杠杆能力",
                "score": min(100, 50 + 15 * ts.get("财星", 0)),
                "detail": f"财星{ts.get('财星',0)}个——{'有资源运作的直觉' if ts.get('财星',0) >= 1 else '杠杆思维需要刻意训练'}"
            },
            {
                "name": "复利耐心",
                "score": min(100, 40 + int(a['daymaster']['support_ratio'])),
                "detail": a["daymaster"]["detail"]
            },
        ]
        
        insights = []
        if ts.get("印星", 0) >= 2:
            insights.append(f"印星{ts.get('印星',0)}个=获取特定知识的天赋——Naval说这是最好的护城河")
        if ts.get("财星", 0) >= 1:
            insights.append("财星透干=对杠杆有直觉——代码/媒体/资本三条路都可以考虑")
        
        warnings = []
        if ts.get("比劫", 0) >= 2 and ts.get("财星", 0) == 0:
            warnings.append("比劫旺而无财——需要警惕杠杆带来的债务风险")
        
        advice = []
        advice.append(f"核心建议：找到你的「特定知识」——{'你已经有了学习的天赋，缺的是选对方向' if ts.get('印星',0) >= 2 else '先深耕一个领域再谈杠杆'}")
        if ts.get("财星", 0) == 0:
            advice.append("财富不是目的，创造价值才是——先聚焦在自己能提供什么稀缺价值")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.65,
            "summary": f"长期主义评分{score}分。{'印星有力=学习类特定知识' if ts.get('印星',0) >= 2 else '需先建立深度专长'}。{'有杠杆直觉' if ts.get('财星',0) >= 1 else '杠杆是选修课'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["Naval式分析更适用于具体问题，先有专业再有杠杆"],
            "warnings": warnings or [],
            "advice": advice,
        }


# ==========================================
# 视角八：老子 · 道法自然
# ==========================================

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
                natural = f"调候用神{f['yongshen_str']}，此乃大道在身。{ys_wx}气充盈，不刻意而为，自然顺势。老子曰'上善若水'——{ys_wx == '水' and '此命天然近道' or f'虽非水，但{ys_wx}气已足，顺其自然即可'}。"
            else:
                natural = f"调候用神{f['yongshen_str']}虽有，但力量{ys_wx and f['wx'].get(ys_wx, 0) > 10 and '不充' or '偏弱'}——老子会说：'为学日益，为道日损'，当下最重要的是减法而非加法。"
        else:
            natural = "用神不明——老子会摇头：'五色令人目盲'，现在你面前的路太多，反而是最大的问题。"
        
        water_approach = ""
        if f['wx'].get('水', 0) >= 20:
            water_approach = f"水性为{f['wx']['水']}%——此命有近道之资。水不争而利万物，不争就是最好的争。在人生的多数场景中，柔软比刚硬更有力量。"
        else:
            water_approach = f"水性仅{f['wx'].get('水', 0)}%——刚多柔少。老子提醒：'天下之至柔，驰骋天下之至坚'。学会柔软是此生的功课。"
        
        dayun_p = ""
        if f["dayun"].get("ganzhi"):
            d = f["dayun"]
            if d.get('gan_wuxing','') == '水' or d.get('zhi_wuxing','') == '水':
                dayun_p = f"当前{f['dayun_str']}——此运带水，正是修炼'不争之德'的好时期。"
            else:
                dayun_p = f"当前{f['dayun_str']}——此运{'' if d.get('gan_wuxing','') == f['dm_wx'] else '非助身'}，老子说'反者道之动'——低谷期反而是在积蓄力量。"
        
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


# ==========================================
# 视角九：王阳明 · 知行合一
# ==========================================

class WangYangming(Perspective):
    name = "王阳明"
    title = "知行合一"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        features = a["features"]
        
        # 知（印星=认知能力）
        knowledge = ts.get("印星", 0) * 15 + 30
        # 行（比劫=行动力 + 财星=实践）
        action = ts.get("比劫", 0) * 10 + ts.get("财星", 0) * 10 + 30
        
        gap = abs(knowledge - action)
        balance = max(0, 100 - gap * 2)
        
        score = int(balance)
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "知", "score": min(100, knowledge),
                "detail": f"认知层面评分{min(100, knowledge)}——{'印星有力=善于思考' if ts.get('印星',0) >= 2 else '思考深度需训练'}"
            },
            {
                "name": "行", "score": min(100, action),
                "detail": f"行动层面评分{min(100, action)}——{'执行力不俗' if action > 50 else '行动力需加强'}"
            },
            {
                "name": "知行落差", "score": score,
                "detail": f"知行差距{gap}分——{'知行合一' if gap < 20 else '想得多做得少' if knowledge > action else '行动快于思考'}"
            },
        ]
        
        insights = []
        if gap < 20:
            insights.append("知行基本合一——这是最难得的素质")
        elif knowledge > action:
            insights.append(f"知({knowledge})大于行({action})——王阳明会说'知道却做不到=不知道'")
        else:
            insights.append(f"行({action})大于知({knowledge})——实干型，但需要在实践中提炼理论")
        
        warnings = []
        if ts.get("印星", 0) >= 3 and ts.get("比劫", 0) == 0:
            warnings.append("纯思型——容易陷入空想，事上练是唯一的出路")
        
        advice = []
        advice.append("事上练——所有道理都要在具体事上验证")
        if gap > 30:
            advice.append(f"知行差距过大，建议选一件小事做到极致，先缩小差距再谈大方向")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.7,
            "summary": f"知行合一评分{score}分。{'知行基本平衡' if gap < 20 else '知大于行' if knowledge > action else '行大于知'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["命局知行差距不明显，后天习惯决定知行合一程度"],
            "warnings": warnings or [],
            "advice": advice,
        }


# ==========================================
# 视角十：斯多葛 · 控制二分法
# ==========================================

class Stoic(Perspective):
    name = "斯多葛"
    title = "控制二分法"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        combos = a["combinations"]
        
        score = 50
        
        # 可控部分：印星（认知）+ 比劫（行动）
        controllable = ts.get("印星", 0) * 10 + ts.get("比劫", 0) * 10
        # 不可控部分：官杀（外界压力）+ 财星（物质波动）
        uncontrollable = ts.get("官杀", 0) * 10 + ts.get("财星", 0) * 10
        
        if controllable >= uncontrollable:
            score += 15
        else:
            score -= 5
        
        # 消极想象（印星越强越能做）
        if ts.get("印星", 0) >= 2:
            score += 10
        
        # 逆境即磨炼
        if "七杀" in str(a["raw_bazi"].get("shishen", {})):
            score += 10
        
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "控制边界清晰度",
                "score": min(100, 50 + int(controllable - uncontrollable)),
                "detail": f"可控力{controllable}分 vs 外力{uncontrollable}分——{'清楚什么在自己掌控之内' if controllable > uncontrollable else '容易为不可控的事情焦虑'}"
            },
            {
                "name": "逆境承受力",
                "score": min(100, 50 + 15 * int("七杀" in str(a['raw_bazi'].get('shishen',{})))),
                "detail": f"{'七杀透干=逆境经验丰富' if '七杀' in str(a['raw_bazi'].get('shishen',{})) else '逆境经历相对较少'}"
            },
            {
                "name": "内心自由",
                "score": max(10, 70 - 10 * ts.get("官杀", 0)),
                "detail": f"官杀{ts.get('官杀',0)}个——{'外界压力可能侵蚀内心自由' if ts.get('官杀',0) >= 2 else '内心相对自主'}"
            },
        ]
        
        insights = []
        if controllable > uncontrollable:
            insights.append("你的命局中，可控因素多于不可控——斯多葛会说你天生适合理性生活")
        if "七杀" in str(a["raw_bazi"].get("shishen", {})):
            insights.append("七杀是斯多葛的黄金训练——逆境是磨炼灵魂的土壤")
        
        warnings = []
        if uncontrollable > controllable * 2:
            warnings.append("外部约束过多——需要在不可控中找回自己的判断主权")
        
        advice = []
        advice.append("控制二分法练习：列出你担心的所有事，划掉你控制不了的")
        if ts.get("官杀", 0) >= 2:
            advice.append("外界压力大时，记住：'人不是被事情本身困扰，而是被对事情的看法困扰'")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.65,
            "summary": f"控制二分法评分{score}分。{'可控>不可控' if controllable > uncontrollable else '需重新识别控制的边界'}。{'七杀=逆境磨炼' if '七杀' in str(a['raw_bazi'].get('shishen',{})) else '建议主动制造适度挑战'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["控制二分法练习对大多数人都有帮助，不依赖命局"],
            "warnings": warnings or [],
            "advice": advice,
        }


# ==========================================
# 视角十一：克劳利 · 意志法则
# ==========================================

class Crowley(Perspective):
    name = "克劳利"
    title = "泰勒玛意志法则"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        th = a["tiaohou"]
        
        score = 50
        
        # 意志力（七杀=执行力）
        ss = a["raw_bazi"].get("shishen", {})
        if "七杀" in ss.get("time", ""):
            score += 20
        if "七杀" in ss.get("month", ""):
            score += 10
        
        # 变通力（食伤=创造力）
        if ts.get("食伤", 0) >= 2:
            score += 10
        
        # 仪式感（印星）
        if ts.get("印星", 0) >= 2:
            score += 10
        
        # 水火平衡（克劳利偏重）
        water = wx.get("水", 0)
        fire = wx.get("火", 0)
        if abs(water - fire) < 15:
            score += 5
        
        score = max(10, min(95, score))
        
        dimensions = [
            {
                "name": "意志力",
                "score": min(100, 50 + (20 if "七杀" in ss.get("time","") else 0) + 10),
                "detail": f"{'七杀透干=强大意志力' if '七杀' in ss.get('time','') else '意志力一般，需要仪式感来增强'}"
            },
            {
                "name": "神圣守护",
                "score": min(100, 30 + 15 * ts.get("印星", 0)),
                "detail": f"印星{ts.get('印星',0)}个——{'有内在精神秩序' if ts.get('印星',0) >= 2 else '需要在外部建立仪式'}"
            },
            {
                "name": "元素平衡",
                "score": min(100, 60 - int(abs(wx.get('水',0) - wx.get('火',0)))),
                "detail": f"水火差{abs(wx.get('水',0)-wx.get('火',0)):.1f}%——{'元素平衡=灵活与稳定的统一' if abs(wx.get('水',0)-wx.get('火',0)) < 15 else '一元素过强需注意平衡'}"
            },
        ]
        
        insights = []
        if "七杀" in ss.get("time", ""):
            insights.append("七杀透干=强大的意志力基础——克劳利会说是'真正的意志'的天然土壤")
        if th.get("yongshen"):
            insights.append(f"用神{th['yongshen']}=你的魔法对应物——在做重要决定前呼唤其能量")
        
        warnings = []
        if "七杀" in ss.get("time", "") and wx.get("水", 0) < 15:
            warnings.append("七杀强而水弱——意志力可能变成强迫性，需要柔性调和")
        
        advice = []
        advice.append(f"建立个人仪式——每天固定时间做同一件事，这是强化意志力的基础训练")
        if wx.get("火", 0) > wx.get("水", 0):
            advice.append("火元素偏旺——需要用水元素柔化意志的刚性")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.55,
            "summary": f"意志法则评分{score}分。{'七杀透干=强大意志' if '七杀' in ss.get('time','') else '意志力适中'}。{'水火' + ('平衡' if abs(wx.get('水',0)-wx.get('火',0)) < 15 else '失衡')}。",
            "dimensions": dimensions,
            "key_insights": insights or ["克劳利视角更适合有明确意志挑战的具体问题"],
            "warnings": warnings or [],
            "advice": advice,
        }


# ==========================================
# 视角十二：萨满 · 灵魂旅行
# ==========================================

class Shaman(Perspective):
    name = "萨满"
    title = "灵魂旅行与能量"
    
    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        combos = a["combinations"]
        
        score = 50
        
        # 水元素=灵性通道
        if wx.get("水", 0) >= 25:
            score += 15
        # 木元素=成长与连接
        if wx.get("木", 0) >= 20:
            score += 10
        # 印星=与更智慧的连接
        if ts.get("印星", 0) >= 2:
            score += 10
        
        # 冲=能量通道不通
        if any("冲" in c for c in combos):
            score -= 5
        # 合=能量整合
        if any("合" in c for c in combos):
            score += 10
        
        score = max(10, min(95, score))
        
        # 力量动物
        animal_map = {
            "木": "鹿（柔韧适应）",
            "火": "狐狸（敏锐机警）",
            "土": "熊（稳重守护）",
            "金": "鹰（高瞻远瞩）",
            "水": "蛇（深沉蜕皮）",
        }
        power_animal = animal_map.get(dm.get("wuxing", ""), "鹿")
        shadow_animal = animal_map.get(min(wx, key=wx.get) if wx else "土", "熊")
        
        dimensions = [
            {
                "name": "灵性通道", "score": min(100, 30 + int(wx.get('水',0))),
                "detail": f"水元素占{wx.get('水',0)}%——{'灵性感知力强' if wx.get('水',0) >= 25 else '灵性通道需要更安静的状态打开'}"
            },
            {
                "name": "能量整合",
                "score": min(100, 50 + (10 if any('合' in c for c in combos) else 0) - (5 if any('冲' in c for c in combos) else 0)),
                "detail": f"命局{'有合有冲=能量在整合与冲突之间' if any('合' in c for c in combos) and any('冲' in c for c in combos) else '有合=能量和谐' if any('合' in c for c in combos) else '有冲=能量有裂痕' if any('冲' in c for c in combos) else '能量相对平稳'}"
            },
            {
                "name": "动物能量",
                "score": min(100, 50 + int(wx.get(max(wx, key=wx.get),0) - wx.get(min(wx, key=wx.get),0)) if wx else 0),
                "detail": f"力量动物：{power_animal}；影子动物：{shadow_animal}"
            },
        ]
        
        insights = []
        if wx.get("水", 0) >= 25:
            insights.append(f"水元素{wx['水']}%——灵性天赋，适合冥想、梦境工作")
        if ts.get("印星", 0) >= 2:
            insights.append("印星=与先祖/更高智慧有天然连接")
        
        warnings = []
        if any("冲" in c for c in combos):
            warnings.append("命局有冲——能量有裂口需要修复仪式")
        
        advice = []
        advice.append(f"与你的力量动物「{power_animal}」连接——在冥想中想象它，学习它的品质")
        if wx.get("水", 0) < 20:
            advice.append("水元素偏弱——多亲近水域（泡澡、游泳、听雨）来加强灵性通道")
        
        return {
            "score": score,
            "monologue": self._build_monologue(a),
            "confidence": 0.5,
            "summary": f"萨满视角评分{score}分。力量动物：{power_animal}。{'灵性天赋突出' if wx.get('水',0) >= 25 else '灵性需后天开发'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["萨满视角是补充视角，不强依赖命局先天数据"],
            "warnings": warnings or [],
            "advice": advice,
        }


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


# ==========================================
# 视角十四：鬼谷子 · 捭阖之道
# ==========================================

class GuiGuZi(Perspective):
    name = "鬼谷子"
    title = "捭阖之道攻心为上"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]

        score = 50
        dm_wx = dm.get("wuxing", "")

        # 捭（开放）：食伤=表达能力
        if ts.get("食伤", 0) >= 2:
            score += 15
        elif ts.get("食伤", 0) >= 1:
            score += 8
        # 阖（闭合）：印星=沉默观察
        if ts.get("印星", 0) >= 2:
            score += 15
        elif ts.get("印星", 0) >= 1:
            score += 8
        # 飞箝（说服力）：财星=资源洞察
        if ts.get("财星", 0) >= 1:
            score += 10
        # 反应术（洞察力）：水元素=感知
        if wx.get("水", 0) >= 20:
            score += 10
        # 抵巇（抓裂缝）：有冲=有可以利用的矛盾
        if any("冲" in c for c in a["combinations"]):
            score += 5

        score = max(10, min(95, score))

        # 性格倾向判断
        if ts.get("食伤", 0) >= ts.get("印星", 0):
            style = "捭（开放型）——善于表达，需要学会闭嘴"
        else:
            style = "阖（内敛型）——善于观察，需要学会开口"

        dimensions = [
            {"name": "捭阖平衡",
             "score": min(100, 50 + 10 * abs(ts.get("食伤",0) - ts.get("印星",0))),
             "detail": style},
            {"name": "洞察人心",
             "score": min(100, 30 + 15 * ts.get("财星",0) + int(wx.get('水',0))),
             "detail": f"{'水元素'+str(wx.get('水',0))+'%'+'=感知力' if wx.get('水',0)>=20 else '感知力一般'}，{'财星透出=对资源流动敏感' if ts.get('财星',0)>=1 else '资源洞察需要训练'}"},
            {"name": "说服力",
             "score": min(100, 40 + 15 * ts.get("食伤",0) + 10 * ts.get("财星",0)),
             "detail": f"食伤{ts.get('食伤',0)}个+财星{ts.get('财星',0)}个——{'有说服他人的天然武器' if ts.get('食伤',0)+ts.get('财星',0)>=2 else '说服力来自信息优势'}"},
            {"name": "随机应变",
             "score": min(100, 50 + 10 * ts.get("食伤",0) - 5 * ts.get("印星",0)),
             "detail": f"{'灵活性高' if ts.get('食伤',0)>ts.get('印星',0) else '稳定性强' if ts.get('印星',0)>ts.get('食伤',0) else '灵活与稳定均衡'}"},
        ]

        insights = []
        if ts.get("食伤", 0) >= 1 and ts.get("印星", 0) >= 1:
            insights.append("食伤印星兼备——天生的纵横家，既能说也能藏")
        if wx.get("水", 0) >= 20:
            insights.append(f"水性足({wx['水']}%)——鬼谷子会说你天生会'反应术'，善于从对方话中读信息")

        warnings = []
        if ts.get("印星", 0) >= 3 and ts.get("食伤", 0) == 0:
            warnings.append("过阖不捭——容易把自己藏太深，别人看不透你也就无法信任你")

        advice = []
        advice.append(f"你的风格是{style}")
        if wx.get("水", 0) < 15:
            advice.append("水性偏弱——可以刻意练习倾听，水主智也主柔")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.65,
            "summary": f"捭阖评分{score}分。{style}。{'洞察力敏锐' if wx.get('水',0)>=20 else '说服力可后天培养'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["捭阖之道需结合具体场景应用"],
            "warnings": warnings or [], "advice": advice,
        }


# ==========================================
# 视角十五：刘伯温 · 微兆预警
# ==========================================

class LiuBowen(Perspective):
    name = "刘伯温"
    title = "天人合一微兆预警"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        combos = a["combinations"]
        ts = a["tenshen"]
        dayun = a["dayun_phase"]

        score = 50

        # 微兆识别：天干地支的微妙组合
        subtle_signals = []

        # 天克地冲=大信号
        for c in combos:
            if "冲" in c:
                subtle_signals.append(c)

        # 害=隐藏矛盾
        for c in combos:
            if "害" in c:
                subtle_signals.append(f"六害{c}——隐藏的矛盾")

        # 空亡=机会与陷阱
        xk = a["raw_bazi"].get("xunkong", {})
        xk_info = f"年柱空亡{xk.get('year','?')}，日柱空亡{xk.get('day','?')}" if xk else ""

        # 大运转换=关键节点
        if dayun:
            yi = dayun.get("year_index", 1)
            if yi <= 2:
                subtle_signals.append(f"刚入{dayun['ganzhi']}运（第{yi}年）——运势转换期，微兆最为关键")
            elif yi >= 8:
                subtle_signals.append(f"{dayun['ganzhi']}运末（第{yi}年）——准备迎接下一个大运的变化")

        # 信号越多分越高
        signal_count = len(subtle_signals)
        if signal_count >= 3:
            score += 20
        elif signal_count >= 1:
            score += 10

        # 印星=留心观察
        if ts.get("印星", 0) >= 2:
            score += 10
        # 水=洞察力
        if wx.get("水", 0) >= 20:
            score += 10
        # 冲=变量
        if any("冲" in c for c in combos):
            score += 5

        score = max(10, min(95, score))

        dimensions = [
            {"name": "微兆识别力",
             "score": min(100, 40 + 15 * signal_count),
             "detail": f"识别{signal_count}个潜在信号——{'机会藏在细节中' if signal_count >= 2 else '目前无明显异常信号'}"},
            {"name": "天人感应",
             "score": min(100, 40 + int(wx.get('水',0)) + 10 * ts.get("印星", 0)),
             "detail": f"{'水元素'+str(wx.get('水',0))+'%'+'=感应通道开放' if wx.get('水',0)>=20 else '感应通道一般'}，{'印星=有内观能力' if ts.get('印星',0)>=1 else '内观能力需培养'}"},
            {"name": "周期意识",
             "score": min(100, 30 + (20 if dayun else 0) + 10 * int(dayun and dayun.get('year_index',1)<=2)),
             "detail": f"当前{'在' + dayun['ganzhi'] + '运关键期' if dayun and dayun.get('year_index',1)<=2 else dayun['ganzhi']+'运' if dayun else '大运未详'}——{'刘伯温强调察微知著' if signal_count >= 2 else '运势平稳期'}"},
        ]

        insights = []
        if subtle_signals:
            insights.append(f"最值得关注的信号：{subtle_signals[0]}")
        if xk_info:
            insights.append(f"{xk_info}——空亡之处藏玄机，可能是意外之喜也可能是陷阱")

        warnings = []
        if any("害" in c for c in combos):
            warnings.append("六害入局——小人暗算或内部矛盾，是最大的隐性风险")

        advice = []
        advice.append("训练观察微兆的习惯——每天记录三个被忽略的小事，慢慢就会看出规律")
        if any("冲" in c for c in combos):
            advice.append("冲局如大潮——提前半年准备而非临时应对")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.6,
            "summary": f"微兆预警评分{score}分。识别{signal_count}个信号。{'水木有灵' if wx.get('水',0)>=20 and wx.get('木',0)>=20 else '感应通道一般'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["目前命局没有突出的大信号，小信号需要细心捕捉"],
            "warnings": warnings or [], "advice": advice,
        }


# ==========================================
# 视角十六：弗洛伊德 · 潜意识
# ==========================================

class Freud(Perspective):
    name = "弗洛伊德"
    title = "潜意识与本能冲动"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        hg = a["raw_bazi"].get("hidden_gans", {})
        ss = a["raw_bazi"].get("shishen", {})

        score = 50

        # 本我（id）：藏干=隐藏的欲望
        hidden_count = sum(len(v) if isinstance(v, list) else 1 for v in hg.values())
        if hidden_count >= 4:
            score += 15  # 藏干多=潜意识丰富
        elif hidden_count >= 2:
            score += 8

        # 自我（ego）：日主=显意识
        dm_wx = dm.get("wuxing", "")
        if dm.get("strength") in ("身强", "中和"):
            score += 10

        # 超我（superego）：官杀=道德约束
        if ts.get("官杀", 0) >= 2:
            score += 10  # 道德感重
        if ts.get("印星", 0) >= 2:
            score += 5  # 教化

        # 压抑：冲=内心冲突
        if any("冲" in c for c in a["combinations"]):
            score += 10
        if any("害" in c for c in a["combinations"]):
            score += 5

        # 力比多：水旺=性/创造力
        if wx.get("水", 0) >= 20:
            score += 10

        score = max(10, min(95, score))

        # 防御机制识别
        defenses = []
        if ts.get("印星", 0) >= 2:
            defenses.append("理智化——用思考隔离情感")
        if ts.get("比劫", 0) >= 2:
            defenses.append("投射——把自己不喜欢的特质归因于他人")
        if "七杀" in ss.get("time", ""):
            defenses.append("反向形成——表面的温和掩盖内在的攻击性")
        if wx.get("水", 0) >= 25 and ts.get("食伤", 0) >= 2:
            defenses.append("升华——创造性的出口")

        dimensions = [
            {"name": "潜意识丰富度",
             "score": min(100, 30 + 15 * hidden_count),
             "detail": f"藏干{hidden_count}个——{'内心世界丰富' if hidden_count >= 4 else '潜意识内容一般'}"},
            {"name": "自我力量",
             "score": min(100, 50 + 15 * int(dm.get('strength') in ('身强','中和'))),
             "detail": f"日主{dm.get('strength','?')}——{'自我功能强健' if dm.get('strength') in ('身强','中和') else '自我边界较弱'}"},
            {"name": "压抑程度",
             "score": max(0, 50 - 10 * sum(1 for c in a['combinations'] if '冲' in c)),
             "detail": f"{'有冲=内心冲突需要表达' if any('冲' in c for c in a['combinations']) else '内心相对平静'}"},
            {"name": "升华潜力",
             "score": min(100, 40 + 15 * ts.get("食伤",0) + 10 * (wx.get('水',0) >= 20)),
             "detail": f"{'食伤+水=强大的创造性能量' if ts.get('食伤',0)>=1 and wx.get('水',0)>=20 else '创造力潜力需要释放'}"},
        ]

        insights = []
        if hidden_count >= 4:
            insights.append(f"藏干丰富（{hidden_count}个）——你的潜意识像冰山，海面下远比表面大")
        if defenses:
            insights.append(f"可能的防御机制：{defenses[0]}")
        if "七杀" in ss.get("time", "") and wx.get("水", 0) >= 20:
            insights.append("七杀透干+水旺——力比多能量强大，需要在创造性的活动中释放")

        warnings = []
        if ts.get("官杀", 0) >= 3 and ts.get("食伤", 0) == 0:
            warnings.append("超我过强——道德约束压倒了本能，可能有强迫性人格倾向")

        advice = []
        advice.append("记录梦境——弗洛伊德认为梦是'通往潜意识的皇家大道'")
        if wx.get("水", 0) >= 20 and ts.get("食伤", 0) >= 1:
            advice.append("你的力比多能量适合创造性工作——写作、艺术、研究都可以成为升华的出口")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.6,
            "summary": f"潜意识评分{score}分。{'内心世界丰富' if hidden_count >= 4 else '潜意识相对平静'}。{'有创造性升华通道' if ts.get('食伤',0)>=1 and wx.get('水',0)>=20 else '压抑需要出口'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["弗洛伊德视角更适用于有具体心理困扰的场景"],
            "warnings": warnings or [], "advice": advice,
        }


# ==========================================
# 视角十七：尼采 · 权力意志
# ==========================================

class Nietzsche(Perspective):
    name = "尼采"
    title = "权力意志重估一切"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        combos = a["combinations"]
        ss = a["raw_bazi"].get("shishen", {})

        score = 50

        # 权力意志：七杀=斗志
        if "七杀" in ss.get("time", ""):
            score += 20
        elif "七杀" in ss.get("month", ""):
            score += 15
        if ts.get("官杀", 0) >= 2:
            score += 5

        # 创造与毁灭：食伤=创造，官杀=破坏
        if ts.get("食伤", 0) >= 2:
            score += 10
        if ts.get("官杀", 0) >= 2:
            score += 5

        # 重估一切：冲=打破旧秩序
        if any("冲" in c for c in combos):
            score += 10
        if any("害" in c for c in combos):
            score += 5

        # 超人倾向：比劫=独立，印星=自我超越
        if ts.get("比劫", 0) >= 1:
            score += 5
        if ts.get("印星", 0) >= 2:
            score += 5

        # 酒神精神：食伤+水=迷狂创造力
        if ts.get("食伤", 0) >= 1 and wx.get("水", 0) >= 20:
            score += 10

        score = max(10, min(95, score))

        # 超人评语
        if score >= 75:
            ubermensch = "超人潜力——不以常人的标准衡量自己"
        elif score >= 50:
            ubermensch = "凡人之上——有超越的欲望但还不够彻底"
        else:
            ubermensch = "骆驼阶段——还需要先背负传统才能成为狮子"

        dimensions = [
            {"name": "权力意志",
             "score": min(100, 40 + 20 * int("七杀" in ss.get("time","") or "七杀" in ss.get("month",""))),
             "detail": f"{'七杀透干=强大的权力意志' if '七杀' in ss.get('time','') or '七杀' in ss.get('month','') else '权力意志需激发'}"},
            {"name": "日神与酒神",
             "score": min(100, 40 + 15 * ts.get("食伤",0) + 10 * (wx.get('水',0) >= 20)),
             "detail": f"{'酒神精神占优——直觉和创造力是主要力量' if ts.get('食伤',0)>=1 and wx.get('水',0)>=20 else '日神精神为主——理性和秩序是安全感来源'}"},
            {"name": "超越等级",
             "score": score,
             "detail": ubermensch},
        ]

        insights = []
        if "七杀" in ss.get("time", ""):
            insights.append("七杀透干——尼采会说'成为你自己'不是温和的邀请，而是激烈的战斗")
        if ts.get("食伤", 0) >= 2 and any("冲" in c for c in combos):
            insights.append("食伤旺+有冲——你有砸碎旧价值的冲动，问题是用什么来取代")
        if ts.get("印星", 0) >= 2 and ts.get("官杀", 0) >= 2:
            insights.append("印与杀对峙——这是'骆驼'与'狮子'的角力，先服从再反抗的经典路径")

        warnings = []
        if ts.get("印星", 0) >= 3 and ts.get("食伤", 0) == 0:
            warnings.append("过度理智化——尼采会提醒'太多的学问会扼杀行动的力量'")
        if "七杀" in ss.get("time", "") and ts.get("印星", 0) == 0:
            warnings.append("有毁灭倾向而无创造力——注意不要为了反抗而反抗")

        advice = []
        advice.append(f"你的超人阶段：{ubermensch}")
        if ts.get("食伤", 0) >= 2:
            advice.append("用创造代替抱怨——创造自己的价值体系比摧毁现有的更有力量")
        if wx.get("水", 0) >= 25:
            advice.append("水性深——适合在思想的深渊中探索，'当你凝视深渊，深渊也凝视着你'")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.65,
            "summary": f"权力意志评分{score}分。{ubermensch}。{'酒神VS日神' + ('——酒神更强' if ts.get('食伤',0)>=1 and wx.get('水',0)>=20 else '——日神为主')}。",
            "dimensions": dimensions,
            "key_insights": insights or ["尼采视角更适合有存在性困惑或面临价值抉择的场景"],
            "warnings": warnings or [], "advice": advice,
        }


# ==========================================
# 视角十八：巴菲特 · 价值投资
# ==========================================

class Buffett(Perspective):
    name = "巴菲特"
    title = "价值投资安全边际"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        dayun = a["dayun_phase"]

        score = 50

        # 内在价值（日主强度）
        support = a["daymaster"]["support_ratio"]
        if support >= 50:
            score += 20  # 基本面扎实
        elif support >= 35:
            score += 10

        # 安全边际（印星+比劫=保护层）
        protection = ts.get("印星", 0) * 10 + ts.get("比劫", 0) * 10
        if protection >= 30:
            score += 15
        elif protection >= 15:
            score += 8

        # 护城河（财星=持久竞争优势）
        if ts.get("财星", 0) >= 1:
            score += 10
        if ts.get("印星", 0) >= 2:
            score += 5  # 印星=可复用的知识

        # 管理层（官杀=决断力）
        if ts.get("官杀", 0) >= 1:
            score += 5

        # 周期判断（大运）
        if dayun:
            d_wx = dayun.get("gan_wuxing", "")
            dm_wx = dm.get("wuxing", "")
            if d_wx == dm_wx:
                score += 10  # 顺周期
            elif _WUXING_CONQUER.get(d_wx) == dm_wx:
                score -= 5  # 逆周期

        score = max(10, min(95, score))

        # 价值判断
        if score >= 70:
            valuation = "低估——市场错了，现在是最好的买入时机"
        elif score >= 50:
            valuation = "合理估值——持有等待价值释放"
        else:
            valuation = "高估——需要更多安全边际"

        dimensions = [
            {"name": "内在价值",
             "score": min(100, int(support)),
             "detail": f"生扶力度{support}%——{'基本面扎实' if support >= 50 else '需要积累更多资本'}"},
            {"name": "安全边际",
             "score": min(100, 30 + protection),
             "detail": f"{'保护充足' if protection >= 30 else '安全边际不足'}"},
            {"name": "护城河",
             "score": min(100, 30 + 20 * ts.get("财星",0) + 10 * ts.get("印星",0)),
             "detail": f"{'财星+印星=有复利根基' if ts.get('财星',0)>=1 and ts.get('印星',0)>=1 else '护城河需要后天建立'}"},
            {"name": "周期位置",
             "score": min(100, 50 + (10 if dayun and (dayun.get('gan_wuxing','')==dm.get('wuxing','')) else 0) - (5 if dayun and (_WUXING_CONQUER.get(dayun.get('gan_wuxing',''))==dm.get('wuxing','')) else 0)),
             "detail": f"当前{'顺周期' if dayun and (dayun.get('gan_wuxing','')==dm.get('wuxing','')) else '逆周期' if dayun and (_WUXING_CONQUER.get(dayun.get('gan_wuxing',''))==dm.get('wuxing','')) else '中性周期'}" if dayun else "周期判断需大运数据"
            },
        ]

        insights = []
        if support >= 50:
            insights.append(f"基本面评分{support}%——巴菲特会说'价格是你支付的，价值是你得到的'")
        if ts.get("印星", 0) >= 2:
            insights.append(f"印星{ts.get('印星',0)}个=复利机器——知识是最佳投资标的")
        if dayun and (dayun.get('gan_wuxing','') == dm.get('wuxing','')):
            insights.append(f"当前{dayun['ganzhi']}运顺周期——是建立护城河的好时机")

        warnings = []
        if protection < 15:
            warnings.append("安全边际不足——不要加杠杆，保持现金储备")

        advice = []
        advice.append(f"价值判断：{valuation}")
        advice.append("最重要的投资是投资自己——印星=自我教育是最好的长期资产")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.65,
            "summary": f"价值投资评分{score}分。{valuation}。{'护城河' + ('已形成' if ts.get('财星',0)>=1 and ts.get('印星',0)>=1 else '待建立')}。",
            "dimensions": dimensions,
            "key_insights": insights or ["巴菲特视角更适合财富管理方面的具体问题"],
            "warnings": warnings or [], "advice": advice,
        }


# ==========================================
# 视角十九：赫尔墨斯 · 对应法则
# ==========================================

class Hermes(Perspective):
    name = "赫尔墨斯"
    title = "七原则如其在上"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        combos = a["combinations"]
        th = a["tiaohou"]

        score = 50

        # 1. 心物对应（mentalism）：印星=思维覆盖现实
        if ts.get("印星", 0) >= 2:
            score += 10
        # 2. 对应原则（correspondence）：五行平衡=宏观微观一致
        wx_vals = sorted(wx.values(), reverse=True)
        if len(wx_vals) >= 2 and wx_vals[0] - wx_vals[-1] < 20:
            score += 15
        # 3. 振动原则（vibration）：食伤=能量向外辐射
        if ts.get("食伤", 0) >= 2:
            score += 10
        # 4. 极性原则（polarity）：冲=对立统一
        if any("冲" in c for c in combos):
            score += 10
        # 5. 节奏原则（rhythm）：大运=生命节奏
        if a["dayun_phase"]:
            score += 10
        # 6. 因果原则（causality）：用神=关键因素
        if th.get("yongshen"):
            score += 5
        # 7. 性别原则（gender）：阴阳平衡
        if wx.get("水", 0) >= 20 and wx.get("火", 0) >= 20:
            score += 10

        score = max(10, min(95, score))

        # 七原则分析
        principles = [
            f"心物法则——{'印星有力=思维能量强' if ts.get('印星',0)>=2 else '心物连接一般'}",
            f"对应法则——{'五行均衡=天地人三才对应良好' if len(wx_vals)>=2 and wx_vals[0]-wx_vals[-1]<20 else '五行偏枯=需要更多调和'}",
            f"振动法则——{'食伤透干=能量向外辐射' if ts.get('食伤',0)>=1 else '能量内敛'}",
            f"极性法则——{'有冲=对立统一的原动力' if any('冲' in c for c in combos) else '极性相对平衡'}",
            f"节奏法则——{'大运流转=生命节奏清晰' if a['dayun_phase'] else '节奏待显化'}",
            f"因果法则——{'用神明确=因果链条清晰' if th.get('yongshen') else '因果需探索'}",
            f"性别法则——{'水火并存=阴阳俱足' if wx.get('水',0)>=20 and wx.get('火',0)>=20 else '阴阳有偏'}"
        ]

        dimensions = [
            {"name": "七原则共振",
             "score": score,
             "detail": f"七原则中{sum(1 for p in [ts.get('印星',0)>=2, len(wx_vals)>=2 and wx_vals[0]-wx_vals[-1]<20, ts.get('食伤',0)>=2, any('冲' in c for c in combos), bool(a['dayun_phase']), bool(th.get('yongshen')), wx.get('水',0)>=20 and wx.get('火',0)>=20])}条活跃"},
            {"name": "如其在上",
             "score": min(100, 40 + 15 * ts.get("印星",0) + 15),
             "detail": f"微观八字对应宏观人生——{'有良好的抽象对应能力' if ts.get('印星',0)>=2 else '对应关系需练习发现'}"},
            {"name": "阴阳调和",
             "score": min(100, 50 + int(abs(wx.get('水',0)-wx.get('火',0)) < 15) * 20),
             "detail": f"水火差{abs(wx.get('水',0)-wx.get('火',0)):.0f}%——{'阴阳平衡' if abs(wx.get('水',0)-wx.get('火',0)) < 15 else '阴' + ('盛' if wx.get('水',0) > wx.get('火',0) else '弱') + '阳' + ('盛' if wx.get('火',0) > wx.get('水',0) else '弱')}"},
        ]

        insights = []
        insights.append(f"七原则核心：{principles[1]}")
        if ts.get("印星", 0) >= 2 and any("冲" in c for c in combos):
            insights.append("心物法则+极性法则=你有通过改变思维来转化对立面的能力")

        warnings = []
        if abs(wx.get('水',0) - wx.get('火',0)) > 30:
            warnings.append("阴阳偏颇——对应法则提醒你需要平衡生命中的对立力量")

        advice = []
        advice.append("如其在上，如其在下——你遇到的问题往往反映了更大的格局问题")
        advice.append("观察最近生活中的'巧合'——赫尔墨斯认为同步性是有意义的")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.55,
            "summary": f"七原则评分{score}分。{'天地人三才对应良好' if len(wx_vals)>=2 and wx_vals[0]-wx_vals[-1]<20 else '对应关系有待调和'}。{'阴阳' + ('平衡' if abs(wx.get('水',0)-wx.get('火',0)) < 15 else '有偏')}。",
            "dimensions": dimensions,
            "key_insights": insights or ["赫尔墨斯视角更偏向哲学诠释，是对其他视角的补充"],
            "warnings": warnings or [], "advice": advice,
        }


# ==========================================
# 视角二十：张一鸣 · 认知迭代
# ==========================================

class ZhangYiming(Perspective):
    name = "张一鸣"
    title = "认知迭代信息效率"

    def analyze(self, data: dict, a: dict) -> dict:
        f = _fmt_bazi_data(a)
        wx = a["wuxing"]
        dm = a["daymaster"]
        ts = a["tenshen"]
        dayun = a["dayun_phase"]
        combos = a["combinations"]

        score = 50

        # 信息处理能力（印星=吸收，食伤=输出）
        absorb = ts.get("印星", 0) * 15
        output = ts.get("食伤", 0) * 15
        info_score = absorb + output
        if info_score >= 40:
            score += 20
        elif info_score >= 20:
            score += 10

        # 延迟满足（财星+印星=长期思维）
        if ts.get("财星", 0) >= 1 and ts.get("印星", 0) >= 1:
            score += 15
        elif ts.get("印星", 0) >= 2:
            score += 10

        # 认知迭代速度（有冲=认知冲突=迭代契机）
        if any("冲" in c for c in combos):
            score += 10

        # 信息效率（木火=生长与表达）
        if wx.get("木", 0) >= 20 and wx.get("火", 0) >= 20:
            score += 10

        # 大运节奏
        if dayun and dayun.get("year_index", 1) <= 3:
            score += 5  # 新运=加速器

        score = max(10, min(95, score))

        dimensions = [
            {"name": "信息吸收力",
             "score": min(100, 30 + absorb),
             "detail": f"印星{ts.get('印星',0)}个={'信息输入能力强' if ts.get('印星',0)>=1 else '需建立稳定输入渠道'}"},
            {"name": "信息输出力",
             "score": min(100, 30 + output),
             "detail": f"食伤{ts.get('食伤',0)}个={'善于表达和输出' if ts.get('食伤',0)>=1 else '输出能力可培养'}"},
            {"name": "延迟满足",
             "score": min(100, 30 + 20 * int(ts.get('财星',0)>=1 and ts.get('印星',0)>=1) + 10 * int(ts.get('印星',0)>=2)),
             "detail": f"{'财印俱全=有长期主义的特质' if ts.get('财星',0)>=1 and ts.get('印星',0)>=1 else '延迟满足是需要刻意练习的'}"},
            {"name": "认知跃迁概率",
             "score": min(100, 40 + 15 * int(any('冲' in c for c in combos)) + 10 * int(wx.get('木',0)>=20 and wx.get('火',0)>=20)),
             "detail": f"{'有冲=认知冲突=跃迁契机' if any('冲' in c for c in combos) else '认知迭代偏渐进式'}"},
        ]

        insights = []
        if ts.get("印星", 0) >= 1 and ts.get("食伤", 0) >= 1:
            insights.append(f"印食兼具——输入输出平衡，有信息飞轮的潜质")
        if ts.get("财星", 0) >= 1 and ts.get("印星", 0) >= 1:
            insights.append("财印皆有——张一鸣式'不做表面功夫'的底层算法")
        if dayun and dayun.get("year_index", 1) <= 3:
            insights.append(f"刚进入{dayun['ganzhi']}运——认知迭代速度应该乘2")

        warnings = []
        if ts.get("印星", 0) >= 3 and ts.get("食伤", 0) == 0:
            warnings.append("信息过载风险——输入太多不输出会形成认知便秘")

        advice = []
        advice.append("建立信息筛选机制——输入质量决定输出质量")
        if wx.get("火", 0) < 15:
            advice.append("火弱——表达需要刻意练习，写作或演讲是认知迭代的加速器")
        if ts.get("财星", 0) >= 1 and ts.get("印星", 0) >= 1:
            advice.append("你的商业模式底色：做那些可以被复利的事——知识产品、数字资产")

        return {
            "score": score, "monologue": self._build_monologue(a), "confidence": 0.6,
            "summary": f"认知迭代评分{score}分。{'信息飞轮已启动' if ts.get('印星',0)>=1 and ts.get('食伤',0)>=1 else '需建立信息循环'}。{'长期主义底色' if ts.get('财星',0)>=1 and ts.get('印星',0)>=1 else '短期导向'}。",
            "dimensions": dimensions,
            "key_insights": insights or ["张一鸣视角更适合职业发展和认知成长方面的具体问题"],
            "warnings": warnings or [], "advice": advice,
        }


# ==========================================
# 模板视角系统
# ==========================================

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

# 生成模板视角
def _load_template_perspectives():
    result = {}
    for pid, cfg in TEMPLATE_PERSPECTIVES.items():
        result[pid] = TemplatePerspective(pid, cfg)
    return result

TEMPLATE_FRAMEWORKS = _load_template_perspectives()

# ==========================================
# 引擎
# ==========================================

class DeepPerspectiveEngine:
    """深度视角引擎——加载所有已实现的视角"""

    def __init__(self):
        self._frameworks = {
            "zhuge-liang": ZhugeLiang(),
            "yuan-tiangang": YuanTiangang(),
            "feynman": Feynman(),
            "jung": Jung(),
            "munger": Munger(),
            "taleb": Taleb(),
            "naval": Naval(),
            "laozi": Laozi(),
            "wang-yangming": WangYangming(),
            "stoic": Stoic(),
            "crowley": Crowley(),
            "shaman": Shaman(),
            # 新增（v1.2.5）：8个深度视角
            "sun-tzu": SunTzu(),
            "gui-gu-zi": GuiGuZi(),
            "liu-bowen": LiuBowen(),
            "freud": Freud(),
            "nietzsche": Nietzsche(),
            "buffett": Buffett(),
            "hermes": Hermes(),
            "zhang-yiming": ZhangYiming(),
        }
        # 合并模板视角（78个）
        self._frameworks.update(TEMPLATE_FRAMEWORKS)

    def list(self) -> list:
        return [{"id": k, "name": v.name, "title": v.title} for k, v in self._frameworks.items()]

    def analyze(self, destiny: dict, perspective_ids: list = None) -> dict:
        if perspective_ids is None:
            perspective_ids = list(self._frameworks.keys())[:5]

        analytics = get_all_analytics(destiny)
        results = {}
        for pid in perspective_ids:
            if pid in self._frameworks:
                try:
                    result = self._frameworks[pid].analyze(destiny, analytics)
                    result["perspective"] = self._frameworks[pid].name
                    result["title"] = self._frameworks[pid].title
                    result["id"] = pid
                    results[pid] = result
                except Exception as e:
                    results[pid] = {
                        "perspective": self._frameworks[pid].name,
                        "title": self._frameworks[pid].title,
                        "score": 0,
                        "confidence": 0,
                        "summary": f"分析异常: {e}",
                        "dimensions": [],
                        "key_insights": [],
                        "warnings": [],
                        "advice": [],
                    }
        return results
