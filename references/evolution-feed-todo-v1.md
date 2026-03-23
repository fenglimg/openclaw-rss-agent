# Evolution Feed TODO v1

> 目标：把 `openclaw-rss-agent` 从“日报渲染工程”推进成“高信噪比进化刷新流”。
> 规则：每做完一项就勾选；默认先追求闭环与可解释，再追求复杂度。

## Phase 0 — 产品定义收口
- [x] 写清产品一句话定义：不是 RSS digest，而是 evolution feed
- [x] 写清双目标：`user upgrade` / `openclaw evolution`
- [x] 写清一等对象模型：repo / product / skill / workflow / capability / pattern
- [x] 写清 X 是 signal layer，不是 stable ingest
- [x] 写清反重复机制：canonicalization / event-gating / angle-gating / action-state memory / cooldown / serve_score
- [x] 写清失败模式与非目标边界
- [ ] 人工复核 spec 是否还有概念重叠、术语歧义、边界不清之处

## Phase 1 — feed-first 数据模型
- [ ] 定义 `candidate object` 统一 schema（不要再以 markdown 报告结构反推对象结构）
- [ ] 为对象增加 `target_audience = user|openclaw|both`
- [ ] 为对象增加 `recommended_action = try_now|follow|adopt_candidate|official_anchor|deep_dive|risk_watch|ignore_for_now`
- [ ] 为对象增加 `why_now`, `upgrade_value`, `signal_quality`, `actionability`, `relevance`
- [ ] 把当前 `payload` 结构重构为更偏 feed/object，而不是偏日报章节
- [ ] 明确 `stable source evidence` 与 `signal-layer evidence` 的分层字段
- [ ] 为 X、GitHub、official docs、search enrichment 定义统一 evidence lane
- [ ] 人工检查：同一对象是否能挂多条 evidence 而不丢 canonical identity

## Phase 2 — anti-repeat / recommendation memory
- [ ] 设计 recommendation memory 文件或存储结构
- [ ] 记录 `canonical_id`
- [ ] 记录 `last_seen_at`
- [ ] 记录 `last_recommended_at`
- [ ] 记录 `last_recommend_reason`
- [ ] 记录 `last_recommend_angle`
- [ ] 记录 `times_recommended_7d` / `times_recommended_30d`
- [ ] 记录 `adoption_state`
- [ ] 记录 `suppressed_until`
- [ ] 实现对象级去重（canonicalization）
- [ ] 实现事件级 gating（没有新事件则不重新上版）
- [ ] 实现视角级 gating（同一理由不能反复重推）
- [ ] 实现冷却窗口
- [ ] 实现重复惩罚 `repeat_penalty`
- [ ] 人工检查：确保“重要对象不会永远消失，但也不会天天霸榜”

## Phase 3 — ranking / serving
- [ ] 实现基础 `serve_score`
- [ ] 将 `relevance` 纳入排序
- [ ] 将 `upgrade_value` 纳入排序
- [ ] 将 `why_now` 纳入排序
- [ ] 将 `signal_quality` 纳入排序
- [ ] 将 `actionability` 纳入排序
- [ ] 将 `saturation` 纳入降权
- [ ] 将 `repeat_penalty` 纳入降权
- [ ] 增加 explore / exploit 配额
- [ ] 增加版面配额（工具/工作流线、能力/产品线、官方基线、风险观察）
- [ ] 人工检查：一次刷新结果要“有变化但不乱”

## Phase 4 — source & signal lanes
- [ ] 收紧稳定主源列表，避免 source scope 膨胀
- [ ] 把 GitHub / official docs / changelog 作为稳定主源 lane 明确化
- [ ] 保持 X 仅作 signal layer
- [ ] 为 X watchlist 定义更稳定的 mock/contract fallback 行为
- [ ] 为 X signal 增加 `repeat-convergence` 与 `weak-risk` 的显式字段
- [ ] 为 search-layer enrichment 增加“验证 / 扩展 / 发现”的角色标签
- [ ] 人工检查：任何对象都不能只靠 X 就上头条

## Phase 5 — output surfaces
- [ ] 设计真正的 refresh feed 输出，而不是只生成日报 markdown
- [ ] 让 daily digest 变成 feed 的一个视图，而不是核心数据结构
- [ ] 继续保留 digest 的四层结构：头条 / 快讯雷达 / 官方基线 / 先放后看
- [ ] 为每条推荐输出明确动作建议
- [ ] 为每条推荐输出 target_audience
- [ ] 为每条推荐输出 why_now / risk / evidence summary
- [ ] 人工检查：同一批对象在 feed 与 digest 里的呈现是否各司其职

## Phase 6 — delivery / ops
- [x] Discord 直发链路已跑通
- [x] X signal 版 `news-style-v3+x-signal` 已真实发送一次
- [ ] 把默认入口切到更贴近 evolution feed 的 runner
- [ ] 把 `x-mode auto|mock|contract|off` 的行为文档化并收口
- [ ] 给 delivery metadata 增加更明确的 ranking / anti-repeat 摘要
- [ ] 如果接 cron，明确“刷新流”和“日报”是不同触发策略
- [ ] 人工检查：delivery 输出里是否已经能看出“推荐系统”而不是“模板渲染器”

## Phase 7 — quality gate
- [ ] 建立“推荐是否重复”的人工检查清单
- [ ] 建立“是否真的对 user/openclaw 有升级价值”的人工检查清单
- [ ] 建立“是否被单一信号源绑架”的人工检查清单
- [ ] 建立“是否解释清楚 why-now”的人工检查清单
- [ ] 建立“是否给出动作建议”的人工检查清单
- [ ] 每轮 ACP 开发后，由主会话做一次质量复核再决定是否合并/发送

## ACP 协作方式
- [ ] 需要长改动或多文件联动时，优先开 ACP 会话
- [ ] ACP 完成后必须给出：改动文件、产物、验证命令、剩余缺口
- [ ] 主会话负责：读结果、看产物、做质量判断、决定是否继续/回退/发送
- [ ] 不把“ACP 跑完”直接等同于“质量达标”
- [x] 方案 A：ACP 完成后必须主动发一条 Discord 线程通知，状态为 `review-ready | blocked | failed`
- [x] 该线程通知先保持简单，只需包含：任务名、状态、测试是否通过、主要产物、是否建议主会话立即审核
- [ ] 后续再升级到 completion artifact（结构化 JSON + 通知）

## 关于 ACP 完成后能否直接在频道发消息
- [x] 可以，但不要依赖 `message(action=send)` 作为主路径
- [x] 当前稳定路径是直接 POST Discord API（机器人身份发送）
- [x] 当前仓库里这条路径已经验证有效：`scripts-v2/send_discord_report_v1.py`
- [ ] 若要让 ACP 自动发消息，应继续沿用现有 Discord HTTP 直发链，不走 provider 会误判为 poll 的路径
- [ ] 自动发前仍建议保留主会话质量复核，避免半成品直接外发
