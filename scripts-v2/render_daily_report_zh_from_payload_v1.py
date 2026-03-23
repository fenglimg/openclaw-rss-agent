#!/usr/bin/env python3
import json
from pathlib import Path

PAYLOAD = Path('test-output/daily-payload-v1.json')
OUT = Path('outputs/daily-report-zh-from-payload-v1.md')


def main():
    payload = json.loads(PAYLOAD.read_text(encoding='utf-8'))
    summary = payload['summary']

    lines = ['# 今日进化日报（中文 v1）', '', '## 先看结论', '']
    lines.append('### 今天最值得优先看的对象')
    for i, item in enumerate(summary['priority'], start=1):
        lines.append(f"{i}. **{item['name']}（`{item['repo']}`）**")
        lines.append(f"   - {item['why'][0]}")
        links = item.get('links', [])[:2]
        if links:
            lines.append('   - 链接：')
            for link in links:
                lines.append(f'     - <{link}>')
        lines.append('')

    lines.extend(['---', '', '## 今天建议优先看', ''])
    for idx, item in enumerate(summary['priority'], start=1):
        lines.append(f"### {idx}. {item['name']}（`{item['repo']}`）")
        lines.append(f"**一句话：** {item['why'][0]}")
        lines.append('**为什么值得看：**')
        for reason in item['why']:
            lines.append(f'- {reason}')
        lines.append(f"**建议动作：** {item['action']}")
        lines.append('**具体链接：**')
        for link in item.get('links', []):
            lines.append(f'- <{link}>')
        lines.extend(['', '---', ''])

    lines.extend(['## 值得继续跟进', ''])
    for idx, item in enumerate(summary['follow'], start=1):
        lines.append(f"### {idx}. {item['name']}（`{item['repo']}`）")
        lines.append(f"**一句话：** {item['why'][0]}")
        lines.append('**为什么值得看：**')
        for reason in item['why']:
            lines.append(f'- {reason}')
        lines.append(f"**建议动作：** {item['action']}")
        lines.append('**具体链接：**')
        for link in item.get('links', []):
            lines.append(f'- <{link}>')
        lines.extend(['', '---', ''])

    lines.extend(['## 官方动向（基线项目）', ''])
    for item in summary['official_anchors']:
        links = ' '.join([f'<{x}>' for x in item.get('links', [])])
        lines.append(f"- **{item['name']}（`{item['repo']}`）** {links}".rstrip())
    lines.extend(['', '这些项目依然要持续看，但更适合作为基线背景，而不是直接占掉今天的 practical adopt 位。', '', '---', '', '## 今天不用急着投入'])
    for item in summary['deprioritized']:
        lines.append(f"- **{item['name']}**：{item['reason']}")
    lines.append('')
    lines.append('<!-- prompt-spec: prompts/daily-report-zh-prompt-v1.txt -->')
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(str(OUT))


if __name__ == '__main__':
    main()
