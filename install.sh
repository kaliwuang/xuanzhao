#!/bin/bash
# 玄照 · 一键安装脚本
set -e

echo "╔═══════════════════════════════════════╗"
echo "║     玄照 · XuanZhao 安装中...        ║"
echo "╚═══════════════════════════════════════╝"

# 1. Python 核心依赖
echo ""
echo "📦 [1/4] 安装 Python 依赖..."
pip install lunar-python pyswisseph sxtwl 2>/dev/null
echo "   ✅ 核心依赖完成"

# 2. 可选依赖
echo ""
echo "📦 [2/4] 安装可选玄学库..."
pip install najia kinliuren kintaiyi iztro-py astral cn2an 2>/dev/null
echo "   ✅ 可选库完成"

# 3. TokScale（可选）
echo ""
echo "📦 [3/4] 安装 TokScale（Token用量监控）..."
npm install -g tokscale 2>/dev/null || echo "   ⚠️ npm 未安装，跳过"
echo "   ✅ TokScale 完成"

# 4. Hermes Skill
echo ""
echo "📦 [4/4] 安装 Hermes Agent Skill..."
mkdir -p ~/.hermes/skills/xuanxue/xuanzhao
mkdir -p ~/.hermes/skills/ai/xuanzhao-engine
cp SKILL.md ~/.hermes/skills/xuanxue/xuanzhao/ 2>/dev/null
cp engine/SKILL.md ~/.hermes/skills/ai/xuanzhao-engine/ 2>/dev/null
cp scripts/predict.py ~/.hermes/skills/ai/xuanzhao-engine/scripts/ 2>/dev/null

# 安装视角 skills
for dir in perspectives/*/; do
    name=$(basename "$dir")
    mkdir -p ~/.hermes/skills/external/"$name"
    cp "$dir"SKILL.md ~/.hermes/skills/external/"$name"/ 2>/dev/null
done
echo "   ✅ Skill 安装完成"

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║      🎉 玄照安装完成！               ║"
echo "╠═══════════════════════════════════════╣"
echo "║  本地 CLI：python xuanzhao.py demo    ║"
echo "║  Hermes：  /load xuanzhao              ║"
echo "║  帮助：   python xuanzhao.py --help   ║"
echo "╚═══════════════════════════════════════╝"
