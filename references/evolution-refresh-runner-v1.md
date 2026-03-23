# Evolution Refresh Runner v1

`scripts-v2/run_evolution_refresh_pipeline_v1.py` 现在是 refresh flow 的正式入口：默认使用仓库根目录相对路径，适合手动复跑，也方便后续接 cron。

## 手动运行

在仓库根目录执行：

```bash
python3 scripts-v2/run_evolution_refresh_pipeline_v1.py --mode review --tests-status passed
```

如果想复用现有 payload、避免重新构建：

```bash
python3 scripts-v2/run_evolution_refresh_pipeline_v1.py --mode review --skip-payload-build --tests-status passed
```

## Review 模式

- `--mode review`：run manifest 状态写成 `review-ready`
- 适合 ACP/人工复核前手动触发
- 如需顺手发 review-ready 线程通知，再加：

```bash
python3 scripts-v2/run_evolution_refresh_pipeline_v1.py \
  --mode review \
  --notify-review-ready \
  --tests-status passed \
  --task-name "Phase 4 unified refresh runner"
```

## Silent 模式

- `--mode silent`：核心产物照常生成，但 run manifest 状态写成 `succeeded`
- 默认不发 review-ready 通知，更适合 cron / 定时刷新

```bash
python3 scripts-v2/run_evolution_refresh_pipeline_v1.py --mode silent --skip-payload-build
```

## 常用参数

- `--item-limit 4`：控制本轮 refresh feed 上屏条数
- `--payload / --current-state / --refresh-feed / --run-manifest`：自定义输入输出位置
- `--stdout-format summary|manifest`：控制标准输出是摘要还是完整 manifest
- `--channel-id` / `--review-note-output`：控制 review-ready 通知发往哪里、结果文件落哪里

## 主要产物

- `test-output/evolution-refresh-run-v1.json`：本次运行的主 manifest，先看这里
- `test-output/evolution-refresh-feed-automation-v1.json`：结构化 refresh feed
- `outputs/evolution-refresh-feed-automation-v1.md`：可读版 refresh markdown
- `outputs/evolution-refresh-review-v1.md`：review 关注点与本轮选中/压下条目
- `test-output/evolution-recommendation-memory-current-state-v1.json`：复跑时会继续承接的当前 recommendation state
- `test-output/discord-review-note-evolution-refresh-v1.json`：如启用通知，这里记录发送结果

## Cron 提示

- 默认路径按仓库根目录解析，不依赖当前 shell 的 `cwd`
- 若 cron 只想静默产物更新，优先用 `--mode silent --skip-payload-build`
- 若希望 cron 结果更易机器读取，可配 `--stdout-format summary`
