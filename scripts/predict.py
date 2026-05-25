#!/usr/bin/env python3
"""
Swarm Predictor — 轻量群体智能预测引擎
自动选择视角 → 并行推理 → 合成输出

用法:
  python scripts/predict.py "预测问题" --context "背景信息" --perspectives auto
  python scripts/predict.py "2027年AI芯片格局" --context "英伟达80%市场..." --perspectives karpathy,munger,taleb
"""

import json, sys, os, argparse
from datetime import datetime

PERSPECTIVE_LIB = {
    "karpathy": {"name": "karpathy-perspective", "desc": "技术深度、系统架构、AI"},
    "feynman": {"name": "feynman-perspective", "desc": "简化、从基本原理推导"},
    "munger": {"name": "munger-perspective", "desc": "多元思维模型、逆向思考"},
    "taleb": {"name": "taleb-perspective", "desc": "反脆弱、尾部风险、黑天鹅"},
    "naval": {"name": "naval-perspective", "desc": "长期主义、杠杆、复利"},
    "stevejobs": {"name": "steve-jobs-perspective", "desc": "产品直觉、极简、用户体验"},
    "paulg": {"name": "paul-graham-perspective", "desc": "创业方法论、创意价值"},
    "zhangyiming": {"name": "zhang-yiming-perspective", "desc": "信息流、平台效应、AI"},
    "zhangxuefeng": {"name": "zhangxuefeng-perspective", "desc": "实用主义、信息差"},
    "trump": {"name": "trump-perspective", "desc": "媒体博弈、谈判、品牌"},
}

QUESTION_TYPE_MAP = {
    "科技": ["karpathy", "feynman", "zhangyiming", "naval"],
    "商业": ["munger", "stevejobs", "paulg", "zhangxuefeng"],
    "金融": ["taleb", "naval", "munger"],
    "社会": ["taleb", "trump", "munger"],
    "产品": ["stevejobs", "paulg", "zhangyiming", "feynman"],
}

def detect_question_type(question: str) -> str:
    """根据问题关键词检测类型"""
    keywords = {
        "科技": ["AI","芯片","技术","算法","软件","硬件","数据","模型","算力"],
        "商业": ["市场","竞争","上市","投资","创业","营收","利润","融资"],
        "金融": ["股市","经济","通胀","利率","汇率","房价","币价","基金"],
        "社会": ["政治","政策","选举","战争","外交","人口","教育"],
        "产品": ["产品","设计","用户","体验","APP","平台","内容"],
    }
    scores = {}
    for qtype, words in keywords.items():
        scores[qtype] = sum(1 for w in words if w in question)
    if not any(scores.values()):
        return "通用"
    return max(scores, key=scores.get)

def select_perspectives(question: str, manual: str = None):
    """选择视角组合"""
    if manual:
        names = [p.strip() for p in manual.split(",")]
        return [PERSPECTIVE_LIB[n] for n in names if n in PERSPECTIVE_LIB]
    
    qtype = detect_question_type(question)
    keys = QUESTION_TYPE_MAP.get(qtype, ["feynman", "munger", "taleb", "naval"])
    return [PERSPECTIVE_LIB[k] for k in keys]

def format_prompt(question: str, context: str, perspective: dict) -> str:
    return f"""你正在以 **{perspective['desc']}** 的思维方式分析以下预测问题。

【预测问题】
{question}

【背景信息】
{context}

请严格以该视角的思维框架出发，输出：

## 核心判断
一句话结论

## 推演过程
你的思维框架如何得出这个结论（200字内）

## 关键假设
你的判断依赖哪些假设条件

## 风险点
什么情况下你会判断错误

## 置信度
0-100%，并说明理由"""

def generate_report(results: list, perspectives: list) -> dict:
    """合成多视角结果为最终报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 提取共识和分歧（基于置信度加权）
    confidences = []
    judgments = []
    for r in results:
        confidences.append(r.get("confidence", 50))
        judgments.append(r.get("judgment", ""))
    
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    
    return {
        "meta": {
            "engine": "Swarm Predictor v1.0",
            "timestamp": now,
            "num_perspectives": len(perspectives),
            "perspectives_used": [p["desc"] for p in perspectives],
        },
        "report": {
            "summary": f"综合{len(perspectives)}个视角，平均置信度{avg_conf:.0f}%",
            "consensus": "多数视角一致认为...（待合成）",
            "divergence": "不同视角的分歧点在于...（待合成）",
        },
        "scenarios": [
            {"name": "基准情景", "probability": "60%", "description": "..."},
            {"name": "乐观情景", "probability": "25%", "description": "..."},  
            {"name": "风险情景", "probability": "15%", "description": "..."}
        ],
        "individual_results": results,
        "signals": ["待补充"],
        "blind_spots": ["待补充"]
    }

def main():
    parser = argparse.ArgumentParser(description="Swarm Predictor")
    parser.add_argument("question", help="预测问题")
    parser.add_argument("--context", default="", help="背景信息")
    parser.add_argument("--perspectives", default="auto", 
                       help="视角列表（逗号分隔）或 auto")
    parser.add_argument("--output", default=None, help="输出JSON路径")
    
    args = parser.parse_args()
    
    # Step 1: 选择视角
    if args.perspectives == "auto":
        selected = select_perspectives(args.question)
    else:
        selected = select_perspectives(args.question, args.perspectives)
    
    print(f"🎯 预测问题: {args.question}")
    print(f"🧠 选定视角 ({len(selected)}个):")
    for s in selected:
        print(f"   - {s['name']} ({s['desc']})")
    
    # Step 2-4: 这里会在 Hermes 中通过 delegate_task 实际执行
    # 脚本输出 JSON 供下游处理
    report = {
        "question": args.question,
        "context": args.context,
        "perspectives": selected,
        "status": "ready_for_execution",
        "instructions": "请在 Hermes 中使用 delegate_task 并行运行各视角分析"
    }
    
    output = json.dumps(report, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\n✅ 已写入 {args.output}")
    else:
        print(f"\n📋 执行计划:")
        print(output)
    
    return report

if __name__ == "__main__":
    main()
