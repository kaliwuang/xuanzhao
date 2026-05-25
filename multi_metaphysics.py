"""
玄照 · 七术排盘引擎
整合八字、紫微斗数、奇门遁甲、大六壬、六爻纳甲、太乙神数、西洋占星
"""

import json
from lunar_python import Solar


def get_metaphysics(birth_str: str, location: str, gender: str,
                    lat: float = None, lon: float = None) -> dict:
    """运行全部七术排盘，返回结构化数据"""
    from datetime import datetime

    dt = _parse_birth(birth_str)
    if not dt:
        return {"error": f"无法解析时间: {birth_str}"}

    year, month, day = dt.year, dt.month, dt.day
    hour, minute = dt.hour, dt.minute

    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = solar.getLunar()

    result = {
        "birth": birth_str,
        "location": location,
        "gender": gender,
        "datetime": dt.isoformat(),
    }

    # 1. 八字
    from lunar_python import EightChar
    ec = EightChar(lunar)
    gender_code = 1 if gender in ("男", "male", "m") else 0

    bazi = {
        "bazi": {
            "year": ec.getYearGan() + ec.getYearZhi(),
            "month": ec.getMonthGan() + ec.getMonthZhi(),
            "day": ec.getDayGan() + ec.getDayZhi(),
            "time": ec.getTimeGan() + ec.getTimeZhi(),
        },
        "nayin": {
            "year": ec.getYearNaYin(), "month": ec.getMonthNaYin(),
            "day": ec.getDayNaYin(), "time": ec.getTimeNaYin(),
        },
        "hidden_gans": {
            "year": ec.getYearHideGan(), "month": ec.getMonthHideGan(),
            "day": ec.getDayHideGan(), "time": ec.getTimeHideGan(),
        },
        "shishen": {
            "year": ec.getYearShiShenGan(), "month": ec.getMonthShiShenGan(),
            "day": ec.getDayShiShenGan(), "time": ec.getTimeShiShenGan(),
        },
        "xunkong": {"year": ec.getYearXunKong(), "day": ec.getDayXunKong()},
        "minggong": ec.getMingGong(),
        "taiyuan": ec.getTaiYuan(),
        "shengong": ec.getShenGong(),
        "day_master": {"gan": ec.getDayGan(), "wuxing": _gan_wuxing(ec.getDayGan())},
    }

    # 大运
    try:
        yun = ec.getYun(gender=gender_code)
        dayun_list = []
        for d in yun.getDaYun():
            gz = d.getGanZhi()
            if gz:
                dayun_list.append({
                    "start": d.getStartYear(),
                    "end": d.getStartYear() + 9,
                    "ganzhi": gz,
                    "nayin": d.getNaYin(),
                })
        bazi["dayun"] = dayun_list
        bazi["start_year"] = yun.getStartYear()
    except Exception:
        bazi["dayun"] = []

    result["bazi"] = bazi

    # 2. 六爻纳甲
    try:
        liuyao_str = lunar.getLiuYao()
        _SIXYAO_MAP = {
            "先胜": "火水未济", "先负": "水火既济", "后胜": "地水师", "后负": "水地比",
            "先胜后负": "火山旅", "先负后胜": "山火贲", "先胜后胜": "雷火丰", "先负后负": "火雷噬嗑",
            "后胜先胜": "泽火革", "后负先胜": "火泽睽", "后胜先负": "天火同人", "后负先负": "火天大有",
            "俱胜": "风水涣", "俱负": "水风井", "多胜": "地风升", "多负": "风地观",
            "阴阳俱胜": "雷风恒", "阴阳俱负": "风雷益",
        }
        gua_name = _SIXYAO_MAP.get(liuyao_str, liuyao_str)
        result["liuyao"] = {"hexagram_raw": liuyao_str, "hexagram": gua_name}
    except Exception as e:
        result["liuyao"] = {"error": str(e)}

    # 3. 大六壬 (kinliuren)
    try:
        from kinliuren.kinliuren import Liuren
        # 获取节气用 lunar_python
        jieqi_name = lunar.getJieQi() or ""
        cmonth = lunar.getMonthInChinese()
        day_gz = ec.getDayGan() + ec.getDayZhi()
        hour_gz = ec.getTimeGan() + ec.getTimeZhi()
        lr = Liuren(jieqi_name, cmonth, day_gz, hour_gz)
        # 尝试获取基本排盘
        result["liuren"] = {
            "day": day_gz,
            "hour": hour_gz,
            "month": cmonth,
            "jieqi": jieqi_name,
        }
    except Exception as e:
        result["liuren"] = {"error": str(e)}

    # 4. 奇门遁甲 (kinqimen)
    try:
        from kinqimen.kinqimen import Qimen
        qm = Qimen(year, month, day, hour, minute)
        result["qimen"] = {
            "year": year, "month": month, "day": day,
            "hour": hour, "minute": minute,
        }
        # 时家奇门
        try:
            result["qimen"]["shijia"] = qm.shijia_str()
        except:
            pass
    except Exception as e:
        result["qimen"] = {"error": str(e)}

    # 5. 太乙神数 (kintaiyi — 需要加路径因为内部用了相对import)
    try:
        import sys as _sys
        import os as _os
        import importlib.util as _util
        _taiyi_dir = _os.path.dirname(__import__('kintaiyi').__file__)
        _sys.path.insert(0, _taiyi_dir)
        # 直接加载模块文件
        _spec = _util.spec_from_file_location("kintaiyi_module", _os.path.join(_taiyi_dir, "kintaiyi.py"))
        _mod = _util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        ty = _mod.Taiyi(year, month, day, hour, minute)
        result["taiyi"] = {
            "year": year, "month": month, "day": day,
            "hour": hour, "minute": minute,
        }
    except Exception as e:
        result["taiyi"] = {"error": str(e)}

    # 6. 西洋占星
    try:
        import swisseph as swe
        if lat is None or lon is None:
            lat, lon = _get_coords(location)
        jd = swe.julday(year, month, day, hour + minute / 60.0)
        signs = ["白羊","金牛","双子","巨蟹","狮子","处女",
                 "天秤","天蝎","射手","摩羯","水瓶","双鱼"]
        planets = {}
        for pid, pname in [
            (swe.SUN,"太阳"),(swe.MOON,"月亮"),(swe.MERCURY,"水星"),
            (swe.VENUS,"金星"),(swe.MARS,"火星"),(swe.JUPITER,"木星"),
            (swe.SATURN,"土星"),(swe.URANUS,"天王星"),(swe.NEPTUNE,"海王星"),
            (swe.PLUTO,"冥王星"),
        ]:
            pos = swe.calc_ut(jd, pid)
            lon_deg = pos[0][0]
            sign_idx = int(lon_deg / 30)
            planets[pname] = {
                "longitude": round(lon_deg, 2),
                "sign": signs[sign_idx] if sign_idx < 12 else "?",
                "degree": round(lon_deg % 30, 2),
            }
        try:
            cusps, ascmc = swe.houses(jd, lat, lon, ord("P"))
            ascendant = cusps[0]
            mc = ascmc[1]
        except:
            ascendant, mc = 0, 0
        result["astrology"] = {
            "planets": planets,
            "ascendant": round(ascendant, 2),
            "mc": round(mc, 2),
        }
    except Exception as e:
        result["astrology"] = {"error": str(e)}

    return result


def _parse_birth(s: str):
    from datetime import datetime
    for fmt in ["%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y-%m-%dT%H:%M",
                "%Y%m%d %H%M", "%Y-%m-%d %H", "%Y-%m-%d"]:
        try:
            return datetime.strptime(s, fmt)
        except:
            continue
    return None


def _gan_wuxing(g):
    return {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
            "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}.get(g, "?")


def _get_coords(loc: str):
    cities = {
        "北京": (39.9, 116.4), "上海": (31.2, 121.5), "广州": (23.1, 113.3),
        "深圳": (22.5, 114.1), "杭州": (30.3, 120.2), "成都": (30.6, 104.1),
        "武汉": (30.6, 114.3), "南京": (32.1, 118.8), "重庆": (29.6, 106.6),
        "西安": (34.3, 108.9), "呼和浩特": (40.8, 111.7), "天津": (39.1, 117.2),
    }
    return cities.get(loc, (39.9, 116.4))


if __name__ == "__main__":
    r = get_metaphysics("2005-06-09 11:50", "呼和浩特", "男")
    available = [k for k, v in r.items() if isinstance(v, dict) and "error" not in v]
    errors = [f"{k}: {v.get('error','?')}" for k, v in r.items() if isinstance(v, dict) and "error" in v]
    print(f"七术状态:")
    for a in available:
        print(f"  ✅ {a}")
    for e in errors:
        print(f"  ❌ {e}")
