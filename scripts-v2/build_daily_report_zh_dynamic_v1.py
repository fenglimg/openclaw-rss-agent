#!/usr/bin/env python3
from pathlib import Path

APPLIED = Path('outputs/applied-ai-evolution-brief-v5.md')
OPENCLAW = Path('outputs/openclaw-evolution-brief-v15.md')
OUT = Path('outputs/daily-report-zh-dynamic-v1.md')


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8').strip() if path.exists() else ''


def main():
    applied = read_text(APPLIED)
    openclaw = read_text(OPENCLAW)

    content = f'''# 今日进化日报（中文动态模板 v1）

## 先看结论

### 今天最值得优先看的对象
1. **Claude HUD（`jarrodwatts/claude-hud`）**
   - 当前在 applied 线中已经被提升为更接近 adopt 的 practical tooling candidate。
   - 链接：<https://github.com/jarrodwatts/claude-hud>

2. **Proactive Agent**
   - 当前在 openclaw 线中已经被提升为 adopt-candidate，更像行为层能力而不是普通 utility skill。
   - 链接：<https://github.com/openclaw/skills>

---

## 今天建议优先看

### 1. Claude HUD（`jarrodwatts/claude-hud`）
**一句话：** 它现在更像“会改变日常工作流”的工具，而不只是一个有趣项目。  
**为什么值得看：**
- applied 输出已经把它放进更强的 adopt 位置。
- 它符合工具型 surface + 作者生态 + practical utility 这条已经被验证过的升级路径。  
**建议动作：** 放进优先体验名单。  
**具体链接：**
- <https://github.com/jarrodwatts/claude-hud>
- <https://github.com/jarrodwatts/claude-delegator>

---

### 2. Proactive Agent
**一句话：** 它代表的是“助手应该更主动”的能力方向，这一层比普通技能点更重要。  
**为什么值得看：**
- openclaw 输出已经把它提升到 adopt-candidate。
- 这类能力更接近产品行为设计，不只是单个工具功能。  
**建议动作：** 提升优先级，后续值得单独分析。  
**具体链接：**
- <https://github.com/openclaw/skills>
- <https://github.com/VoltAgent/awesome-openclaw-skills>

---

## 值得继续跟进

### 3. Get Shit Done（`gsd-build/get-shit-done`）
**一句话：** 值得研究，但更适合当方法论框架看，而不是今天直接 adopt。  
**为什么值得看：**
- 它在 applied 线里仍然更像 framework-to-study。
- 价值主要在方法论，不在立刻上手。  
**建议动作：** 保持 follow。  
**具体链接：**
- <https://github.com/gsd-build/get-shit-done>

---

### 4. Gog
**一句话：** 支持信号不少，但可复用 lesson 还不够清楚。  
**为什么值得看：**
- 它当前继续留在 follow，不是因为没证据，而是 because lesson clarity 不够强。  
**建议动作：** 继续跟，不急着加权。  
**具体链接：**
- <https://github.com/openclaw/skills>

---

## 官方动向（基线项目）
- <https://github.com/anthropics/claude-code>
- <https://github.com/openai/codex>
- <https://github.com/google-gemini/gemini-cli>

这些项目依然要持续看，但更适合作为基线背景，而不是直接占掉今天的 practical adopt 位。

---

## 附：当前动态来源快照

### Applied brief source

```md
{applied}
```

### OpenClaw brief source

```md
{openclaw}
```
'''
    OUT.write_text(content, encoding='utf-8')
    print(str(OUT))


if __name__ == '__main__':
    main()
