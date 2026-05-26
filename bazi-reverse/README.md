# 七术互逆 · Bazi Reverse & Seven Arts Debate

**八字倒推 → 七术全排 → 群体辩论**

一个从八字四柱倒推出生时间，进而排全七术（八字/紫微/奇门/六爻/六壬/太乙/占星），并运行96+视角群体智能辩论的系统。

## 快速开始

### 从八字倒推出生时间

```bash
python scripts/reverse_bazi.py -y 乙酉 -m 壬午 -d 甲子 -t 庚午 --json --brief
```

输出：
```json
{"year": 2005, "month": 6, "day": 9, "hour_dz": "午", ...}
```

### 全七术辩论

配合主项目的 `xuanzhao.py` 使用：

```bash
python ../xuanzhao.py analyze --birth "2005-06-09 11:50" --location "呼和浩特" --gender male --format json
```

然后加载96视角引擎获取跨学科辩论。

## 文件结构

```
bazi-reverse/
├── README.md                    ← 本文件
├── scripts/
│   └── reverse_bazi.py          ← 八字→出生时间倒推脚本
├── debate_template.md           ← 七术辩论输出格式模板
└── reverse-algorithm.md         ← 各入口倒推算法详解
```

## 七术互逆理念

七门术数中**任意一门**都可以是入口：

```
         ┌ 八字四柱 ──────────┐
         │ 紫微斗数 ──┐       │
         │ 奇门遁甲 ──┤       │
  输入 ──┤ 六爻纳甲 ──┼→ 倒推 → 排全七术 → 96视角辩论
         │ 大六壬   ──┤   出生
         │ 太乙神数 ──┘
         └ 西洋占星 ────────
```

## 入口可行性

| 入口 | 精度 | 方式 |
|------|------|------|
| 出生日期 | ✅ 直接排七术 | 无需倒推 |
| 八字四柱 | ✅ 到天 | reverse_bazi.py |
| 西洋占星 | ⚠ 到3-5天 | 太阳+上升+月亮约束 |
| 紫微斗数 | ⚠ 到3-10天 | 命宫+紫微星约束 |
| 奇门遁甲 | ⚠ 到3-7天 | 遁局+值符约束 |

## 依赖

- Python 3.10+
- `lunar-python` — 八字历法
- `iztro-py` — 紫微斗数
- `kinqimen` — 奇门遁甲
- `kinliuren` — 大六壬
- `kintaiyi` — 太乙神数
- `najia` — 六爻纳甲
- `pyswisseph` — 西洋占星
