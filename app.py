"""
玄照 · FastAPI Web 后端 v1.2.0
一键启动：uvicorn app:app --host 0.0.0.0 --port 8080
新增：深度视角引擎（12核心视角×基于命盘数据计算）
"""

import sys, os, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# 导入玄照引擎
try:
    from xuanzhao import DestinyAnalyzer, PerspectiveEngine
    analyzer = DestinyAnalyzer()
    pers_engine = PerspectiveEngine()
    ENGINE_OK = True
except ImportError as e:
    print(f"⚠️ 引擎导入失败: {e}")
    ENGINE_OK = False

# 导入深度视角引擎
try:
    from perspectives_engine import DeepPerspectiveEngine
    deep_engine = DeepPerspectiveEngine()
    DEEP_OK = True
except ImportError:
    deep_engine = None
    DEEP_OK = False

app = FastAPI(title="玄照 · XuanZhao API", version="1.2.0")

frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="frontend")


@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return "<h1>玄照 · XuanZhao</h1><p>前端文件缺失</p>"


@app.get("/api/analyze")
async def analyze(
    birth: str = Query("2005-06-09 11:50"),
    location: str = Query("呼和浩特"),
    gender: str = Query("男"),
    deep: str = Query("auto", description="deep|shallow|auto"),
):
    if not ENGINE_OK:
        return JSONResponse({"error": "引擎未加载", "available": False})

    try:
        destiny = analyzer.analyze(birth, location, gender)
        if "error" in destiny:
            return JSONResponse(destiny, status_code=400)

        # 视角分析
        if deep == "deep" and DEEP_OK:
            # 仅深度
            deep_ids = list(deep_engine._frameworks.keys())
            pers_result = pers_engine.deep_analyze(destiny, deep_ids, 0)
        elif deep == "shallow":
            # 仅浅层
            shallow_ids = list(pers_engine.perspectives.keys())[:12]
            pers_result = pers_engine.analyze(destiny, shallow_ids)
        else:
            # auto: 8深度 + 3浅层
            deep_ids = list(deep_engine._frameworks.keys())[:8] if DEEP_OK else None
            pers_result = pers_engine.deep_analyze(destiny, deep_ids, 3)

        # 构建响应
        bazi = destiny.get("bazi", {})
        astrology = destiny.get("astrology", {})
        planets_summary = {}
        if "planets" in astrology:
            for name, data in astrology["planets"].items():
                planets_summary[name] = {"sign": data.get("sign",""), "degree": data.get("degree",0)}

        result = {
            "bazi": bazi,
            "tiaohou": destiny.get("tiaohou", {}),
            "features": destiny.get("features", []),
            "astrology": {"planets": planets_summary, "ascendant": astrology.get("ascendant", 0)},
            "perspectives": {},
            "birth": birth,
            "location": location,
            "version": "1.2.0",
        }

        # 转换视角数据为前端友好格式
        for pid, pdata in pers_result.items():
            entry = {
                "id": pid,
                "name": pdata.get("perspective", pdata.get("name", pid)),
                "title": pdata.get("title", ""),
            }
            # 深度视角（有评分）
            if "score" in pdata:
                entry["score"] = pdata["score"]
                entry["confidence"] = pdata.get("confidence", 0)
                entry["summary"] = pdata.get("summary", "")
                entry["dimensions"] = pdata.get("dimensions", [])
                entry["key_insights"] = pdata.get("key_insights", [])
                entry["warnings"] = pdata.get("warnings", [])
                entry["advice"] = pdata.get("advice", [])
            else:
                # 浅层视角
                entry["models"] = pdata.get("models", [])
                entry["prompt"] = pdata.get("prompt", "")
                entry["context"] = pdata.get("context", "")
            result["perspectives"][pid] = entry

        return result

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/perspectives")
async def list_perspectives():
    result = {"deep": [], "shallow": []}
    if DEEP_OK:
        result["deep"] = deep_engine.list()
    if ENGINE_OK:
        result["shallow"] = pers_engine.list_all()
    return result


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "1.2.0",
        "engine": ENGINE_OK,
        "deep_engine": DEEP_OK,
        "deep_perspectives": len(deep_engine.list()) if DEEP_OK else 0,
        "shallow_perspectives": len(pers_engine.list_all()) if ENGINE_OK else 0,
    }


if __name__ == "__main__":
    print(f"🚀 玄照 v1.2.0 — http://localhost:8080")
    print(f"   深度视角: {len(deep_engine.list()) if DEEP_OK else 0} 个")
    print(f"   浅层视角: {len(pers_engine.list_all()) if ENGINE_OK else 0} 个")
    print(f"   引擎状态: {'✓' if ENGINE_OK else '✗'}")
    uvicorn.run(app, host="0.0.0.0", port=8080)
