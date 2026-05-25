"""
玄照 · FastAPI Web 辩论台 v2.0
辩论交互后端 + 前端
"""
import sys, os, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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

# ==========================================
# 辩论台 HTML
# ==========================================
DEBATE_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>玄照 · 玄学辩论台</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'PingFang SC','Microsoft YaHei',sans-serif}
body{background:#0a0a0f;color:#c0c0cc;min-height:100vh;display:flex;flex-direction:column}
.header{background:linear-gradient(135deg,#1a1a2e,#16213e);padding:16px 20px;border-bottom:1px solid rgba(255,255,255,.08)}
.header h1{font-size:18px;color:#e8e8f0;letter-spacing:2px;font-weight:400}
.header span{color:#7c7c8a;font-size:12px;margin-left:12px}
.bazi-bar{background:rgba(20,20,40,.8);padding:10px 16px;display:flex;flex-wrap:wrap;gap:6px;font-size:13px;border-bottom:1px solid rgba(255,255,255,.05)}
.bazi-bar .tag{background:rgba(100,100,200,.15);border:1px solid rgba(100,100,200,.25);padding:2px 10px;border-radius:12px;color:#9090c0;font-size:11px}
.bazi-bar .tag.highlight{background:rgba(200,150,50,.15);border-color:rgba(200,150,50,.3);color:#c0a050}
.debate-stage{flex:1;overflow-y:auto;padding:12px 16px;scroll-behavior:smooth}
.message{margin-bottom:14px;animation:fadeIn .3s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.message .header-line{display:flex;align-items:center;gap:8px;margin-bottom:4px}
.message .badge{font-size:10px;padding:1px 8px;border-radius:8px;font-weight:500}
.message .name{font-size:13px;color:#d0d0e0;font-weight:500}
.message .title{font-size:11px;color:#707080}
.message .content{font-size:13px;line-height:1.6;color:#c0c0cc;padding:8px 12px;border-radius:8px;background:rgba(255,255,255,.04);margin-left:0;border-left:2px solid rgba(100,100,200,.2)}
.message .content .quote{color:#808090;font-style:italic;margin-top:6px;font-size:12px}

.faction-orthodox .badge{background:rgba(60,120,200,.3);color:#80b0e0}
.faction-orthodox .content{border-left-color:#3c78c8}
.faction-daoist .badge{background:rgba(60,180,120,.3);color:#80d0a0}
.faction-daoist .content{border-left-color:#3cb478}
.faction-prophet .badge{background:rgba(200,60,60,.3);color:#e08080}
.faction-prophet .content{border-left-color:#c83c3c}
.faction-alchemy .badge{background:rgba(200,150,50,.3);color:#e0b050}
.faction-alchemy .content{border-left-color:#c89632}
.faction-witchcraft .badge{background:rgba(150,60,200,.3);color:#b080d0}
.faction-witchcraft .content{border-left-color:#963cc8}
.faction-western .badge{background:rgba(60,160,200,.3);color:#70c0e0}
.faction-western .content{border-left-color:#3ca0c8}
.faction-rational .badge{background:rgba(140,140,160,.3);color:#a0a0b0}
.faction-rational .content{border-left-color:#8c8ca0}

.system-msg{text-align:center;color:#606070;font-size:12px;margin:16px 0;letter-spacing:1px}
.rebuttal{background:rgba(200,150,50,.06);border-radius:8px;padding:10px 14px;margin:10px 0 14px 24px;border:1px solid rgba(200,150,50,.12)}
.rebuttal .re-label{font-size:11px;color:#c0a050;margin-bottom:6px}
.rebuttal .re-content{font-size:12px;line-height:1.5;color:#a0a0b0}
.input-bar{background:#12121a;border-top:1px solid rgba(255,255,255,.06);padding:12px 16px;padding-bottom:calc(12px + env(safe-area-inset-bottom));display:flex;gap:8px}
.input-bar input{flex:1;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:20px;padding:10px 16px;color:#ccc;font-size:14px;outline:none}
.input-bar input:focus{border-color:rgba(80,80,200,.4)}
.input-bar button{background:rgba(80,80,200,.3);border:1px solid rgba(80,80,200,.3);border-radius:20px;padding:10px 20px;color:#a0a0e0;font-size:14px;cursor:pointer;white-space:nowrap}
.input-bar button:hover{background:rgba(80,80,200,.4)}
.input-bar button:disabled{opacity:.4;cursor:not-allowed}
.typing{color:#606070;font-size:12px;margin:8px 0 8px 24px;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:.4}50%{opacity:1}}
</style>
</head>
<body>

<div class="header">
  <h1>玄照 · 玄学辩论台 <span>108位人物 × 7大阵营</span></h1>
</div>

<div class="bazi-bar" id="baziBar">
  <span>加载命盘...</span>
</div>

<div class="debate-stage" id="debateStage">
  <div class="system-msg">欢迎来到玄学辩论台——输入你的问题，108位玄学人物当场辩论</div>
</div>

<div class="input-bar">
  <input type="text" id="questionInput" placeholder="输入问题，如：此人适合做什么？" onkeydown="if(event.key==='Enter')askQuestion()">
  <button id="askBtn" onclick="askQuestion()">发问</button>
</div>

<script>
let currentDestiny = null;
let currentAnalytics = null;
let debateHistory = [];
let isLoading = false;

// 阵营颜色映射
const FACTION_META = {
  "orthodox": {"name": "玄学正宗", "color": "#3c78c8"},
  "daoist": {"name": "道家自然", "color": "#3cb478"},
  "prophet": {"name": "预言警示", "color": "#c83c3c"},
  "alchemy": {"name": "炼金转化", "color": "#c89632"},
  "witchcraft": {"name": "巫术萨满", "color": "#963cc8"},
  "western": {"name": "西方神秘", "color": "#3ca0c8"},
  "rational": {"name": "理性研究", "color": "#8c8ca0"},
};

async function init() {
  // 加载命盘
  try {
    const r = await fetch("/api/analyze?deep=shallow");
    const data = await r.json();
    currentDestiny = data;
    
    // 更新八字信息栏
    const ba = data.bazi?.bazi || {};
    const dm = data.bazi?.day_master || {};
    const features = data.features || [];
    const bar = document.getElementById("baziBar");
    const baziStr = [ba.year, ba.month, ba.day, ba.time].filter(Boolean).join(" ");
    let html = `<span>${baziStr}</span>`;
    if (dm.gan) html += `<span class="tag highlight">日主${dm.gan}${dm.wuxing}</span>`;
    features.forEach(f => {
      const short = f.length > 16 ? f.slice(0, 16) + "…" : f;
      html += `<span class="tag">${short}</span>`;
    });
    bar.innerHTML = html;
    
    // 加载辩论引擎
    await loadAnalytics();
  } catch(e) {
    document.getElementById("baziBar").innerHTML = `<span style="color:#e08080">❌ 命盘加载失败</span>`;
  }
}

async function loadAnalytics() {
  const r = await fetch("/api/analytics");
  const d = await r.json();
  currentAnalytics = d;
}

async function askQuestion() {
  if (isLoading) return;
  const input = document.getElementById("questionInput");
  const question = input.value.trim();
  if (!question) return;
  
  isLoading = true;
  document.getElementById("askBtn").disabled = true;
  
  // 显示用户问题
  addSystemMsg("你问：" + question);
  
  // 清空输入
  input.value = "";
  
  try {
    const r = await fetch("/api/debate/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: question})
    });
    const data = await r.json();
    
    // 显示第一轮：各阵营立论
    addSystemMsg("── 各派立论 ──");
    if (data.round1) {
      for (const speech of data.round1) {
        addMessage(speech.faction, speech.name, speech.title, speech.text, speech.catchphrase);
        await sleep(200);
      }
    }
    
    // 显示驳论
    if (data.round2 && data.round2.length > 0) {
      addSystemMsg("── 观点交锋 ──");
      for (const ex of data.round2) {
        addRebuttal(ex.from, ex.to, ex.text);
        await sleep(150);
      }
    }
    
    // 显示总结
    if (data.summary) {
      addSystemMsg("── 小结 ──");
      addSummary(data.summary);
    }
    
  } catch(e) {
    addSystemMsg("❌ 辩论出错: " + e.message);
  }
  
  isLoading = false;
  document.getElementById("askBtn").disabled = false;
  
  // 滚动到底部
  const stage = document.getElementById("debateStage");
  stage.scrollTop = stage.scrollHeight;
}

function addMessage(faction, name, title, text, catchphrase) {
  const stage = document.getElementById("debateStage");
  const div = document.createElement("div");
  div.className = "message faction-" + faction;
  
  const facName = FACTION_META[faction]?.name || faction;
  const color = FACTION_META[faction]?.color || "#888";
  
  div.innerHTML = \`
    <div class="header-line">
      <span class="badge" style="background:\${color}33;color:\${color}">\${facName}</span>
      <span class="name">\${name}</span>
      <span class="title">\${title}</span>
    </div>
    <div class="content">
      \${text.replace(/\\n/g, "<br>")}
      \${catchphrase ? '<div class="quote">⚡ ' + catchphrase + '</div>' : ''}
    </div>
  \`;
  stage.appendChild(div);
}

function addRebuttal(from, to, text) {
  const stage = document.getElementById("debateStage");
  const div = document.createElement("div");
  div.className = "rebuttal";
  div.innerHTML = \`
    <div class="re-label">⚡ \${from} → \${to}</div>
    <div class="re-content">\${text.replace(/\\n/g, "<br>")}</div>
  \`;
  stage.appendChild(div);
}

function addSystemMsg(text) {
  const stage = document.getElementById("debateStage");
  const div = document.createElement("div");
  div.className = "system-msg";
  div.textContent = text;
  stage.appendChild(div);
}

function addSummary(text) {
  const stage = document.getElementById("debateStage");
  const div = document.createElement("div");
  div.style.cssText = "background:rgba(80,80,160,.1);border:1px solid rgba(80,80,160,.2);border-radius:8px;padding:12px 16px;margin:12px 0;font-size:12px;line-height:1.6;color:#b0b0c0";
  div.innerHTML = text.replace(/\\n/g, "<br>");
  stage.appendChild(div);
}

function sleep(ms) {return new Promise(r => setTimeout(r, ms))}

init();
</script>
</body>
</html>"""


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
async def debate_page():
    return DEBATE_HTML


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
async def root():
    # 重定向到辩论台
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return DEBATE_HTML


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
