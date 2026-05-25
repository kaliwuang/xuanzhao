#!/usr/bin/env python3
"""
玄照 · XuanZhao — 玄学群体智能预测系统
独立 CLI 版本，无需 Hermes Agent

用法:
  python xuanzhao.py analyze --birth "2005-06-09 11:50" --location "呼和浩特" --gender male
  python xuanzhao.py predict --birth "2005-06-09 11:50" --location "呼和浩特" --gender male --api-key "sk-..."
  python xuanzhao.py perspectives --list
"""

import argparse, json, os, sys, re, math
from datetime import datetime
from typing import Optional

# 深度视角引擎（12个核心视角基于实际命盘数据计算分析）
try:
    from perspectives_engine import DeepPerspectiveEngine
    DEEP_ENGINE = DeepPerspectiveEngine()
    DEEP_OK = True
except ImportError:
    DEEP_OK = False

# ========================
# 引擎版本
# ========================
VERSION = "1.2.0"

# ========================
# 八字排盘模块
# ========================
class BaziEngine:
    """基于 lunar_python 的八字排盘"""

    def __init__(self):
        self._available = False
        try:
            from lunar_python import Solar, EightChar
            self.Solar = Solar
            self.EightChar = EightChar
            self._available = True
        except ImportError:
            pass

    def analyze(self, year: int, month: int, day: int, hour: int, minute: int, gender: int) -> dict:
        if not self._available:
            return {"error": "lunar_python not installed", "available": False}

        solar = self.Solar.fromYmdHms(year, month, day, hour, minute, 0)
        lunar = solar.getLunar()
        ec = self.EightChar(lunar)

        # 四柱
        result = {
            "bazi": {
                "year": ec.getYearGan() + ec.getYearZhi(),
                "month": ec.getMonthGan() + ec.getMonthZhi(),
                "day": ec.getDayGan() + ec.getDayZhi(),
                "time": ec.getTimeGan() + ec.getTimeZhi(),
            },
            "nayin": {
                "year": ec.getYearNaYin(),
                "month": ec.getMonthNaYin(),
                "day": ec.getDayNaYin(),
                "time": ec.getTimeNaYin(),
            },
            "hidden_gans": {
                "year": ec.getYearHideGan(),
                "month": ec.getMonthHideGan(),
                "day": ec.getDayHideGan(),
                "time": ec.getTimeHideGan(),
            },
            "shishen": {
                "year": ec.getYearShiShenGan(),
                "month": ec.getMonthShiShenGan(),
                "day": ec.getDayShiShenGan(),
                "time": ec.getTimeShiShenGan(),
            },
            "xunkong": {
                "year": ec.getYearXunKong(),
                "day": ec.getDayXunKong(),
            },
            "minggong": ec.getMingGong(),
            "taiyuan": ec.getTaiYuan(),
            "shengong": ec.getShenGong(),
        }

        # 大运
        try:
            yun = ec.getYun(gender=gender)
            dayun_list = []
            for d in yun.getDaYun():
                gz = d.getGanZhi()
                if gz:
                    dayun_list.append({
                        "start": d.getStartYear(),
                        "end": d.getStartYear() + 9,
                        "ganzhi": gz,
                    })
            result["dayun"] = dayun_list
            result["start_year"] = yun.getStartYear()
        except Exception:
            result["dayun"] = []

        # 日主五行分析
        day_gan = ec.getDayGan()
        gan_wuxing = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                      "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
        result["day_master"] = {
            "gan": day_gan,
            "wuxing": gan_wuxing.get(day_gan, "?"),
        }

        return result


# ========================
# 西洋占星模块
# ========================
class AstrologyEngine:
    def __init__(self):
        self._available = False
        try:
            import swisseph as swe
            self.swe = swe
            self._available = True
        except ImportError:
            pass

    def analyze(self, year: int, month: int, day: int, hour: float, lat: float, lon: float) -> dict:
        if not self._available:
            return {"error": "pyswisseph not installed", "available": False}

        jd = self.swe.julday(year, month, day, hour)
        signs = ['白羊','金牛','双子','巨蟹','狮子','处女',
                 '天秤','天蝎','射手','摩羯','水瓶','双鱼']

        planets = {}
        for pid, pname in [
            (self.swe.SUN, '太阳'), (self.swe.MOON, '月亮'),
            (self.swe.MERCURY, '水星'), (self.swe.VENUS, '金星'),
            (self.swe.MARS, '火星'), (self.swe.JUPITER, '木星'),
            (self.swe.SATURN, '土星'), (self.swe.URANUS, '天王星'),
            (self.swe.NEPTUNE, '海王星'), (self.swe.PLUTO, '冥王星'),
        ]:
            pos = self.swe.calc_ut(jd, pid)
            lon_deg = pos[0][0]
            sign_idx = int(lon_deg / 30)
            planets[pname] = {
                "longitude": round(lon_deg, 2),
                "sign": signs[sign_idx] if sign_idx < 12 else "?",
                "degree": round(lon_deg % 30, 2),
            }

        # 宫位
        try:
            cusps, ascmc = self.swe.houses(jd, lat, lon, ord('P'))
            ascendant = cusps[0]
            mc = ascmc[1]
            houses = [round(c, 2) for c in cusps[:12]]
        except:
            ascendant = 0
            mc = 0
            houses = []

        return {
            "planets": planets,
            "ascendant": round(ascendant, 2),
            "mc": round(mc, 2),
            "houses": houses,
        }


# ========================
# 命理分析综合
# ========================
class DestinyAnalyzer:
    """综合七术分析"""

    def __init__(self):
        self.bazi = BaziEngine()
        self.astro = AstrologyEngine()

    def analyze(self, birth_str: str, location: str, gender: str) -> dict:
        # 解析出生时间
        dt = self._parse_birth(birth_str)
        if not dt:
            return {"error": f"无法解析出生时间: {birth_str}"}

        year, month, day = dt.year, dt.month, dt.day
        hour = dt.hour + dt.minute / 60.0
        gender_code = 1 if gender in ('男', 'male', 'm') else 0

        # 经纬度
        lat, lon = self._get_location(location)

        result = {
            "birth": birth_str,
            "location": location,
            "gender": gender,
            "datetime": dt.isoformat(),
        }

        # 八字分析
        bazi_result = self.bazi.analyze(year, month, day, dt.hour, dt.minute, gender_code)
        if "error" not in bazi_result:
            result["bazi"] = bazi_result

        # 占星分析
        astro_result = self.astro.analyze(year, month, day, hour, lat, lon)
        if "error" not in astro_result:
            result["astrology"] = astro_result

        # 调候用神
        result["tiaohou"] = self._calc_tiaohou(bazi_result)

        # 综合特征
        result["features"] = self._extract_features(result)

        return result

    def _parse_birth(self, s: str) -> Optional[datetime]:
        for fmt in ["%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y-%m-%dT%H:%M",
                     "%Y%m%d %H%M", "%Y-%m-%d %H", "%Y-%m-%d"]:
            try:
                return datetime.strptime(s, fmt)
            except:
                continue
        return None

    def _get_location(self, loc: str) -> tuple:
        # 城市经纬度查询
        cities = {
            "北京": (39.9, 116.4), "上海": (31.2, 121.5), "广州": (23.1, 113.3),
            "深圳": (22.5, 114.1), "杭州": (30.3, 120.2), "成都": (30.6, 104.1),
            "武汉": (30.6, 114.3), "南京": (32.1, 118.8), "重庆": (29.6, 106.6),
            "西安": (34.3, 108.9), "呼和浩特": (40.8, 111.7), "天津": (39.1, 117.2),
            "苏州": (31.3, 120.6), "长沙": (28.2, 112.9), "郑州": (34.8, 113.7),
            "东莞": (23.0, 113.8), "青岛": (36.1, 120.4), "沈阳": (41.8, 123.4),
            "宁波": (29.9, 121.5), "昆明": (25.0, 102.7), "大连": (38.9, 121.6),
            "厦门": (24.5, 118.1), "合肥": (31.8, 117.3), "佛山": (23.0, 113.1),
            "福州": (26.1, 119.3), "哈尔滨": (45.8, 126.6), "济南": (36.7, 116.9),
            "温州": (28.0, 120.7), "长春": (43.9, 125.3), "石家庄": (38.0, 114.5),
            "常州": (31.8, 119.9), "泉州": (24.9, 118.6), "南宁": (22.8, 108.4),
            "贵阳": (26.6, 106.7), "南昌": (28.7, 115.9), "太原": (37.9, 112.5),
            "烟台": (37.5, 121.4), "嘉兴": (30.8, 120.8), "南通": (32.0, 120.9),
            "金华": (29.1, 119.6), "珠海": (22.3, 113.6), "徐州": (34.3, 117.2),
            "海口": (20.0, 110.3), "乌鲁木齐": (43.8, 87.6), "绍兴": (30.0, 120.6),
            "中山": (22.5, 113.4), "台州": (28.7, 121.4), "兰州": (36.1, 103.8),
        }
        if loc in cities:
            return cities[loc]
        # 默认北京
        return (39.9, 116.4)

    def _calc_tiaohou(self, bazi_result: dict) -> dict:
        """调候用神计算"""
        if "error" in bazi_result:
            return {}
        month_zhi = bazi_result.get("bazi", {}).get("month", "?")[1] if len(bazi_result.get("bazi", {}).get("month", "?")) > 1 else "?"
        day_gan = bazi_result.get("day_master", {}).get("gan", "?")

        tiaohou_table = {
            ("甲","午"): "癸", ("甲","子"): "丙", ("甲","寅"): "丙癸",
            ("乙","午"): "癸", ("乙","子"): "丙", ("乙","寅"): "丙",
            ("丙","午"): "癸", ("丙","子"): "壬戊", ("丙","寅"): "壬庚",
            ("丁","午"): "癸", ("丁","子"): "甲壬", ("丁","寅"): "甲庚",
            ("戊","午"): "丙癸", ("戊","子"): "丙甲癸", ("戊","寅"): "丙甲癸",
            ("己","午"): "癸丙", ("己","子"): "甲丙", ("己","寅"): "丙甲癸",
            ("庚","午"): "壬", ("庚","子"): "壬丙", ("庚","寅"): "丙甲",
            ("辛","午"): "壬辛", ("辛","子"): "壬辛", ("辛","寅"): "壬庚",
            ("壬","午"): "庚辛壬", ("壬","子"): "庚辛", ("壬","寅"): "庚丙",
            ("癸","午"): "庚辛壬", ("癸","子"): "辛丙", ("癸","寅"): "丙庚",
        }

        key = (day_gan, month_zhi)
        yongshen = tiaohou_table.get(key, "")
        return {
            "day_gan": day_gan,
            "month_zhi": month_zhi,
            "yongshen": yongshen,
            "description": f"调候用神为【{yongshen}】" if yongshen else "调候用神需综合判断"
        }

    def _extract_features(self, result: dict) -> list:
        features = []
        bazi = result.get("bazi", {})
        ba = bazi.get("bazi", {})

        # 子午冲
        if ba.get("day","") and ba.get("month",""):
            if "子" in ba["day"] and "午" in ba["month"]:
                features.append("子午冲 — 核心矛盾：印星与食伤相冲，吸收与表达之间的张力")
            if "午" in ba["day"] and "子" in ba["month"]:
                features.append("子午冲 — 核心矛盾")

        # 七杀透干
        ss = bazi.get("shishen", {})
        if "七杀" in ss.get("time", ""):
            features.append("七杀透干时柱 — 自我驱动力强，但压力大，需印化解")
        if "七杀" in ss.get("month", ""):
            features.append("七杀当令 — 竞争意识强，早年多磨练")

        # 印星
        if "印" in ss.get("day", ""):
            features.append("日坐印星 — 内心有根基，学习能力强")
        if "印" not in str(ss.get("day","")) and "印" not in str(ss.get("month","")):
            features.append("印星不显 — 可能缺乏外部支持系统")

        # 财星
        for pos in ["year","month","day","time"]:
            if "财" in ss.get(pos,""):
                features.append(f"{'年柱' if pos=='year' else '月柱' if pos=='month' else '日支' if pos=='day' else '时柱'}见财")
                break

        return features[:8]


# ========================
# 视角库（内置核心视角）
# ========================
PERSPECTIVES = {
    "zhuge-liang": {
        "name": "诸葛亮",
        "title": "隆中对全局推演",
        "models": [
            "全局推演法：从整体格局出发，分析各方势力、资源、时机，找出最优路径",
            "借势而为：不凭蛮力，利用对手的力量和外部环境变化达成目标",
            "以逸待劳：在不利局面下保存实力，等待对方犯错",
            "多算胜少算：决策前穷尽可能的变量，做得越多胜算越大",
        ],
        "prompt": "你以诸葛亮隆中对式的全局思维分析这个命局。看格局不看细节，找核心矛盾而非表面现象。"
    },
    "yuan-tiangang": {
        "name": "袁天罡",
        "title": "骨相推命运分段",
        "models": [
            "骨相推命法：先天结构决定命运格局，大框架从小细节可窥",
            "命运分段论：人生分段看——少年看骨（潜力）、中年看气（运势）、晚年看神（修为）",
            "大运国运联动：个人命运嵌在时代中，不能脱离时代谈个人",
        ],
        "prompt": "你以袁天罡推背图式的格局思维看这个命局。关注命运的大框架和关键转折点。"
    },
    "feynman": {
        "name": "费曼",
        "title": "简化核心机制",
        "models": [
            "第一性原理：回到最基本的物理定律，不给任何权威结论留豁免权",
            "费曼学习法：如果你不能简单地解释它，说明你没真正理解",
            "不要欺骗自己：你自己是最容易欺骗的人",
        ],
        "prompt": "你以费曼的精神分析这个命局——简化到核心机制，去除所有玄学术语包装，用最直白的话说清楚本质。"
    },
    "jung": {
        "name": "荣格",
        "title": "集体无意识与阴影",
        "models": [
            "个体化（Individuation）：成为完整的自己，而非完美的自己",
            "阴影整合：你最讨厌的别人的特质，往往是你自己的阴影投射",
            "共时性（Synchronicity）：有意义的巧合不是偶然",
        ],
        "prompt": "你以荣格分析心理学视角看这个命局。关注阴影、原型、个体化进程。"
    },
    "munger": {
        "name": "芒格",
        "title": "多元思维模型",
        "models": [
            "逆向思维：要得到X，先想想什么会阻碍X，然后避开它们",
            "心理模型网格：用100+个跨学科模型做决策，而不是只用一两个",
            "人类误判心理学：25种心理倾向如何影响判断",
        ],
        "prompt": "你以芒格的逆向思维和多元模型分析这个命局。关注避坑而非追求。"
    },
    "taleb": {
        "name": "Taleb",
        "title": "反脆弱与黑天鹅",
        "models": [
            "反脆弱：有些东西越挫越强——命局的逆境可能是隐藏的优势",
            "黑天鹅：最重大的事件往往是无法预测的",
            "凸性策略：在损失有限但收益无限的方向下注",
        ],
        "prompt": "你以Taleb的反脆弱思维分析这个命局。关注隐藏的风险和韧性。"
    },
    "naval": {
        "name": "Naval",
        "title": "长期主义与杠杆",
        "models": [
            "特定知识：无法通过培训获得的知识才是真正的护城河",
            "杠杆：代码、媒体、资本——用杠杆放大个人产出",
            "复利：选择那些随年龄增长而增值的职业和能力",
        ],
        "prompt": "你以Naval的长期主义视角分析这个命局。关注什么能力能在时间中产生复利。"
    },
    "laozi": {
        "name": "老子",
        "title": "道法自然",
        "models": [
            "无为而治：过度干预适得其反，顺应本性的发展最有效率",
            "反者道之动：物极必反——命局最弱的点可能是最大的潜力",
            "上善若水：不争之争，柔弱胜刚强",
        ],
        "prompt": "你以老子道家智慧分析这个命局。关注顺势、不争、回归本质。"
    },
    "sun-tzu": {
        "name": "孙子",
        "title": "知己知彼",
        "models": [
            "知己知彼：信息=胜利，了解自己的优势和对手的弱点",
            "不战而屈人之兵：最高明的胜利是不用打",
            "以正合以奇胜：常规手段和出其不意相结合",
        ],
        "prompt": "你以孙子兵法视角分析这个命局。关注战略位置和竞争策略。"
    },
    "stoic": {
        "name": "斯多葛",
        "title": "控制二分法",
        "models": [
            "控制二分法：有些事由你决定（判断、行动），有些不由你决定（结果、他人评价）",
            "消极想象：预演最坏的情况，就不再恐惧",
            "逆境即磨炼：真正的成长来自于如何面对困难",
        ],
        "prompt": "你以斯多葛哲学视角分析这个命局。关注可控与不可控的边界。"
    },
    "socrates": {
        "name": "苏格拉底",
        "title": "反诘法追问",
        "models": [
            "精神助产术：通过提问让别人自己发现答案",
            "反诘法：不断追问直至抵达本质",
            "无知之知：'我唯一知道的就是我一无所知'——保持质疑",
        ],
        "prompt": "你以苏格拉底的提问精神分析这个命局。不断追问'为什么'直到找到根源。"
    },
    "wang-yangming": {
        "name": "王阳明",
        "title": "知行合一",
        "models": [
            "心即理：答案在内不在外，外部知识只有在被内心验证后才算真正理解",
            "知行合一：知道却做不到=不知道",
            "事上练：在具体事务中磨炼心性",
        ],
        "prompt": "你以王阳明心学视角分析这个命局。关注认知与行动的关系。"
    },
}


class PerspectiveEngine:
    """视角引擎 — 加载视角框架，生成分析提示"""

    def __init__(self):
        self.perspectives = PERSPECTIVES

    def list_all(self) -> list:
        return [{"id": k, "name": v["name"], "title": v["title"]}
                for k, v in self.perspectives.items()]

    def analyze(self, destiny_data: dict, perspective_ids: list = None) -> dict:
        if not perspective_ids:
            perspective_ids = list(self.perspectives.keys())[:5]

        # 提取关键命理信息
        summary = self._destiny_summary(destiny_data)

        results = {}
        for pid in perspective_ids:
            if pid not in self.perspectives:
                continue
            p = self.perspectives[pid]
            results[pid] = {
                "perspective": p["name"],
                "title": p["title"],
                "models": p["models"],
                "prompt": p["prompt"],
                "context": summary,
            }
        return results

    def deep_analyze(self, destiny_data: dict, deep_ids: list = None, shallow_count: int = 3) -> dict:
        """深度分析：核心视角用计算引擎，其余用 prompt 模板"""
        results = {}
        if deep_ids is None:
            deep_ids = list(DEEP_ENGINE._frameworks.keys()) if DEEP_OK else []
        # 1. 深度视角
        if DEEP_OK and deep_ids:
            deep_results = DEEP_ENGINE.analyze(destiny_data, deep_ids)
            results.update(deep_results)
        # 2. 补充浅层视角
        shallow_ids = [k for k in list(self.perspectives.keys())[:shallow_count]
                      if k not in results]
        if shallow_ids:
            shallow = self.analyze(destiny_data, shallow_ids)
            results.update(shallow)
        return results

    def _destiny_summary(self, data: dict) -> str:
        parts = []
        bazi = data.get("bazi", {})
        ba = bazi.get("bazi", {})

        if ba:
            parts.append(f"八字: {ba.get('year','?')} {ba.get('month','?')} {ba.get('day','?')} {ba.get('time','?')}")

        day_master = bazi.get("day_master", {})
        if day_master:
            parts.append(f"日主: {day_master.get('gan','?')}（{day_master.get('wuxing','?')}）")

        features = data.get("features", [])
        if features:
            parts.append(f"核心特征: {'; '.join(features[:3])}")

        tiaohou = data.get("tiaohou", {})
        if tiaohou.get("yongshen"):
            parts.append(f"调候用神: {tiaohou['yongshen']}")

        dayun = bazi.get("dayun", [])
        if dayun:
            current = [d for d in dayun if d["start"] <= 2026 <= d["end"]]
            if current:
                parts.append(f"当前大运: {current[0]['ganzhi']} ({current[0]['start']}-{current[0]['end']})")

        return "\n".join(parts)


# ========================
# 报告生成模块
# ========================
class ReportGenerator:
    """生成结构化预测报告"""

    def generate(self, destiny: dict, perspectives: dict, output_format: str = "markdown") -> str:
        if output_format == "json":
            return json.dumps({"destiny": destiny, "perspectives": perspectives}, ensure_ascii=False, indent=2)

        # Markdown 报告
        lines = []
        lines.append("╔══════════════════════════════════════════╗")
        lines.append("║         玄照 · 玄学群体智能预测报告      ║")
        lines.append("╚══════════════════════════════════════════╝")
        lines.append("")

        # 基本信息
        lines.append(f"**命主信息**")
        lines.append(f"- 出生：{destiny.get('birth','?')}　{ destiny.get('location','?')}")
        lines.append(f"- 性别：{destiny.get('gender','?')}")
        lines.append("")

        # 八字
        bazi = destiny.get("bazi", {})
        ba = bazi.get("bazi", {})
        if ba:
            lines.append("**八字命盘**")
            lines.append(f"> {ba.get('year','?')}　{ba.get('month','?')}　{ba.get('day','?')}　{ba.get('time','?')}")
            dm = bazi.get("day_master", {})
            lines.append(f"> 日主：{dm.get('gan','?')}{dm.get('wuxing','?')}")
            features = destiny.get("features", [])
            for f in features:
                lines.append(f"> ⚡ {f}")
            lines.append("")

        # 调候用神
        th = destiny.get("tiaohou", {})
        if th.get("yongshen"):
            lines.append(f"**调候用神：{th['yongshen']}**")
            lines.append("")

        # 大运
        dayun = bazi.get("dayun", [])
        if dayun:
            lines.append("**大运轨迹**")
            for d in dayun:
                marker = " ← 当前" if d["start"] <= 2026 <= d["end"] else ""
                lines.append(f"| {d['ganzhi']}　({d['start']}-{d['end']}){marker}")
            lines.append("")

        # 多视角解读
        lines.append("---")
        lines.append("## 多视角解读")
        lines.append("")

        for pid, pdata in perspectives.items():
            lines.append(f"### {pdata['perspective']} · {pdata['title']}")
            lines.append("")

            # 深度视角（有score和dimensions）
            if "score" in pdata:
                lines.append(f"**综合评分：{pdata['score']}/100**　置信度：{int(pdata.get('confidence',0)*100)}%")
                lines.append("")
                lines.append(f"> {pdata.get('summary','')}")
                lines.append("")
                # 维度
                for d in pdata.get("dimensions", []):
                    bar = "█" * (d["score"] // 10) + "░" * (10 - d["score"] // 10)
                    lines.append(f"- **{d['name']}**　{d['score']}/100　`{bar}`")
                    lines.append(f"  _{d['detail']}_")
                    lines.append("")
                # 洞察
                insights = pdata.get("key_insights", [])
                if insights:
                    lines.append("**关键洞察：**")
                    for ins in insights:
                        lines.append(f"- 🔍 {ins}")
                    lines.append("")
                # 警告
                warnings = pdata.get("warnings", [])
                if warnings:
                    lines.append("**风险预警：**")
                    for w in warnings:
                        lines.append(f"- ⚠ {w}")
                    lines.append("")
                # 建议
                advice = pdata.get("advice", [])
                if advice:
                    lines.append("**行动建议：**")
                    for a in advice:
                        lines.append(f"- 📌 {a}")
                    lines.append("")
            else:
                # 旧格式兼容
                lines.append(f"**心智模型：**")
                for model in pdata.get("models", []):
                    lines.append(f"- {model}")
                lines.append("")
                lines.append(f"**命盘数据：**")
                lines.append("```")
                lines.append(pdata.get("context", ""))
                lines.append("```")
                lines.append("")

        # 评分汇总
        score_summary = []
        for pid, pdata in perspectives.items():
            if "score" in pdata:
                score_summary.append(f"- {pdata['perspective']}: **{pdata['score']}/100**")
        if score_summary:
            lines.append("---")
            lines.append("## 综合评分汇总")
            lines.append("")
            lines.extend(score_summary)
            lines.append("")

        # 使用说明
        lines.append("---")

        return "\n".join(lines)


# ========================
# CLI 入口
# ========================
def main():
    parser = argparse.ArgumentParser(
        description=f"玄照 v{VERSION} — 玄学群体智能预测系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python xuanzhao.py analyze --birth "2005-06-09 11:50" --location "呼和浩特" --gender male
  python xuanzhao.py predict --birth "2005-06-09 11:50" --location "呼和浩特" --gender male --api-key "sk-..."
  python xuanzhao.py perspectives --list
  python xuanzhao.py demo
        """
    )

    parser.add_argument("--version", action="version", version=f"玄照 v{VERSION}")
    sub = parser.add_subparsers(dest="command", help="子命令")

    # analyze
    p_analyze = sub.add_parser("analyze", help="命理分析")
    p_analyze.add_argument("--birth", required=True, help="出生时间 (如 2005-06-09 11:50)")
    p_analyze.add_argument("--location", default="北京", help="出生地点 (城市名)")
    p_analyze.add_argument("--gender", default="男", help="性别 (男/女)")
    p_analyze.add_argument("--format", default="markdown", choices=["markdown","json"])

    # predict
    p_predict = sub.add_parser("predict", help="完整预测")
    p_predict.add_argument("--birth", required=True)
    p_predict.add_argument("--location", default="北京")
    p_predict.add_argument("--gender", default="男")
    p_predict.add_argument("--api-key", help="OpenAI 兼容 API Key")
    p_predict.add_argument("--api-url", default="https://api.openai.com/v1", help="API 地址")
    p_predict.add_argument("--model", default="gpt-4o", help="模型名")
    p_predict.add_argument("--perspectives", default="auto", help="视角ID列表(逗号分隔)或auto")

    # perspectives
    p_pers = sub.add_parser("perspectives", help="视角管理")
    p_pers.add_argument("--list", action="store_true", help="列出所有视角")

    # demo
    p_demo = sub.add_parser("demo", help="生成示例报告")
    p_demo.add_argument("--output", default=None, help="输出文件路径")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    analyzer = DestinyAnalyzer()
    pers_engine = PerspectiveEngine()
    reporter = ReportGenerator()

    if args.command == "perspectives" and args.list:
        all_deep = DEEP_ENGINE.list() if DEEP_OK else []
        all_shallow = pers_engine.list_all()
        print(f"\n📚 玄照视角库\n")
        print(f"深度视角（12个核心——基于命盘数据计算）：")
        for p in all_deep:
            print(f"  🔴 {p['id']:30s} {p['name']} — {p['title']}")
        print()
        print(f"浅层视角（{len(all_shallow)}个——prompt模板）：")
        for p in all_shallow:
            print(f"  ⚪ {p['id']:30s} {p['name']} — {p['title']}")
        print(f"\n总计：{len(all_deep)} 深度 + {len(all_shallow)} 浅层")
        return

    if args.command == "demo":
        birth = "2005-06-09 11:50"
        location = "呼和浩特"
        gender = "男"
        print(f"🔄 正在分析 {birth} {location}...")
        destiny = analyzer.analyze(birth, location, gender)
        if "error" in destiny:
            print(f"❌ {destiny['error']}")
            return
        print(f"✅ 命盘分析完成，运行深度视角引擎...")
        # 使用深度视角
        deep_ids = list(DEEP_ENGINE._frameworks.keys())[:8] if DEEP_OK else None
        pers_result = pers_engine.deep_analyze(destiny, deep_ids, shallow_count=0)
        report = reporter.generate(destiny, pers_result, "markdown")
        print(report)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n✅ 已保存到 {args.output}")
        return

    # analyze or predict
    print(f"🔄 正在分析 {args.birth} {args.location}...")
    destiny = analyzer.analyze(args.birth, args.location, args.gender)
    if "error" in destiny:
        print(f"❌ {destiny['error']}")
        return

    # 视角选择——优先使用深度视角
    if args.command == "predict" and args.perspectives != "auto":
        pids = [p.strip() for p in args.perspectives.split(",")]
        pers_result = pers_engine.deep_analyze(destiny, pids, 0)
    else:
        # 默认：全部12个深度视角 + 3个浅层补充
        deep_ids = list(DEEP_ENGINE._frameworks.keys())[:8] if DEEP_OK else None
        pers_result = pers_engine.deep_analyze(destiny, deep_ids, shallow_count=3)

    if args.command == "predict" and args.api_key:
        # LLM 预测模式
        print("🤖 调用 AI 生成预测报告...")
        # TODO: 调用 LLM API
        print("⚠️ LLM 预测模式需要实现，暂时使用本地引擎")
        report = reporter.generate(destiny, pers_result, args.format)
    else:
        report = reporter.generate(destiny, pers_result, args.format)

    print(report)


if __name__ == "__main__":
    main()
