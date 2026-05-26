#!/usr/bin/env python3
"""
玄照 · 深度视角引擎 — 基础模块
包含公用分析函数和抽象视角基类。
"""

from typing import Optional
from abc import ABC, abstractmethod

# 模板视角数据（78个批量生成视角）
from perspectives_templates import TEMPLATE_PERSPECTIVES

# ==========================================
# 五行基础数据（从 data/wuxing.yaml 加载，回退到硬编码）
# ==========================================
_GAN_WUXING_HARDCODED = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
               "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
_ZHI_WUXING_HARDCODED = {"寅":"木","卯":"木","巳":"火","午":"火",
               "辰":"土","戌":"土","丑":"土","未":"土",
               "申":"金","酉":"金","亥":"水","子":"水"}
_WUXING_CYCLE_HARDCODED = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
_WUXING_CONQUER_HARDCODED = {"木":"土","土":"水","水":"火","火":"金","金":"木"}
_WUXING_COLORS_HARDCODED = {"木":"绿色","火":"红色","土":"黄色","金":"白色","水":"黑色"}

import os
try:
    import yaml
    _wuxing_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "wuxing.yaml")
    with open(_wuxing_path, encoding="utf-8") as _f:
        _wd = yaml.safe_load(_f) or {}
    _GAN_WUXING = _wd.get("gan_wuxing", _GAN_WUXING_HARDCODED)
    _ZHI_WUXING = _wd.get("zhi_wuxing", _ZHI_WUXING_HARDCODED)
    _WUXING_CYCLE = _wd.get("wuxing_cycle", _WUXING_CYCLE_HARDCODED)
    _WUXING_CONQUER = _wd.get("wuxing_conquer", _WUXING_CONQUER_HARDCODED)
    _WUXING_COLORS = _wd.get("wuxing_colors", _WUXING_COLORS_HARDCODED)
except (FileNotFoundError, ImportError, Exception):
    _GAN_WUXING = _GAN_WUXING_HARDCODED
    _ZHI_WUXING = _ZHI_WUXING_HARDCODED
    _WUXING_CYCLE = _WUXING_CYCLE_HARDCODED
    _WUXING_CONQUER = _WUXING_CONQUER_HARDCODED
    _WUXING_COLORS = _WUXING_COLORS_HARDCODED


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
        
        # 加入名言引用（从模板视角配置的quotes字段）
        quote_text = ""
        if hasattr(self, '_cfg') and self._cfg.get("quotes"):
            qs = self._cfg["quotes"]
            if qs:
                quote_text = f"\n\n如我所言：「{qs[0]}」"
                if len(qs) > 1:
                    quote_text += f"\n又如：「{qs[1]}」"
        
        # 加入著作引用
        works_text = ""
        if hasattr(self, '_cfg') and self._cfg.get("works"):
            ws = self._cfg["works"][:2]
            if ws:
                works_text = f"\n\n上述论断，可参阅{'、'.join(ws)}以知其详。"
        
        return f"{p1}\n\n{p2}\n\n{p3}{quote_text}{works_text}"
