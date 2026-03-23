#!/usr/bin/env python3
import json
from pathlib import Path

PAYLOAD = Path('test-output/daily-payload-v1.json')
OUT = Path('outputs/daily-report-zh-from-payload-v2.md')


def main():
    payload = json.loads(PAYLOAD.read_text(encoding='utf-8'))
    s = payload['summary']
    p1, p2 = s['priority'][:2]
    f1, f2 = s['follow'][:2]
    o1, o2, o3 = s['official_anchors'][:3]
    d1, d2 = s['deprioritized'][:2]

    text = f'''# 今日进化日报

## 先看结论
今天最值得优先看的，还是两类东西：

1. **能直接改善日常工作流的工具型项目**，代表是 **{p1['name']}（`{p1['repo']}`）**。
2. **会改变助手行为模式的能力层信号**，代表是 **{p2['name']}**。

前者更接近“拿来就能试、很可能马上有体感”的工具升级；后者更像“如果做对了，会改变整个产品行为方式”的能力方向。相比之下，`{f1['repo']}` 和 `{f2['name']}` 仍然值得跟，但暂时还不到今天就要大幅投入注意力的程度。官方项目像 `{o1['name']}`、`{o2['name']}`、`{o3['name']}`` 依然要看，不过更适合作为基线背景，而不是直接挤占今天的 adopt 位。

---

## 今天建议优先看

### 1. {p1['name']}（`{p1['repo']}`）
**一句话：** {p1['why'][0]}

**为什么值得看：**
- {p1['why'][0]}
- {p1['why'][1]}
- {p1['why'][2]}

**建议动作：** {p1['action']}

**具体链接：**
- 主项目：<{p1['links'][0]}>
- 作者相关项目：<{p1['links'][1]}>
- 生态参考：<{p1['links'][2]}>
- 生态参考：<{p1['links'][3]}>

---

### 2. {p2['name']}
**一句话：** {p2['why'][0]}

**为什么值得看：**
- {p2['why'][0]}
- {p2['why'][1]}
- {p2['why'][2]}

**建议动作：** {p2['action']}

**具体链接：**
- 技能生态：<{p2['links'][0]}>
- 生态收录：<{p2['links'][1]}>
- 生态收录：<{p2['links'][2]}>

---

## 值得继续跟进

### 3. {f1['name']}（`{f1['repo']}`）
**一句话：** {f1['why'][0]}

**为什么值得看：**
- {f1['why'][0]}
- {f1['why'][1]}

**建议动作：** {f1['action']}

**具体链接：**
- 主项目：<{f1['links'][0]}>

---

### 4. {f2['name']}
**一句话：** {f2['why'][0]}

**为什么值得看：**
- {f2['why'][0]}

**建议动作：** {f2['action']}

**具体链接：**
- 技能生态：<{f2['links'][0]}>

---

## 官方动向（基线项目）

这三类项目依然要持续盯着，因为它们定义的是生态基线，而不是今天的战术 adopt 位：

- {o1['name']}：<{o1['links'][0]}>
- {o2['name']}：<{o2['links'][0]}>
- {o3['name']}：<{o3['links'][0]}>

如果日报里把它们和实战型 workflow / tooling 候选混在一起，读起来会很乱；单独列出来会更符合阅读习惯。

---

## 今天不用急着投入

- **{d1['name']}**：{d1['reason']}
- **{d2['name']}**：{d2['reason']}

---

## 今天的阅读建议
如果时间很少，先看：
- `{p1['name']}`
- `{p2['name']}`

如果还有时间，再看：
- `{f1['name']}`

剩下的先作为背景跟踪，不需要今天全部展开。
'''
    OUT.write_text(text, encoding='utf-8')
    print(str(OUT))


if __name__ == '__main__':
    main()
