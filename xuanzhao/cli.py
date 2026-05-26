#!/usr/bin/env python3
"""
玄照 · CLI 入口 — 命令行界面
"""
import argparse, json, os, sys, re, math
from datetime import datetime
from typing import Optional

from xuanzhao.analyzer import DestinyAnalyzer, BaziEngine, AstrologyEngine

# 深度视角引擎（96个核心视角基于实际命盘数据计算分析）
try:
    from perspectives_engine import DeepPerspectiveEngine
    DEEP_ENGINE = DeepPerspectiveEngine()
    DEEP_OK = True
except ImportError:
    DEEP_OK = False

VERSION = "1.3.5"


# ========================
# 视角库（内置核心视角）
# ========================
PERSPECTIVES_HARDCODED = {
    "zhuge-liang": {
        "name": "诸葛亮",
        "title": "隆中对全局推演",
        "models": [
            "全局推演法：从整体格局出发，分析各方势力、资源、时机，找出最优路径",
            "借势而为：不凭蛮力，利用对手的力量和外部环境变化达成目标",
            "以逸待劳：在不利局面下保存实力，等待对方犯错",
            "多算胜少算：决策前穷尽可能的变量，做得越多胜算越大",
        ],
        "prompt": "你以诸葛亮隆中对式的全局思维分析这个命局。看格局不看细节，找核心矛盾而非表面现象。"
    },
    "yuan-tiangang": {
        "name": "袁天罡",
        "title": "骨相推命运分段",
        "models": [
            "骨相推命法：先天结构决定命运格局，大框架从小细节可窥",
            "命运分段论：人生分段看——少年看骨（潜力）、中年看气（运势）、晚年看神（修为）",
            "大运国运联动：个人命运嵌在时代中，不能脱离时代谈个人",
        ],
        "prompt": "你以袁天罡推背图式的格局思维看这个命局。关注命运的大框架和关键转折点。"
    },
    "feynman": {
        "name": "费曼",
        "title": "简化核心机制",
        "models": [
            "第一性原理：回到最基本的物理定律，不给任何权威结论留豁免权",
            "费曼学习法：如果你不能简单地解释它，说明你没真正理解",
            "不要欺骗自己：你自己是最容易欺骗的人",
        ],
        "prompt": "你以费曼的精神分析这个命局——简化到核心机制，去除所有玄学术语包装，用最直白的话说清楚本质。"
    },
    "jung": {
        "name": "荣格",
        "title": "集体无意识与阴影",
        "models": [
            "个体化（Individuation）：成为完整的自己，而非完美的自己",
            "阴影整合：你最讨厌的别人的特质，往往是你自己的阴影投射",
            "共时性（Synchronicity）：有意义的巧合不是偶然",
        ],
        "prompt": "你以荣格分析心理学视角看这个命局。关注阴影、原型、个体化进程。"
    },
    "munger": {
        "name": "芒格",
        "title": "多元思维模型",
        "models": [
            "逆向思维：要得到X，先想想什么会阻碍X，然后避开它们",
            "心理模型网格：用100+个跨学科模型做决策，而不是只用一两个",
            "人类误判心理学：25种心理倾向如何影响判断",
        ],
        "prompt": "你以芒格的逆向思维和多元模型分析这个命局。关注避坑而非追求。"
    },
    "taleb": {
        "name": "Taleb",
        "title": "反脆弱与黑天鹅",
        "models": [
            "反脆弱：有些东西越挫越强——命局的逆境可能是隐藏的优势",
            "黑天鹅：最重大的事件往往是无法预测的",
            "凸性策略：在损失有限但收益无限的方向下注",
        ],
        "prompt": "你以Taleb的反脆弱思维分析这个命局。关注隐藏的风险和韧性。"
    },
    "naval": {
        "name": "Naval",
        "title": "长期主义与杠杆",
        "models": [
            "特定知识：无法通过培训获得的知识才是真正的护城河",
            "杠杆：代码、媒体、资本——用杠杆放大个人产出",
            "复利：选择那些随年龄增长而增值的职业和能力",
        ],
        "prompt": "你以Naval的长期主义视角分析这个命局。关注什么能力能在时间中产生复利。"
    },
    "laozi": {
        "name": "老子",
        "title": "道法自然",
        "models": [
            "无为而治：过度干预适得其反，顺应本性的发展最有效率",
            "反者道之动：物极必反——命局最弱的点可能是最大的潜力",
            "上善若水：不争之争，柔弱胜刚强",
        ],
        "prompt": "你以老子道家智慧分析这个命局。关注顺势、不争、回归本质。"
    },
    "sun-tzu": {
        "name": "孙子",
        "title": "知己知彼",
        "models": [
            "知己知彼：信息=胜利，了解自己的优势和对手的弱点",
            "不战而屈人之兵：最高明的胜利是不用打",
            "以正合以奇胜：常规手段和出其不意相结合",
        ],
        "prompt": "你以孙子兵法视角分析这个命局。关注战略位置和竞争策略。"
    },
    "stoic": {
        "name": "斯多葛",
        "title": "控制二分法",
        "models": [
            "控制二分法：有些事由你决定（判断、行动），有些不由你决定（结果、他人评价）",
            "消极想象：预演最坏的情况，就不再恐惧",
            "逆境即磨炼：真正的成长来自于如何面对困难",
        ],
        "prompt": "你以斯多葛哲学视角分析这个命局。关注可控与不可控的边界。"
    },
    "socrates": {
        "name": "苏格拉底",
        "title": "反诘法追问",
        "models": [
            "精神助产术：通过提问让别人自己发现答案",
            "反诘法：不断追问直至抵达本质",
            "无知之知：'我唯一知道的就是我一无所知'——保持质疑",
        ],
        "prompt": "你以苏格拉底的提问精神分析这个命局。不断追问'为什么'直到找到根源。"
    },
    "wang-yangming": {
        "name": "王阳明",
        "title": "知行合一",
        "models": [
            "心即理：答案在内不在外，外部知识只有在被内心验证后才算真正理解",
            "知行合一：知道却做不到=不知道",
            "事上练：在具体事务中磨炼心性",
        ],
        "prompt": "你以王阳明心学视角分析这个命局。关注认知与行动的关系。"
    },
}

# 从 data/prompt_perspectives.yaml 加载，回退到硬编码数据
try:
    import yaml
    _yaml_path = os.path.join(os.path.dirname(__file__), "..", "data", "prompt_perspectives.yaml")
    with open(_yaml_path, encoding="utf-8") as _f:
        PERSPECTIVES = yaml.safe_load(_f)
except (FileNotFoundError, ImportError, Exception):
    PERSPECTIVES = PERSPECTIVES_HARDCODED


class PerspectiveEngine:
    """视角引擎 — 加载视角框架，生成分析提示"""

    def __init__(self):
        self.perspectives = PERSPECTIVES

    def list_all(self) -> list:
        return [{"id": k, "name": v["name"], "title": v["title"]}
                for k, v in self.perspectives.items()]

    def analyze(self, destiny_data: dict, perspective_ids: list = None) -> dict:
        if not perspective_ids:
            perspective_ids = list(self.perspectives.keys())[:5]

        # 提取关键命理信息
        summary = self._destiny_summary(destiny_data)

        results = {}
        for pid in perspective_ids:
            if pid not in self.perspectives:
                continue
            p = self.perspectives[pid]
            results[pid] = {
                "perspective": p["name"],
                "title": p["title"],
                "models": p["models"],
                "prompt": p["prompt"],
                "context": summary,
            }
        return results

    def deep_analyze(self, destiny_data: dict, deep_ids: list = None, shallow_count: int = 3) -> dict:
        """深度分析：核心视角用计算引擎，其余用 prompt 模板"""
        results = {}
        if deep_ids is None:
            deep_ids = list(DEEP_ENGINE._frameworks.keys()) if DEEP_OK else []
        # 1. 深度视角
        if DEEP_OK and deep_ids:
            deep_results = DEEP_ENGINE.analyze(destiny_data, deep_ids)
            results.update(deep_results)
        # 2. 补充浅层视角
        shallow_ids = [k for k in list(self.perspectives.keys())[:shallow_count]
                      if k not in results]
        if shallow_ids:
            shallow = self.analyze(destiny_data, shallow_ids)
            results.update(shallow)
        return results

    def _destiny_summary(self, data: dict) -> str:
        parts = []
        bazi = data.get("bazi", {})
        ba = bazi.get("bazi", {})

        if ba:
            parts.append(f"八字: {ba.get('year','?')} {ba.get('month','?')} {ba.get('day','?')} {ba.get('time','?')}")

        day_master = bazi.get("day_master", {})
        if day_master:
            parts.append(f"日主: {day_master.get('gan','?')}（{day_master.get('wuxing','?')}）")

        features = data.get("features", [])
        if features:
            parts.append(f"核心特征: {'; '.join(features[:3])}")

        tiaohou = data.get("tiaohou", {})
        if tiaohou.get("yongshen"):
            parts.append(f"调候用神: {tiaohou['yongshen']}")

        dayun = bazi.get("dayun", [])
        if dayun:
            current = [d for d in dayun if d["start"] <= 2026 <= d["end"]]
            if current:
                parts.append(f"当前大运: {current[0]['ganzhi']} ({current[0]['start']}-{current[0]['end']})")

        return "\n".join(parts)


# ========================
# 报告生成模块
# ========================
class ReportGenerator:
    """生成结构化预测报告"""

    def generate(self, destiny: dict, perspectives: dict, output_format: str = "markdown") -> str:
        if output_format == "json":
            return json.dumps({"destiny": destiny, "perspectives": perspectives}, ensure_ascii=False, indent=2)

        # Markdown 报告
        lines = []
        lines.append("╔══════════════════════════════════════════╗")
        lines.append("║         玄照 · 玄学群体智能预测报告      ║")
        lines.append("╚══════════════════════════════════════════╝")
        lines.append("")

        # 基本信息
        lines.append(f"**命主信息**")
        lines.append(f"- 出生：{destiny.get('birth','?')}　{ destiny.get('location','?')}")
        lines.append(f"- 性别：{destiny.get('gender','?')}")
        lines.append("")

        # 八字
        bazi = destiny.get("bazi", {})
        ba = bazi.get("bazi", {})
        if ba:
            lines.append("**八字命盘**")
            lines.append(f"> {ba.get('year','?')}　{ba.get('month','?')}　{ba.get('day','?')}　{ba.get('time','?')}")
            dm = bazi.get("day_master", {})
            lines.append(f"> 日主：{dm.get('gan','?')}{dm.get('wuxing','?')}")
            features = destiny.get("features", [])
            for f in features:
                lines.append(f"> ⚡ {f}")
            lines.append("")

        # 调候用神
        th = destiny.get("tiaohou", {})
        if th.get("yongshen"):
            lines.append(f"**调候用神：{th['yongshen']}**")
            lines.append("")

        # 大运
        dayun = bazi.get("dayun", [])
        if dayun:
            lines.append("**大运轨迹**")
            for d in dayun:
                marker = " ← 当前" if d["start"] <= 2026 <= d["end"] else ""
                lines.append(f"| {d['ganzhi']}　({d['start']}-{d['end']}){marker}")
            lines.append("")

        # 多视角解读
        lines.append("---")
        lines.append("## 多视角解读")
        lines.append("")

        for pid, pdata in perspectives.items():
            lines.append(f"### {pdata['perspective']} · {pdata['title']}")
            lines.append("")

            # 深度视角（有score和dimensions）
            if "score" in pdata:
                lines.append(f"**综合评分：{pdata['score']}/100**　置信度：{int(pdata.get('confidence',0)*100)}%")
                lines.append("")
                
                # 独白（核心输出）
                monologue = pdata.get("monologue", "")
                if monologue:
                    for para in monologue.split("\n\n"):
                        lines.append(f"> {para.strip()}")
                        lines.append("")
                
                lines.append(f"> _{pdata.get('summary','')}_")
                lines.append("")
                
                # 维度
                for d in pdata.get("dimensions", []):
                    bar = "█" * int(d["score"] // 10) + "░" * int(10 - d["score"] // 10)
                    lines.append(f"- **{d['name']}**　{d['score']}/100　`{bar}`")
                    lines.append(f"  _{d['detail']}_")
                    lines.append("")
                # 洞察
                insights = pdata.get("key_insights", [])
                if insights:
                    lines.append("**关键洞察：**")
                    for ins in insights:
                        lines.append(f"- 🔍 {ins}")
                    lines.append("")
                # 警告
                warnings = pdata.get("warnings", [])
                if warnings:
                    lines.append("**风险预警：**")
                    for w in warnings:
                        lines.append(f"- ⚠ {w}")
                    lines.append("")
                # 建议
                advice = pdata.get("advice", [])
                if advice:
                    lines.append("**行动建议：**")
                    for a in advice:
                        lines.append(f"- 📌 {a}")
                    lines.append("")
            else:
                # 旧格式兼容
                lines.append(f"**心智模型：**")
                for model in pdata.get("models", []):
                    lines.append(f"- {model}")
                lines.append("")
                lines.append(f"**命盘数据：**")
                lines.append("```")
                lines.append(pdata.get("context", ""))
                lines.append("```")
                lines.append("")

        # 评分汇总
        score_summary = []
        for pid, pdata in perspectives.items():
            if "score" in pdata:
                score_summary.append(f"- {pdata['perspective']}: **{pdata['score']}/100**")
        if score_summary:
            lines.append("---")
            lines.append("## 综合评分汇总")
            lines.append("")
            lines.extend(score_summary)
            lines.append("")

        # 使用说明
        lines.append("---")

        return "\n".join(lines)


# ========================
# CLI 入口
# ========================
def main():
    parser = argparse.ArgumentParser(
        description=f"玄照 v{VERSION} — 玄学群体智能预测系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python xuanzhao.py analyze --birth "2005-06-09 11:50" --location "呼和浩特" --gender male
  python xuanzhao.py report --birth "2005-06-09 11:50" --location "呼和浩特" --gender male
  python xuanzhao.py perspectives --list
  python xuanzhao.py demo
        """
    )

    parser.add_argument("--version", action="version", version=f"玄照 v{VERSION}")
    sub = parser.add_subparsers(dest="command", help="子命令")

    # analyze
    p_analyze = sub.add_parser("analyze", help="命理分析")
    p_analyze.add_argument("--birth", required=True, help="出生时间 (如 2005-06-09 11:50)")
    p_analyze.add_argument("--location", default="北京", help="出生地点 (城市名)")
    p_analyze.add_argument("--gender", default="男", help="性别 (男/女)")
    p_analyze.add_argument("--format", default="markdown", choices=["markdown","json"])

    # report
    p_report = sub.add_parser("report", help="AI解读报告（无需API Key）")
    p_report.add_argument("--birth", required=True)
    p_report.add_argument("--location", default="北京")
    p_report.add_argument("--gender", default="男")
    p_report.add_argument("--deep", type=int, default=0, help="使用前N个深度视角（默认全部）")

    # predict (alias for report, 不再需要API Key)
    p_predict = sub.add_parser("predict", help="完整预测（同report，无需API Key）")
    p_predict.add_argument("--birth", required=True)
    p_predict.add_argument("--location", default="北京")
    p_predict.add_argument("--gender", default="男")
    p_predict.add_argument("--api-key", help="[已弃用] 现在无需API Key")
    p_predict.add_argument("--deep", type=int, default=0, help="使用前N个深度视角")

    # perspectives
    p_pers = sub.add_parser("perspectives", help="视角管理")
    p_pers.add_argument("--list", action="store_true", help="列出所有视角")

    # demo
    p_demo = sub.add_parser("demo", help="生成示例报告")
    p_demo.add_argument("--output", default=None, help="输出文件路径")

    # debate
    p_debate = sub.add_parser("debate", help="108玄学人物辩论")
    p_debate.add_argument("--birth", default="2005-06-09 11:50", help="出生时间")
    p_debate.add_argument("--location", default="呼和浩特", help="出生地点")
    p_debate.add_argument("--gender", default="男", help="性别")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    analyzer = DestinyAnalyzer()
    pers_engine = PerspectiveEngine()
    reporter = ReportGenerator()

    if args.command == "perspectives" and args.list:
        all_deep = DEEP_ENGINE.list() if DEEP_OK else []
        all_shallow = pers_engine.list_all()
        print(f"\n📚 玄照视角库\n")
        print(f"深度视角（96个核心——含78模板生成）：")
        for p in all_deep:
            print(f"  🔴 {p['id']:30s} {p['name']} — {p['title']}")
        print()
        print(f"浅层视角（{len(all_shallow)}个——prompt模板）：")
        for p in all_shallow:
            print(f"  ⚪ {p['id']:30s} {p['name']} — {p['title']}")
        print(f"\n总计：{len(all_deep)} 深度 + {len(all_shallow)} 浅层")
        return

    if args.command == "demo":
        birth = "2005-06-09 11:50"
        location = "呼和浩特"
        gender = "男"
        print(f"🔄 正在分析 {birth} {location}...")
        destiny = analyzer.analyze(birth, location, gender)
        if "error" in destiny:
            print(f"❌ {destiny['error']}")
            return
        print(f"✅ 命盘分析完成，运行深度视角引擎...")
        # 使用深度视角 — 不移除硬编码限制
        deep_ids = list(DEEP_ENGINE._frameworks.keys()) if DEEP_OK else None
        pers_result = pers_engine.deep_analyze(destiny, deep_ids, shallow_count=0)
        report = reporter.generate(destiny, pers_result, "markdown")
        print(report)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n✅ 已保存到 {args.output}")
        return

    if args.command == "debate":
        birth = args.birth
        location = args.location
        gender = args.gender
        print(f"🔄 正在分析 {birth} {location}...")
        destiny = analyzer.analyze(birth, location, gender)
        if "error" in destiny:
            print(f"❌ {destiny['error']}")
            return
        print(f"✅ 命盘分析完成，召集中外108位玄学人物...")
        try:
            from debate_engine import generate_debate, select_debaters
            from perspectives_engine import get_all_analytics
            analytics = get_all_analytics(destiny)
            debaters = select_debaters(per_faction=2)
            print(f"✅ 选定{len(debaters)}位辩论代表...")
            result = generate_debate(destiny, analytics)
            
            # 输出辩论
            print("\n" + "=" * 60)
            print(f"  玄学辩论会：{result['topic']}")
            print("=" * 60)
            
            # 参辩人员
            print(f"\n📋 参辩方阵（{len(result['participants'])}人）：")
            fac_groups = {}
            for p in result["participants"]:
                fac_groups.setdefault(p["faction_name"], []).append(p["name"])
            for fn, names in fac_groups.items():
                print(f"  【{fn}】{'、'.join(names)}")
            
            # 第一轮
            for r in result["rounds"]:
                print(f"\n{'─' * 50}")
                print(f"  {r['phase']}")
                print(f"{'─' * 50}")
                if "speeches" in r:
                    for s in r["speeches"]:
                        print(f"\n【{s['faction']}】{s['name']}（{s['title']}）:")
                        for para in s["text"].split("\n\n"):
                            print(f"  {para.strip()}")
                            print()
                if "exchanges" in r:
                    for e in r["exchanges"]:
                        print(f"\n⚡ {e['label']}")
                        print(f"  {e['challenger']} → {e['target']}: {e['text']}")
                        print(f"  {e['challenger']} ← {e['target']}: {e['rebuttal']}")
            
            # 综述
            print(f"\n{'═' * 50}")
            print(f"  辩论综述")
            print(f"{'═' * 50}")
            print(f"\n{result['final_summary']}")
            
        except Exception as e:
            import traceback
            print(f"❌ 辩论引擎异常: {e}")
            traceback.print_exc()
        return

    # analyze or predict
    print(f"🔄 正在分析 {args.birth} {args.location}...")
    destiny = analyzer.analyze(args.birth, args.location, args.gender)
    if "error" in destiny:
        print(f"❌ {destiny['error']}")
        return

    # 视角选择 — 默认全部，可通过 --deep 限制
    deep_count = getattr(args, 'deep', 0)
    if deep_count == 0:
        deep_count = len(DEEP_ENGINE._frameworks) if DEEP_OK else 12
    if args.command in ("report", "predict"):
        deep_count = getattr(args, 'deep', deep_count)
    
    deep_ids = list(DEEP_ENGINE._frameworks.keys())[:deep_count] if DEEP_OK else None
    pers_result = pers_engine.deep_analyze(destiny, deep_ids, shallow_count=0)

    if args.command in ("report", "predict"):
        # AI 解读模式 — 输出完整数据供AI分析
        output = {
            "destiny": destiny,
            "perspectives": pers_result,
            "summary": {
                "total_perspectives": len(pers_result),
                "avg_score": round(sum(p.get("score", 0) for p in pers_result.values()) / max(len(pers_result), 1), 1),
                "top_perspectives": sorted(
                    [{"name": p.get("perspective", k), "score": p.get("score", 0)}
                     for k, p in pers_result.items()],
                    key=lambda x: x["score"], reverse=True
                )[:5],
            }
        }
        json_output = json.dumps(output, ensure_ascii=False, indent=2, default=str)
        print(json_output)
    else:
        report = reporter.generate(destiny, pers_result, args.format)
        print(report)


if __name__ == "__main__":
    main()
