#!/usr/bin/env python3
"""
深度视角引擎——加载所有已实现的视角
"""
from xuanzhao.perspectives.base import get_all_analytics
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

