#!/usr/bin/env python3
"""
玄照 · 深度视角引擎包
"""
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)
from xuanzhao.perspectives.zhuge_liang import ZhugeLiang
from xuanzhao.perspectives.yuan_tiangang import YuanTiangang
from xuanzhao.perspectives.feynman import Feynman
from xuanzhao.perspectives.jung import Jung
from xuanzhao.perspectives.munger import Munger
from xuanzhao.perspectives.taleb import Taleb
from xuanzhao.perspectives.naval import Naval
from xuanzhao.perspectives.laozi import Laozi
from xuanzhao.perspectives.wang_yangming import WangYangming
from xuanzhao.perspectives.stoic import Stoic
from xuanzhao.perspectives.crowley import Crowley
from xuanzhao.perspectives.shaman import Shaman
from xuanzhao.perspectives.sun_tzu import SunTzu
from xuanzhao.perspectives.gui_gu_zi import GuiGuZi
from xuanzhao.perspectives.liu_bowen import LiuBowen
from xuanzhao.perspectives.freud import Freud
from xuanzhao.perspectives.nietzsche import Nietzsche
from xuanzhao.perspectives.buffett import Buffett
from xuanzhao.perspectives.hermes import Hermes
from xuanzhao.perspectives.zhang_yiming import ZhangYiming
from xuanzhao.perspectives.template_perspective import TemplatePerspective, _load_template_perspectives, TEMPLATE_FRAMEWORKS
from xuanzhao.perspectives.engine import DeepPerspectiveEngine

__all__ = [
    "Perspective", "ZhugeLiang", "YuanTiangang", "Feynman", "Jung",
    "Munger", "Taleb", "Naval", "Laozi", "WangYangming", "Stoic",
    "Crowley", "Shaman", "SunTzu", "GuiGuZi", "LiuBowen", "Freud",
    "Nietzsche", "Buffett", "Hermes", "ZhangYiming",
    "TemplatePerspective", "DeepPerspectiveEngine",
    "safe_get", "calc_wuxing_distribution", "calc_tenshen_strength",
    "check_dayun_phase", "check_combinations", "_fmt_bazi_data",
    "calc_daymaster_rating", "get_all_analytics",
    "_GAN_WUXING", "_ZHI_WUXING", "_WUXING_CYCLE", "_WUXING_CONQUER", "_WUXING_COLORS",
    "TEMPLATE_FRAMEWORKS", "_load_template_perspectives",
]
