#!/usr/bin/env python3
"""
玄照 · XuanZhao — 玄学群体智能预测系统
独立 CLI 版本，无需 Hermes Agent

用法:
  python xuanzhao.py analyze --birth "2005-06-09 11:50" --location "呼和浩特" --gender male
  python xuanzhao.py report --birth "2005-06-09 11:50" --location "呼和浩特" --gender male
  python xuanzhao.py perspectives --list

注意: 功能已迁移至 xuanzhao/ 包。此文件为向后兼容入口点。
"""
import sys
import os

# Add the project root to sys.path so imports work from the package
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Execute cli.py from the xuanzhao package
_cli_path = os.path.join(_project_root, 'xuanzhao', 'cli.py')
if os.path.exists(_cli_path):
    # Use compile + exec to avoid name shadowing between xuanzhao.py and xuanzhao/ package
    with open(_cli_path, 'r', encoding='utf-8') as _f:
        _code = compile(_f.read(), _cli_path, 'exec')
    exec(_code, {'__name__': '__main__', '__file__': _cli_path})
else:
    print(f"ERROR: xuanzhao/cli.py not found at {_cli_path}", file=sys.stderr)
    sys.exit(1)
