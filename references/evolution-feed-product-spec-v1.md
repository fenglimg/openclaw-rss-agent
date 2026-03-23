# Evolution Feed Product Spec v1

## 1. 一句话定义

`openclaw-rss-agent` 不再是一个 RSS digest 工具，而是一个 **AI 时代的高信噪比进化刷新流（Evolution Feed）**：持续帮助 **用户自己升级** 与 **OpenClaw 自己进化**，刷出当前最值得吸收、最值得跟进、最值得警惕的能力、工具、工作流与信号。

---

## 2. 产品目标

本产品服务两个一等目标：

### 2.1 用户升级目标（Personal Upgrade Feed）
帮助用户持续发现：
- 值得直接上手的 workflow / 模板 / agent 使用法
- 值得迁移进日常工作的工具与编排
- 能明显提升效率、判断力、产出质量的 AI 应用层新用法
- 值得学习、模仿、二改的高价值项目与实践

### 2.2 OpenClaw 进化目标（OpenClaw Evolution Feed）
帮助 OpenClaw 持续发现：
- 值得吸收的能力层 / skill 形态 / product surface
- 值得跟进的 orchestration / memory / retrieval / proactive 机制
- 值得借鉴的交互、推荐、通知、行动闭环模式
- 值得警惕的噪声、伪趋势、不可复现模式与错误优化方向

---

## 3. 目标受众模型

每个推荐对象必须显式带 `target_audience`：
- `user`
- `openclaw`
- `both`

### 3.1 user
适合直接帮助用户提升：
- workflow
- productivity
- usecase
- toolchain
- cognition upgrade

### 3.2 openclaw
适合直接帮助 OpenClaw 进化：
- product capability
- skill / MCP / orchestration
- proactive / memory / planning / recommendation
- ecosystem positioning

### 3.3 both
同时具备：
- 用户能立刻受益
- OpenClaw 也值得吸收其方法或形态

---

## 4. 一等推荐对象

系统推荐的核心对象不是 tweet / post / article 本身，而是被 canonicalize 后的对象：

- `repo`
- `product`
- `skill`
- `workflow`
- `capability`
- `pattern`
- `official-anchor`

### 4.1 内容条目的角色
这些都只是信号载体，不是一等推荐对象：
- X / Twitter post
- blog post
- changelog
- release note
- Hacker News / Reddit discussion
- docs update
- GitHub issue / PR / commit / release

它们的职责是：
- 提供 why-now
- 提供 author-signal
- 提供 evidence / risk / editorial-reference
- 触发对象的重新排序与重新上版

---

## 5. 信号源分层

### 5.1 稳定主源（Stable Sources）
用于稳定召回与可复查输入：
- GitHub repos / releases / trending / topics
- 官方博客 / docs / changelog / release notes
- OpenClaw / skills / MCP / ecosystem directories
- 高质量社区站点与 curated directories

### 5.2 信号增强源（Signal Enhancers）
用于 why-now 与 editorial weighting：
- X / Twitter watchlists
- trusted author watchlists
- 短时间重复提及
- 社区热度突然抬升

### 5.3 验证 / 扩展源（Verification & Expansion）
用于二次验证与补背景：
- `search-layer`
- 官方文档/站点补查
- 多站点交叉确认

---

## 6. 推荐逻辑

每个对象的推荐分数不应由单一热度驱动，而应由多维可解释信号共同决定。

核心维度：
- `relevance`：与用户 / OpenClaw 目标的相关度
- `upgrade_value`：是否真能帮助升级
- `why_now`：今天 / 本轮为什么值得看
- `signal_quality`：信号来源是否可靠、重复收敛是否明显
- `actionability`：看完之后是否可试、可学、可接、可决策

推荐系统应该更像：
- 一个 **进化型排序系统**
而不是：
- 一个热度播报器

---

## 7. 反重复机制

目标不是“永不重复”，而是：

> 只让“带来新价值的新事件 / 新视角 / 新行动意义”的对象再次出现。

### 7.1 对象级去重（Canonicalization）
不同来源的内容要归并到同一对象。

### 7.2 事件级 gating
同一对象只有在出现新事件时，才值得再次上版：
- 新 release
- 新能力
- 新作者信号收敛
- 新风险
- 新使用案例
- judgment 升降档

### 7.3 视角级 gating
同一对象再次出现时，必须带来新的推荐理由，而不是同一理由改写重发。

### 7.4 行动状态记忆
系统需要记住对象当前所处状态：
- 未看
- 已看
- 已试
- 已采纳
- 跟进中
- 暂时搁置
- 风险观察

### 7.5 冷却窗口
普通对象不应在短时间内重复霸榜；高价值对象只有在出现新事件时才可打破冷却。

### 7.6 explore / exploit
推荐流需要同时保留：
- 高确定性的高价值对象
- 少量高潜探索项
- 少量异类但可能重要的边缘信号

### 7.7 serve_score
建议引入：

`serve_score = relevance + upgrade_value + why_now + signal_quality + actionability - saturation - repeat_penalty`

---

## 8. 时间层级

产品至少分三层：

### 8.1 Refresh Feed
像手动下滑刷新的 feed。
强调：
- now-ness
- diversity
- why-now
- 探索感

### 8.2 Daily Digest / 班报
编辑整理层。
强调：
- 头条
- 快讯雷达
- 官方基线
- 风险备注
- 先放后看

### 8.3 Queues / Memory
长期判断层。
强调：
- 是否已采纳
- 是否应再次浮起
- 是否要降档或退出视野
- 是否进入长期待办或产品路线

---

## 9. 输出动作模型

每条推荐不应只告诉用户“看什么”，还应告诉用户 / OpenClaw “现在该怎么处理它”。

推荐动作包括：
- `try_now`
- `follow`
- `adopt_candidate`
- `official_anchor`
- `deep_dive`
- `risk_watch`
- `ignore_for_now`

这让系统从“信息展示”升级为“决策辅助”。

---

## 10. X / Twitter 的角色

X / Twitter 的正确角色是：
- `author-signal`
- `repeat-convergence`
- `why-now`
- `editorial-reference`
- `weak-risk`
- `discovery expansion`

### 10.1 X 不应承担的角色
- 不做稳定主源（not stable ingest）
- 不做唯一排序器
- 不替代 judgment
- 不做个性化 home timeline 复刻

### 10.2 当前产品立场
X 是 **signal layer**，不是主稿源。
它帮助解释“为什么今天值得看”，但不直接决定“什么最该看”。

---

## 11. 失败模式

### 11.1 热度绑架
谁更吵谁上版，导致高信噪比丢失。

### 11.2 重复播报
同一对象高频重复出现，只是换说法，没有新价值。

### 11.3 单一信号源绑架
某个源（例如 X 或 GitHub trending）把系统整体带偏。

### 11.4 不可解释
用户不知道为什么会看到这个对象。

### 11.5 行动性不足
用户看完知道“有这个东西”，但不知道下一步该做什么。

### 11.6 对 OpenClaw 没有回流
推荐流看起来丰富，但没有沉淀回：
- skill
- workflow
- product capability
- roadmap signal

---

## 12. 非目标 / 明确不做

当前不做：
- 全网 firehose
- X home timeline 复刻
- 泛科技资讯站
- 单纯热点聚合
- 黑盒推荐
- 以文案润色替代推荐质量
- 用 X 取代稳定 source ingest

---

## 13. V1 最小闭环定义

V1 的目标不是“做一个完美 feed”，而是先做出：

### 13.1 基础发现闭环
- 稳定主源 ingest
- X signal layer 接入
- 可解释排序
- digest / queue 输出
- Discord delivery 闭环

### 13.2 可解释判断闭环
- 每条推荐都能回答：
  - 为什么看到它
  - 为什么是今天
  - 该怎么处理它
  - 它更偏 user 还是 openclaw

### 13.3 反重复闭环
- 同一对象不会无理由反复霸榜
- 同一对象再次上版时必须有新理由 / 新事件 / 新行动意义

---

## 14. 后续演进路线

### 阶段 A：定位与推荐规则钉死
- 完成产品 spec
- 明确对象模型 / audience / action model / anti-repeat model

### 阶段 B：feed-first 重构
- 不再以日报脚本为中心，而以 recommendation/feed pipeline 为中心
- digest 只是 feed 的一个渲染层

### 阶段 C：状态记忆层
- recommendation memory / evolution memory
- 记录对象状态、冷却、采纳、风险、重复次数

### 阶段 D：真实 X backend
- 在 watchlist + contract-first 前提下接真实 backend
- 保持 X 只是 signal layer

### 阶段 E：质量治理
- 引入质量阈值、失败模式监控、重复率监控、动作分布监控

---

## 15. 当前最重要的产品原则

> 不要因为“新”就推，也不要因为“重要”就天天推。只有“现在值得再次出现”的对象，才应该进入这一轮刷新。

这条原则应贯穿：
- source ingestion
- ranking
- digest generation
- delivery
- follow-up action
