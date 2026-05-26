#!/usr/bin/env python3
"""
玄照 · 分析引擎 — 八字排盘、西洋占星、综合命理分析
"""
import json, os, sys, re, math
from datetime import datetime
from typing import Optional


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

        # 从 data/tiaohou.yaml 加载调候表，回退到硬编码
        tiaohou_hardcoded = {
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

        tiaohou_table = {}
        try:
            import yaml, os
            _th_path = os.path.join(os.path.dirname(__file__), "..", "data", "tiaohou.yaml")
            with open(_th_path, encoding="utf-8") as _f:
                _th_data = yaml.safe_load(_f) or {}
            for dg, month_map in _th_data.items():
                for mz, ys in month_map.items():
                    tiaohou_table[(dg, mz)] = ys
        except (FileNotFoundError, ImportError, Exception):
            tiaohou_table = tiaohou_hardcoded

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
