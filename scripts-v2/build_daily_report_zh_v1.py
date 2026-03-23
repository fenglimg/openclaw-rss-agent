#!/usr/bin/env python3
from pathlib import Path

OUT = Path('outputs/daily-report-zh-v1.md')

CONTENT = '''# 今日进化日报（中文模板 v1）

## 先看结论

### 今天最值得优先看的 2 个对象
1. **Claude HUD（`jarrodwatts/claude-hud`）**
   - 这是最近更值得重看的 Claude Code 工具型项目，实用性信号明显变强。
   - 链接：
     - <https://github.com/jarrodwatts/claude-hud>
     - <https://github.com/jarrodwatts/claude-delegator>

2. **Proactive Agent**
   - 这是更接近“行为层能力”的 OpenClaw 信号，战略价值比普通 utility skill 更高。
   - 链接：
     - <https://github.com/openclaw/skills>
     - <https://github.com/VoltAgent/awesome-openclaw-skills>

---

## 今天建议优先看

### 1. Claude HUD（`jarrodwatts/claude-hud`）
**一句话：** 这是最近更像“真会改变日常工作流”的 Claude Code 工具，而不只是一个看起来有意思的小插件。  
**为什么值得看：**
- 它现在不只是单点 repo，而是开始带出作者生态和相邻项目。
- 前面的 calibration 里，它已经从普通 `follow` 提升为更接近 `adopt` 的对象。
- 如果把 X / 作者信号接进来，这类工具型对象会很容易得到额外加权，因为它符合“多作者收敛 + practical tooling”模式。  
**建议动作：** 放进优先体验名单。  
**具体链接：**
- 主项目：<https://github.com/jarrodwatts/claude-hud>
- 作者相关项目：<https://github.com/jarrodwatts/claude-delegator>
- 生态参考：<https://github.com/hesreallyhim/awesome-claude-code>
- 生态参考：<https://github.com/ccplugins/awesome-claude-code-plugins>

---

### 2. Proactive Agent
**一句话：** 这不是普通功能点，而是更接近“助手应该主动做到什么”的行为层能力。  
**为什么值得看：**
- 在 OpenClaw 这条线里，它已经从普通 `follow` 被提升到 `adopt-candidate`。
- 它的价值不只是一个 skill，而是会影响整个产品行为设计：主动执行、持续跟进、减少被动等待。
- 这类对象和 `Agent Browser`、`Summarize` 不同，但战略意义可能更高。  
**建议动作：** 继续提升优先级，后面值得单独做深一点的行为层分析。  
**具体链接：**
- 技能生态：<https://github.com/openclaw/skills>
- 生态收录：<https://github.com/VoltAgent/awesome-openclaw-skills>
- 生态收录：<https://github.com/sundial-org/awesome-openclaw-skills>

---

## 值得继续跟进

### 3. Get Shit Done（`gsd-build/get-shit-done`）
**一句话：** 这更像值得研究的方法论框架，而不是今天立刻上手 adopt 的成品能力。  
**为什么值得看：**
- 它的方法论信号很强，尤其适合给 workflow / context engineering 提供参考。
- 但当前更适合归到“framework-to-study”，而不是直接挤进 adopt 位。
- 这类项目对系统的价值更像“帮你改思路”，而不是“直接拿来就用”。  
**建议动作：** 保持 follow，后面必要时单做专题拆解。  
**具体链接：**
- 主项目：<https://github.com/gsd-build/get-shit-done>

---

### 4. Gog
**一句话：** 现在它的支持信号不少，但“到底能抽出什么可复用 lesson”还不够清楚。  
**为什么值得看：**
- 当前不是没证据，而是 lesson clarity 不够强。
- 它和 `browser`、`search`、`summarize` 这种一看就知道产品 lesson 的对象不太一样。
- 所以保留在 `follow` 是合理的，不急着升。  
**建议动作：** 继续跟，不着急加权。  
**具体链接：**
- 技能生态：<https://github.com/openclaw/skills>

---

## 官方动向（基线项目）

### 5. Claude Code / Codex / Gemini CLI
**一句话：** 这些依然是必须持续盯着的基线产品，但今天不应该直接占掉 practical adopt 的位置。  
**为什么值得看：**
- 它们定义了生态基线。
- 但日报里更适合把它们单列成“官方动向”，而不是和 workflow/tooling 候选混在一起。  
**建议动作：** 继续跟踪，作为背景基线。  
**具体链接：**
- Claude Code：<https://github.com/anthropics/claude-code>
- Codex：<https://github.com/openai/codex>
- Gemini CLI：<https://github.com/google-gemini/gemini-cli>

---

## 今天不用急着投入
- `Polymarket`
- `Weather`

**原因：** 这类对象现在更像 domain-specific signal，暂时还没抽出足够强的通用产品 lesson。后面可以留在 deep-dive，不需要挤占今天的注意力。
'''


def main():
    OUT.write_text(CONTENT, encoding='utf-8')
    print(str(OUT))


if __name__ == '__main__':
    main()
