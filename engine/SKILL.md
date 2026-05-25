---
name: xuanzhao-engine
description: 轻量级群体智能预测引擎——借鉴 MiroFish 多智能体群体智能思路，使用 Hermes 已有的 44 个人物视角 skill 作为预测智能体，从多个认知框架分析同一问题，通过交叉验证产出预测报告。无需 Docker，在任意环境可运行。触发词：预测、群体智能、swarm、多视角分析、推演、MiroFish、群体预测、综合研判。
required_skills:
  - huashu-nuwa
---

# 玄照引擎 — 轻量群体智能预测引擎

## 核心理念

MiroFish 跑数千个通用 AI 智能体在数字沙盘中交互演化。我们的版本跑 **3-7 个顶级认知框架**（费曼/芒格/Taleb/张一鸣等）在同一个问题上独立推理并交叉印证。

```
MiroFish:                玄照引擎:
  数千同类 Agent         3-7 个异质认知框架
  ↓                      ↓
  沙盘环境模拟           独立推理 + 交叉印证
  ↓                      ↓
  涌现结果               共识/分歧/置信度
  ↓                      ↓
  需要 Docker            纯 Hermes 环境
```

**更少的 Agent，更深的推理**。不是用数量模拟涌现，而是用认知多样性覆盖盲区。

## 执行流程

### Phase 0: 问题解析

用户输入预测问题后，提取：

| 要素 | 示例 |
|------|------|
| 预测对象 | "2027年AI芯片市场格局" |
| 时间范围 | "未来12个月" |
| 关键变量 | "英伟达/AMD/华为竞争，出口管制" |
| 不确定因素 | "美国大选结果、技术突破" |
| 已有信息 | 用户提供或自动补充 |

### Phase 1: 视角选择

根据问题类型自动匹配最佳视角组合：

| 问题类型 | 推荐视角（3-5个） |
|---------|----------------|
| **科技趋势** | karpathy-perspective, feynman-perspective, zhang-yiming-perspective, naval-perspective |
| **商业决策** | munger-perspective, steve-jobs-perspective, paul-graham-perspective, zhangxuefeng-perspective |
| **市场/金融** | taleb-perspective, naval-perspective, munger-perspective |
| **社会/政治** | taleb-perspective, trump-perspective, munger-perspective |
| **产品/创业** | steve-jobs-perspective, paul-graham-perspective, zhang-yiming-perspective |
| **通用预测** | feynman-perspective + munger-perspective + taleb-perspective + naval-perspective |

### Phase 2: 并行推理

使用 `delegate_task` 并行运行每个视角：

```
问题 → 分发给 3-5 个子任务
         │
   ┌─────┼─────┐
   │     │     │
 视角A  视角B  视角C  视角D  视角E
 (费曼) (芒格) (Taleb)(张一鸣)(Naval)
   │     │     │     │     │
   └─────┴──┬──┘     └──┬──┘
             ↓            ↓
        独立分析结果   独立分析结果
```

每个子任务的 prompt 模板：

```
你正在以 [人物名] 的思维方式分析以下问题：

[预测问题]
背景：[补充信息]

请从你的视角出发，给出：
1. 核心判断（一句话结论）
2. 推演过程（你的思维框架如何得出这个结论）
3. 关键假设（你的判断依赖哪些假设）
4. 风险点（什么情况下你会错）
5. 置信度（0-100%）
```

### Phase 3: 合成输出

收集所有视角的结果后，合成最终报告：

```json
{
  "prediction": {
    "summary": "综合判断...",
    "consensus": "多数视角一致认为...",
    "divergence": "视角A和视角B在X点上有分歧..."
  },
  "confidence": {
    "overall": 75,
    "breakdown": {"perspective_A": 80, "perspective_B": 70, ...}
  },
  "scenarios": [
    {"name": "基准情景", "probability": "60%", "description": "..."},
    {"name": "乐观情景", "probability": "20%", "description": "..."},
    {"name": "风险情景", "probability": "20%", "description": "..."}
  ],
  "key_signals": ["未来3个月内需要关注的事件信号1", "信号2", ...],
  "blind_spots": ["所有视角可能都忽略的..."]
}
```

### Phase 4: 反思（可选）

将合成报告返回给所有视角进行第二轮反馈，迭代收敛。

## 默认视角库

| 视角 | 思维方式 | 最适合 |
|------|---------|--------|
| feynman-perspective | 简化、从基本原理推导 | 科技/物理/复杂系统 |
| munger-perspective | 多元思维模型、逆向思考 | 商业/投资/决策 |
| taleb-perspective | 反脆弱、尾部风险、黑天鹅 | 风险/市场/不确定性 |
| naval-perspective | 长期主义、杠杆、复利 | 趋势/财富/技术 |
| steve-jobs-perspective | 产品直觉、极简、用户体验 | 产品/设计/品牌 |
| paul-graham-perspective | 创业方法论、创意价值 | 创业/初创公司 |
| zhang-yiming-perspective | 信息流、平台效应、AI | 科技/互联网/平台 |

### 中国玄学泰斗

| 视角 | 思维方式 | 最适合 |
|------|---------|--------|
| zhuge-liang-perspective | 隆中对全局推演、借势而为 | 战略规划/长期布局 |
| liu-bowen-perspective | 天人合一、微兆预警 | 趋势预测/风险预警 |
| yuan-tiangang-perspective | 骨相推命、命运分段论 | 命理分析/命运观测 |
| jiang-ziya-perspective | 等待时机、顺势天命 | 投资/职业转型时机 |
| gui-gu-zi-perspective | 捭阖之道、说服心理学 | 谈判/人际关系/商业博弈 |
| wang-yangming-perspective | 知行合一、事上练 | 个人成长/决策执行 |
| sun-tzu-perspective | 知己知彼、不战而屈人 | 商业竞争/资源博弈 |
| laozi-perspective | 无为而治、上善若水 | 管理/领导力/修身 |
| zhuangzi-perspective | 逍遥游、齐物论、无用之用 | 人生哲学/心态调整 |
| shao-yong-perspective | 元会运世、观物内省 | 易学分析/时间周期 |

### 西方哲学家

| 视角 | 思维方式 | 最适合 |
|------|---------|--------|
| socrates-perspective | 反诘法、追问直至本质 | 问题分析/逻辑验证 |
| nietzsche-perspective | 权力意志、重估价值 | 人生意义/逆境重生 |
| kant-perspective | 理性批判、道德律令 | 伦理决策/逻辑框架 |
| plato-perspective | 理型论、洞穴比喻 | 穿透表象见本质 |
| aristotle-perspective | 三段论、中庸之道 | 逻辑推理/德性判断 |
| jung-perspective | 集体无意识、阴影整合 | 心理学/梦境/人际关系 |
| stoic-perspective | 控制二分法、逆境磨炼 | 情绪管理/抗压/决策 |

### 西方神秘学

| 视角 | 思维方式 | 最适合 |
|------|---------|--------|
| crowley-perspective | 泰勒玛法则、仪式魔法 | 创造性转化/自我蜕变 |
| nostradamus-perspective | 四行诗预言、星象推演 | 象征解读/趋势外推 |
| paracelsus-perspective | 万物皆毒/剂量决定 | 风险判断/临界点分析 |
| hermes-trismegistus-perspective | 七原则如在其上 | 跨领域类比/规律发现 |
| shaman-perspective | 灵魂旅行、万物有灵 | 直觉开发/生态视角 |
| witch-perspective | 元素魔法、月相周期 | 自然节奏/周期律|

## 使用方法

```python
# 示例：预测"2027年AI芯片市场格局"
from hermes_tools import delegate_task

tasks = []
perspectives = ['karpathy-perspective', 'feynman-perspective', 
                'munger-perspective', 'zhang-yiming-perspective']

for p in perspectives:
    tasks.append({
        "goal": f"以{p}的视角分析预测问题",
        "context": f"预测问题：2027年AI芯片市场格局会如何演变？\n背景信息：英伟达当前占80%+市场，AMD MI300追赶，华为昇腾受出口管制影响...\n请输出：核心判断、推演过程、关键假设、风险点、置信度",
        "toolsets": ["skills"]
    })

results = delegate_task(goal="批量视角分析", tasks=tasks)
# 然后合成结果
```

## 局限

1. 不是真正的"涌现"——每个视角独立推理后合成，而非实时交互迭代
2. 视角数量受限于 Hermes 并发子任务上限（默认3-5个）
3. 预测质量取决于视角 skill 的质量和 prompt 设计
4. 无法模拟时间和动态演化（MiroFish 的数字沙盘能做到）
