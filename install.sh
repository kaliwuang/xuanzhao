#!/bin/bash
# 玄照 · 一键安装脚本

echo "🪄 玄照 · 安装开始"

# 1. Python 依赖
echo "📦 安装 Python 依赖..."
pip install lunar-python sxtwl najia kinliuren kintaiyi iztro-py pyswisseph astral cn2an 2>/dev/null
echo "✅ Python 依赖完成"

# 2. TokScale
echo "📦 安装 TokScale..."
npm install -g tokscale 2>/dev/null
echo "✅ TokScale 完成"

# 3. 创建 skill 目录
mkdir -p ~/.hermes/skills/xuanxue/xuanzhao
mkdir -p ~/.hermes/skills/ai/xuanzhao-engine
mkdir -p ~/.hermes/skills/external

# 4. 复制主 skill
cp SKILL.md ~/.hermes/skills/xuanxue/xuanzhao/
cp engine/SKILL.md ~/.hermes/skills/ai/xuanzhao-engine/
cp engine/predict.py ~/.hermes/skills/ai/xuanzhao-engine/scripts/

# 5. 复制视角 skill
for dir in perspectives/*/; do
    name=$(basename "$dir")
    mkdir -p ~/.hermes/skills/external/"$name"
    cp "$dir"SKILL.md ~/.hermes/skills/external/"$name"/
done

echo ""
echo "🎉 玄照安装完成！"
echo "在 Hermes 中输入：/load xuanzhao"
