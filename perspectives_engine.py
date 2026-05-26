#!/usr/bin/env python3
"""
玄照 · 深度视角引擎（向后兼容包装）
此文件保留仅用于兼容性，所有功能已迁移到 xuanzhao/perspectives/ 包。
"""
from xuanzhao.perspectives import *
from xuanzhao.perspectives.base import (
    Perspective, safe_get, _GAN_WUXING, _ZHI_WUXING, _WUXING_CYCLE,
    _WUXING_CONQUER, _WUXING_COLORS, calc_wuxing_distribution,
    calc_tenshen_strength, check_dayun_phase, check_combinations,
    _fmt_bazi_data, calc_daymaster_rating, get_all_analytics,
)
from xuanzhao.perspectives.engine import DeepPerspectiveEngine
