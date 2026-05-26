"""
玄照 · FastAPI Web 辩论台 v2.0
辩论交互后端 + 前端
"""
import sys, os, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# 导入引擎
try:
    from xuanzhao import DestinyAnalyzer, PerspectiveEngine
    analyzer = DestinyAnalyzer()
    pers_engine = PerspectiveEngine()
    ENGINE_OK = True
except ImportError as e:
    print(f"⚠️ 引擎导入失败: {e}")
    ENGINE_OK = False

# 导入辩论引擎
try:
    from debate_engine import FIGURES, FACTIONS, build_monologue
    from perspectives_engine import get_all_analytics
    DEBATE_OK = True
except ImportError as e:
    FIGURES = {}
    FACTIONS = {}
    build_monologue = None
    DEBATE_OK = False
    print(f"⚠️ 辩论引擎导入失败: {e}")

# 导入深度视角
try:
    from perspectives_engine import DeepPerspectiveEngine
    deep_engine = DeepPerspectiveEngine()
    DEEP_OK = True
except ImportError:
    deep_engine = None
    DEEP_OK = False

app = FastAPI(title="玄照 · 玄学辩论台", version="2.0.0")
templates = Jinja2Templates(directory="templates")

# ==========================================
# 辩论台 HTML (moved to templates/index.html)
# ==========================================


# ==========================================
# 缓存辩论状态
# ==========================================
_debate_cache = {}

def _load_debate_data():
    """加载或缓存辩论数据"""
    if DEBATE_OK:
        return FIGURES, FACTIONS
    
    if "figures" in _debate_cache:
        return _debate_cache["figures"], _debate_cache["factions"]
    return {}, {}


@app.get("/api/debate", response_class=HTMLResponse)
async def debate_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/analytics")
async def get_analytics(
    birth: str = Query("2005-06-09 11:50"),
    location: str = Query("呼和浩特"),
    gender: str = Query("男"),
):
    try:
        destiny = analyzer.analyze(birth, location, gender)
        analytics = get_all_analytics(destiny)
        return analytics
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/debate/ask")
async def debate_ask(data: dict):
    try:
        question = data.get("question", "此人命运如何？")
        birth = data.get("birth", "2005-06-09 11:50")
        location = data.get("location", "呼和浩特")
        gender = data.get("gender", "男")
        
        global _debate_cache
        if "destiny" not in _debate_cache:
            _debate_cache["destiny"] = analyzer.analyze(birth, location, gender)
        destiny = _debate_cache["destiny"]
        
        analytics = get_all_analytics(destiny)
        _debate_cache["analytics"] = analytics
        
        if not DEBATE_OK or not FIGURES:
            return {"error": "辩论引擎未加载"}
        
        import random
        random.seed(hash(question) & 0x7FFFFFFF)
        
        # 每个阵营选2位代表
        from collections import defaultdict
        fm = defaultdict(list)
        for pid, fig in FIGURES.items():
            fm[fig["faction"]].append((pid, fig))
        
        factions_order = ["orthodox", "daoist", "prophet", "alchemy", "witchcraft", "western", "rational"]
        debaters = {}
        for fac in factions_order:
            members = fm.get(fac, [])
            random.shuffle(members)
            for pid, fig in members[:2]:
                debaters[pid] = fig
        
        # 构建第一轮发言
        round1 = []
        for pid, fig in debaters.items():
            speech = build_monologue(pid, fig, analytics)
            round1.append({
                "name": fig["name"],
                "title": fig["title"],
                "faction": fig["faction"],
                "text": speech,
                "catchphrase": fig.get("catchphrase", ""),
            })
        
        # 构建驳论：根据问题关键词选择交锋
        round2 = []
        if "冲" in question or "子午" in question:
            # 子午冲是焦点
            orthodox = [p for p in fm.get("orthodox", []) if p[0] in debaters]
            prophet = [p for p in fm.get("prophet", []) if p[0] in debaters]
            if orthodox and prophet:
                round2.append({
                    "from": orthodox[0][1]["name"],
                    "to": prophet[0][1]["name"],
                    "text": f"{orthodox[0][1]['name']}驳{prophet[0][1]['name']}：冲非必凶，拘泥于吉凶二字反而遮蔽了真机——关键在于癸水用神是否到位。{orthodox[0][1].get('catchphrase','')}",
                })
                round2.append({
                    "from": prophet[0][1]["name"],
                    "to": orthodox[0][1]["name"],
                    "text": f"{prophet[0][1]['name']}驳{orthodox[0][1]['name']}：你没有见过真正的凶象——子午冲在上应天象下应人事，历年所见无不有灾。{prophet[0][1].get('catchphrase','')}",
                })
        elif "事业" in question or "工作" in question or "职业" in question:
            western = [p for p in fm.get("western", []) if p[0] in debaters]
            rational = [p for p in fm.get("rational", []) if p[0] in debaters]
            if western and rational:
                round2.append({
                    "from": western[0][1]["name"],
                    "to": rational[0][1]["name"],
                    "text": f"{western[0][1]['name']}驳{rational[0][1]['name']}：你只看数据，但星象显示此人命带火金相战——事业方向决定了成败，不可轻率。{western[0][1].get('catchphrase','')}",
                })
                round2.append({
                    "from": rational[0][1]["name"],
                    "to": western[0][1]["name"],
                    "text": f"{rational[0][1]['name']}驳{western[0][1]['name']}：星象是意象而非证据。从职业数据看，此命甲木七杀格与技术、管理类职业高度相关。{rational[0][1].get('catchphrase','')}",
                })
        elif "感情" in question or "婚姻" in question or "恋爱" in question:
            witchcraft = [p for p in fm.get("witchcraft", []) if p[0] in debaters]
            daoist = [p for p in fm.get("daoist", []) if p[0] in debaters]
            if witchcraft and daoist:
                round2.append({
                    "from": witchcraft[0][1]["name"],
                    "to": daoist[0][1]["name"],
                    "text": f"{witchcraft[0][1]['name']}驳{daoist[0][1]['name']}：此命子午冲在夫妻宫——感情中水火不容是写进命里的。你说顺其自然，但有些冲突需要法术干预。{witchcraft[0][1].get('catchphrase','')}",
                })
                round2.append({
                    "from": daoist[0][1]["name"],
                    "to": witchcraft[0][1]["name"],
                    "text": f"{daoist[0][1]['name']}驳{witchcraft[0][1]['name']}：顺其自然不是不作为——是不强求。此命火旺而水有根，感情虽多波折但终会找到平衡。{daoist[0][1].get('catchphrase','')}",
                })
        else:
            # 通用辩论：玄学正宗 vs 炼金派
            orthodox = [p for p in fm.get("orthodox", []) if p[0] in debaters]
            alchemy = [p for p in fm.get("alchemy", []) if p[0] in debaters]
            if orthodox and alchemy:
                round2.append({
                    "from": orthodox[0][1]["name"],
                    "to": alchemy[0][1]["name"],
                    "text": f"{orthodox[0][1]['name']}驳{alchemy[0][1]['name']}：命运可解不可改——你所谓的炼金转化，不过是换个说法安慰人。{orthodox[0][1].get('catchphrase','')}",
                })
                round2.append({
                    "from": alchemy[0][1]["name"],
                    "to": orthodox[0][1]["name"],
                    "text": f"{alchemy[0][1]['name']}驳{orthodox[0][1]['name']}：铅的确能变成金——这不是安慰，这是炼金术三千年验证的事实。命运也一样。{alchemy[0][1].get('catchphrase','')}",
                })
        
        # 总结
        summary = (
            f"关于「{question}」的辩论总结：\n"
            f"七个阵营对此问题的看法集中在{'子午冲核心矛盾' if '冲' in question else '甲木七杀的格局特征'}上。"
            f"玄学正宗派主张基于格局做判断，预言派提醒风险，炼丹派认为问题本身就是转化的机会。"
            f"理性派的结论是：数据支持此命题有{'高波动率特征' if '冲' in question else '技术与领导力特质'}，"
            f"建议采纳正宗的格局判断为基础，结合各派的审慎态度——最终决策在命主手中。"
        )
        
        return {
            "round1": round1,
            "round2": round2,
            "summary": summary,
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ==========================================
# 原有 API
# ==========================================
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="frontend")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # 如果 frontend/index.html 存在，使用 result.html 模板；否则使用辩论台
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/analyze")
async def analyze(
    birth: str = Query("2005-06-09 11:50"),
    location: str = Query("呼和浩特"),
    gender: str = Query("男"),
    deep: str = Query("auto"),
):
    if not ENGINE_OK:
        return JSONResponse({"error": "引擎未加载"})
    try:
        destiny = analyzer.analyze(birth, location, gender)
        if "error" in destiny:
            return JSONResponse(destiny, status_code=400)
        if deep == "deep" and DEEP_OK:
            deep_ids = list(deep_engine._frameworks.keys())
            pers_result = pers_engine.deep_analyze(destiny, deep_ids, 0)
        elif deep == "shallow":
            shallow_ids = list(pers_engine.perspectives.keys())[:12]
            pers_result = pers_engine.analyze(destiny, shallow_ids)
        else:
            deep_ids = list(deep_engine._frameworks.keys())[:8] if DEEP_OK else None
            pers_result = pers_engine.deep_analyze(destiny, deep_ids, 3)
        bazi = destiny.get("bazi", {})
        astrology = destiny.get("astrology", {})
        planets_summary = {}
        if "planets" in astrology:
            for name, pdata in astrology["planets"].items():
                planets_summary[name] = {"sign": pdata.get("sign",""), "degree": pdata.get("degree",0)}
        result = {
            "bazi": bazi,
            "tiaohou": destiny.get("tiaohou", {}),
            "features": destiny.get("features", []),
            "astrology": {"planets": planets_summary, "ascendant": astrology.get("ascendant", 0)},
            "perspectives": {},
            "birth": birth,
            "location": location,
        }
        for pid, pdata in pers_result.items():
            entry = {
                "id": pid,
                "name": pdata.get("perspective", pdata.get("name", pid)),
                "title": pdata.get("title", ""),
            }
            if "score" in pdata:
                entry["score"] = pdata["score"]
                entry["confidence"] = pdata.get("confidence", 0)
                entry["summary"] = pdata.get("summary", "")
                entry["dimensions"] = pdata.get("dimensions", [])
                entry["key_insights"] = pdata.get("key_insights", [])
                entry["warnings"] = pdata.get("warnings", [])
                entry["advice"] = pdata.get("advice", [])
            else:
                entry["models"] = pdata.get("models", [])
                entry["prompt"] = pdata.get("prompt", "")
                entry["context"] = pdata.get("context", "")
            result["perspectives"][pid] = entry
        return result
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "engine": ENGINE_OK,
        "debate_engine": DEBATE_OK,
        "deep_engine": DEEP_OK,
    }


if __name__ == "__main__":
    print(f"🚀 玄照 v2.0 辩论台 — http://localhost:8080")
    print(f"   深度视角: {len(deep_engine.list()) if DEEP_OK else 0}")
    print(f"   辩论人物: {len(FIGURES) if DEBATE_OK else 0}")
    print(f"   启动命令: uvicorn app:app --host 0.0.0.0 --port 8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
