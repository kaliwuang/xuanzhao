#!/usr/bin/env python3
"""
玄照 · 模板视角数据（78个批量生成视角）
从 data/perspectives.yaml 加载；若文件缺失则回退到硬编码数据。
"""
import os
import sys

_YAML_PATH = os.path.join(os.path.dirname(__file__), "data", "perspectives.yaml")

_TEMPLATE_PERSPECTIVES_HARDCODED = {}


try:
    import yaml
    with open(_YAML_PATH, encoding="utf-8") as _f:
        TEMPLATE_PERSPECTIVES = yaml.safe_load(_f)
except (FileNotFoundError, ImportError, Exception):
    TEMPLATE_PERSPECTIVES = _TEMPLATE_PERSPECTIVES_HARDCODED


def reload_from_yaml():
    """Reload perspectives from YAML file at runtime."""
    global TEMPLATE_PERSPECTIVES
    try:
        import yaml
        with open(_YAML_PATH, encoding="utf-8") as _f:
            TEMPLATE_PERSPECTIVES = yaml.safe_load(_f)
        return True
    except Exception:
        return False