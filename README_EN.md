# XuanZhao · 玄照

> **Chinese Metaphysical Arts for the Age of Collective Intelligence**
>
> **7 Arts × 40+ Perspectives × Cross-Validation = Next-Generation Prediction System**

[![CI](https://github.com/kaliwuang/xuanzhao/actions/workflows/ci.yml/badge.svg)](https://github.com/kaliwuang/xuanzhao/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.4.0-blue)](https://github.com/kaliwuang/xuanzhao)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](https://github.com/kaliwuang/xuanzhao/pulls)

XuanZhao is a **collective intelligence system for Chinese metaphysical arts**. Enter birth information, and the system automatically runs **Ba Zi (Four Pillars of Destiny)**, Zi Wei Dou Shu, Qi Men Dun Jia, and other classical Chinese divination arts. It then feeds the charts to **96 cross-disciplinary perspectives** — from Zhuge Liang's grand strategy to Feynman's first principles, from Jungian shadow integration to Taleb's anti-fragility — producing a synthesized multi-perspective prediction.

**No API key required for core features — fully local computation.** AI agents like Hermes Agent can load the SKILL.md and use it directly.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [The 7 Arts (七术)](#the-7-arts-七术)
- [Perspectives Library](#perspectives-library)
- [CLI Usage](#cli-usage)
- [New: 7-Arts Cross-Validation Module (bazi-reverse)](#new-7-arts-cross-validation-module-bazi-reverse)
- [Hermes Agent Integration](#hermes-agent-integration)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Roadmap](#roadmap)
- [FAQ](#faq)
- [License](#license)

---

## Quick Start

```bash
# Clone
git clone https://github.com/kaliwuang/xuanzhao.git
cd xuanzhao

# Install core dependency
pip install lunar-python

# Run analysis (fully local, no network needed)
python xuanzhao.py analyze --birth "2005-06-09 11:50" --location "Hohhot" --gender male

# Generate a demo report
python xuanzhao.py demo --output my-report.md
```

**The CLI works standalone — no Hermes Agent or API keys required.**

---

## Features

- **🔮 7 Classical Chinese Arts** — Ba Zi (Four Pillars), Zi Wei Dou Shu, Qi Men Dun Jia, Da Liu Ren, Liu Yao, Tai Yi Shen Shu, Western Astrology
- **🧠 96 Cross-Disciplinary Perspectives** — Eastern sages, Western philosophers, modern thinkers, occult traditions, each with their own mental models
- **⚡ Fully Local** — Core Ba Zi analysis runs 100% offline using `lunar-python`
- **🔄 7-Arts Cross-Validation** — Input from any one art can reconstruct the birth time and generate all 7 charts
- **🤖 AI-Ready** — Ships with a complete SKILL.md for Hermes Agent; API mode available for LLM-powered prediction
- **📊 Structured Output** — JSON export for easy integration, rich terminal output for human reading

---

## Architecture

```
┌─────────────────────────────────────┐
│           INPUT LAYER               │
│   Birth Date/Time + Location + Sex  │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      7-ARTS DIVINATION LAYER        │
│  ┌────┬────┬────┬────┬────┬────┬────┐│
│  │Bazi│ZiWei│QiMen│LiuRen│Yao│TaiYi│Ast│
│  └────┴────┴────┴────┴────┴────┴────┘│
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   MULTI-PERSPECTIVE ANALYSIS LAYER  │
│  ┌────┬────┬────┬────┬────┬────┬────┐│
│  │Zhuge│Yuan│Feyn│Jung│Laozi│Mung│...││
│  └────┴────┴────┴────┴────┴────┴────┘│
│        40+ Perspectives in Parallel   │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│          SYNTHESIS OUTPUT LAYER      │
│   Consensus + Divergence + Scores    │
└─────────────────────────────────────┘
```

### Data Flow

1. **Input** — User provides birth date/time, location, and gender
2. **Chart Calculation** — The engine computes Ba Zi pillars, then optionally Zi Wei, Qi Men, and other arts
3. **Feature Extraction** — Key patterns detected: clashes, combinations, noble stars, etc.
4. **Parallel Perspective Processing** — Each perspective reads the same chart data through its unique mental model
5. **Synthesis** — Results are aggregated into a coherent prediction with consensus and divergence markers

---

## The 7 Arts (七术)

| Art | Chinese | Description | Status |
|-----|---------|-------------|--------|
| **Ba Zi** | 八字 (Four Pillars) | Destiny analysis based on Heavenly Stems and Earthly Branches | ✅ Core |
| **Zi Wei Dou Shu** | 紫微斗数 | Purple Star Astrology — a star-based fate system | ✅ Core |
| **Qi Men Dun Jia** | 奇门遁甲 | The Strange Gate — time-space strategy divination | ✅ Core |
| **Da Liu Ren** | 大六壬 | Greatest of the Three Styles — day-based divination | 🚧 Optional |
| **Liu Yao** | 六爻 (Six Lines) | Coin oracle based on I Ching hexagram changes | 🚧 Optional |
| **Tai Yi Shen Shu** | 太乙神数 | Supreme Unity — cosmic cycle divination | 🚧 Optional |
| **Western Astrology** | 西洋占星 | Western tropical/sidereal astrology | 🚧 Optional |

---

## Perspectives Library

XuanZhao ships with **40+ perspectives** organized into 4 categories, designed to provide truly diverse, cross-disciplinary readings of any birth chart.

### Chinese Metaphysical Masters (10)

| Perspective | Framework | Core Model |
|---|---|---|
| **Zhuge Liang** | Longzhong Grand Strategy | Outthink the opposition, leverage circumstances |
| **Yuan Tian'gang** | Physiognomy + Fate Segmentation | Destiny segmented by youth/middle/old age |
| **Liu Bowen** | Heaven-Human Alignment | Historical cycles, yin-yang balance |
| **Jiang Ziya** | Timing & Patience | Wait for the right moment, late bloomer |
| **Gui Gu Zi** | Persuasion & Strategy | The art of opening/closing, psychological tactics |
| **Wang Yangming** | Unity of Knowledge & Action | Inner sage, outer king |
| **Sun Tzu** | The Art of War | Know yourself and your enemy |
| **Laozi** | Daoist Non-Action | The Dao that can be told is not the eternal Dao |
| **Zhuangzi** | Free and Easy Wandering | Usefulness of the useless |
| **Shao Yong** | Cosmic Cycles | Observation through number and principle |

### Modern Thinkers (10)

| Perspective | Framework | Core Model |
|---|---|---|
| **Feynman** | First Principles | Simplify to essence, don't fool yourself |
| **Munger** | Mental Models Lattice | Invert, always invert |
| **Taleb** | Anti-fragility | Barbell strategy, convexity |
| **Naval** | Long-Termism | Specific knowledge, leverage, ownership |
| **Steve Jobs** | Product Intuition | Reality distortion field, stay hungry |
| **Paul Graham** | Startup Methodology | Do hard things, small teams |
| **Zhang Yiming** | Information Flow | Cognitive iteration, delayed gratification |
| **Karpathy** | Technical Depth | Zero-to-one understanding |
| **Elon Musk** | First Principles Physics | Question everything |
| **Zhang Xuefeng** | Pragmatism | Information asymmetry, dimensionality reduction |

### Western Philosophers (7)

| Perspective | Framework | Core Model |
|---|---|---|
| **Socrates** | The Socratic Method | Intellectual midwifery, knowing you know nothing |
| **Nietzsche** | Will to Power | Eternal recurrence, revaluation of values |
| **Kant** | Critical Philosophy | Categorical imperative, transcendental idealism |
| **Plato** | Theory of Forms | The allegory of the cave |
| **Aristotle** | Syllogistic Logic | Four causes, golden mean |
| **Jung** | Collective Unconscious | Archetypes, shadow integration, synchronicity |
| **Stoics** | Dichotomy of Control | Negative visualization, Memento Mori |

### Western Esoteric Traditions (6)

| Perspective | Framework | Core Model |
|---|---|---|
| **Aleister Crowley** | Thelema | Do what thou wilt, ceremonial magic |
| **Nostradamus** | Quatrain Prophecy | Astrological symbolism, fuzzy precision |
| **Paracelsus** | Alchemical Medicine | The dose makes the poison, signature doctrine |
| **Hermes Trismegistus** | The Kybalion | As above, so below |
| **Shaman** | Soul Journey | Three worlds, power animals |
| **Witchcraft** | Elemental Magic | Law of threefold return, moon phases |

> **Full list:** Run `python xuanzhao.py perspectives --list` to see all available perspectives.

---

## CLI Usage

XuanZhao provides a complete command-line tool that runs fully offline:

```bash
# Core analysis (local, no network)
python xuanzhao.py analyze --birth "2005-06-09 11:50" --location "Hohhot" --gender male

# JSON format (programmatic use)
python xuanzhao.py analyze --birth "2005-06-09 11:50" --location "Hohhot" --gender male --format json

# List all perspectives
python xuanzhao.py perspectives --list

# Generate a demo report
python xuanzhao.py demo --output my-report.md
```

### analyze Command Output

- Ba Zi Four Pillars + Na Yin + Hidden Stems + Ten Gods
- Day Master element and strength
- Climate Tuning God (调候用神)
- Luck Pillars sequence (大运)
- Core Features (auto-detected: clashes, noble stars, etc.)
- Multi-perspective interpretation framework

### predict Command (Requires API Key)

```bash
python xuanzhao.py predict --birth "2005-06-09 11:50" \
  --location "Hohhot" --gender male \
  --api-key "sk-..." --model "gpt-4o"
```

---

## New: 7-Arts Cross-Validation Module (bazi-reverse/)

The `bazi-reverse/` module can **reverse-engineer birth time from Ba Zi pillars** or any of the 7 arts, then compute all 7 charts and run the full 96-perspective debate.

```bash
# Reverse from Ba Zi pillars
cd bazi-reverse
python scripts/reverse_bazi.py -y 乙酉 -m 壬午 -d 甲子 -t 庚午 --json --brief
# → Output: 2005-06-09 Hour of the Horse (午时)

# Feed into main engine for 96-perspective debate
cd ..
python xuanzhao.py analyze --birth "2005-06-09 11:50" --location "Hohhot" --gender male
```

See [bazi-reverse/README.md](bazi-reverse/README.md) for details.

---

## Hermes Agent Integration

For fully automated collective intelligence predictions, install the Hermes skill:

```bash
bash install.sh
```

Then in Hermes Agent:

```
/load xuanzhao
Predict my career direction, birth info: 2005-06-09 11:50, Hohhot, Male
```

---

## Project Structure

```
xuanzhao/
├── xuanzhao.py          # Standalone CLI engine
├── SKILL.md             # Hermes Agent main skill
├── install.sh           # One-click install
├── DEMO.md              # Live run example
├── README.md            # Chinese documentation
├── README_EN.md         # This file
├── LICENSE              # MIT
├── pyproject.toml       # Python project config
├── Makefile             # Build helpers
├── engine/              # Engine modules
│   └── SKILL.md
├── scripts/
│   └── predict.py       # LLM prediction script
├── perspectives/        # 39+ perspective SKILL.md files
├── xuanzhao/            # Python package
│   ├── cli.py
│   ├── analyzer.py
│   └── perspectives/    # Python perspective implementations
│       ├── zhuge_liang.py
│       ├── feynman.py
│       ├── jung.py
│       └── ... (40+ files)
├── bazi-reverse/        # 7-Arts cross-validation module
├── tests/               # Test suite
└── docs/
    └── architecture.md
```

---

## Dependencies

- Python 3.10+
- Node.js 18+ (optional, for TokScale)
- Termux / Linux / macOS / Windows

### Python Packages

```
lunar-python>=1.4.8    # Ba Zi chart calculation (core, required)
pyswisseph>=2.10       # Western astrology (optional)
sxtwl                  # Calendar supplement (optional)
najia                  # Liu Yao / Yi Jing (optional)
kinliuren              # Da Liu Ren (optional)
kintaiyi               # Tai Yi Shen Shu (optional)
fastapi>=0.110         # Web UI (optional)
uvicorn>=0.29          # Web server (optional)
```

---

## Roadmap

- [x] Standalone CLI engine (fully local)
- [x] 7-Arts divination basics
- [x] 40+ cross-disciplinary perspectives
- [x] 7-Arts cross-validation (bazi-reverse)
- [ ] LLM-powered fully automatic prediction
- [ ] Web visualization frontend
- [ ] Online demo
- [ ] User case library

---

## FAQ

### What makes XuanZhao different from other Ba Zi apps?

XuanZhao combines **7 traditional Chinese arts** with **96 cross-disciplinary perspectives** — from Zhuge Liang to Feynman to Jung — creating a synthesis that no single-tradition tool can match. It's a **collective intelligence system** rather than a simple chart calculator.

### Do I need an API key?

**No**, the core CLI (analyze, demo) works fully offline with no API key. The `predict` command requires an LLM API key for text generation, but all chart calculations and perspective analysis are local.

### What does "local computation" mean?

Your birth data never leaves your machine. All Ba Zi chart calculations, luck pillar computation, and perspective analysis run locally using `lunar-python`. Only the optional `predict` command sends data to an LLM API.

### How are the perspectives generated?

Each perspective is a carefully crafted mental model — a unique way of seeing and interpreting chart data. They are not random prompts. Think of them as **96 different lenses** through which the same chart is analyzed, then synthesized into a coherent output. The perspectives include Python implementations that compute scores and generate interpretations.

### Can I add my own perspective?

Yes! Perspectives are modular. Add a new Python file in `xuanzhao/perspectives/` following the template in `template_perspective.py`, or add a new SKILL.md in `perspectives/`. The system auto-discovers new perspectives.

### What is the "7-Arts Cross-Validation"?

This is the ability to input any one art's result (e.g., just Ba Zi pillars) and reconstruct the birth time, then compute all 7 arts for a comprehensive reading. This enables verification and deeper insight.

### Who is this for?

- **Practitioners** of Chinese metaphysics seeking a modern, multi-perspective tool
- **Developers** interested in AI + traditional knowledge systems
- **Researchers** in computational astrology and collective intelligence
- **Curious minds** wanting to explore their birth chart through 96+ different viewpoints

---

## License

MIT — feel free to use, modify, and distribute. See [LICENSE](LICENSE).

---

[中文版本](README.md) | [English Version](README_EN.md)
