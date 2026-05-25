"""
玄照 · FastAPI Web 后端
一键启动：uvicorn app:app --host 0.0.0.0 --port 8080
"""

import sys, os, json
from pathlib import Path

# 添加项目根目录到路径
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
    print("请确保 xuanzhao.py 在上级目录")
    ENGINE_OK = False

app = FastAPI(title="玄照 · XuanZhao API", version="1.1.0")

# 挂载前端静态文件
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
):
    if not ENGINE_OK:
        return JSONResponse({"error": "引擎未加载", "available": False})

    try:
        # 1. 命理分析
        destiny = analyzer.analyze(birth, location, gender)
        if "error" in destiny:
            return JSONResponse(destiny, status_code=400)

        # 2. 视角分析
        pers_ids = list(pers_engine.perspectives.keys())[:5]
        pers_result = pers_engine.analyze(destiny, pers_ids)

        # 3. 合成
        perspectives = []
        for pid, pdata in pers_result.items():
            perspectives.append({
                "id": pid,
                "name": pdata["perspective"],
                "title": pdata["title"],
                "models": pdata["models"],
                "insight": pdata.get("prompt", ""),
            })

        # 4. 西洋占星（如果可用）
        astrology = destiny.get("astrology", {})
        planets_summary = {}
        if "planets" in astrology:
            for name, data in astrology["planets"].items():
                planets_summary[name] = {"sign": data.get("sign",""), "degree": data.get("degree",0)}

        result = {
            "bazi": destiny.get("bazi", {}),
            "tiaohou": destiny.get("tiaohou", {}),
            "features": destiny.get("features", []),
            "astrology": {"planets": planets_summary, "ascendant": astrology.get("ascendant", 0)},
            "perspectives": perspectives,
            "birth": birth,
            "location": location,
        }
        return result

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/perspectives")
async def list_perspectives():
    if not ENGINE_OK:
        return {"perspectives": []}
    return {"perspectives": pers_engine.list_all()}

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "engine": ENGINE_OK,
        "version": "1.1.0",
    }

if __name__ == "__main__":
    print("🪄 玄照 · Web 服务启动中...")
    print(f"   前端: http://localhost:8080")
    print(f"   API:  http://localhost:8080/api/analyze?birth=2005-06-09 11:50&location=呼和浩特&gender=男")
    uvicorn.run(app, host="0.0.0.0", port=8080)
