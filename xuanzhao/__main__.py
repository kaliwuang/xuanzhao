#!/usr/bin/env python3
"""
玄照 · __main__ — 支持 python -m xuanzhao 运行
"""
import sys
import os

# Ensure the project root is in sys.path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from xuanzhao.cli import main
main()
