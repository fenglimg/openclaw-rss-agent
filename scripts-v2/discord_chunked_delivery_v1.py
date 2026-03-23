#!/usr/bin/env python3
import json
import sys
from pathlib import Path

MAX_LEN = 1800


def chunk_text(text: str, max_len: int = MAX_LEN):
    text = text.strip()
    if not text:
        return []
    paragraphs = text.split('\n\n')
    chunks = []
    cur = ''
    for p in paragraphs:
        candidate = p.strip()
        if not candidate:
            continue
        if not cur:
            if len(candidate) <= max_len:
                cur = candidate
            else:
                lines = candidate.splitlines()
                sub = ''
                for line in lines:
                    line = line.rstrip()
                    if not sub:
                        if len(line) <= max_len:
                            sub = line
                        else:
                            for i in range(0, len(line), max_len):
                                chunks.append(line[i:i+max_len])
                    elif len(sub) + 1 + len(line) <= max_len:
                        sub += '\n' + line
                    else:
                        chunks.append(sub)
                        if len(line) <= max_len:
                            sub = line
                        else:
                            for i in range(0, len(line), max_len):
                                chunks.append(line[i:i+max_len])
                            sub = ''
                if sub:
                    cur = sub
        elif len(cur) + 2 + len(candidate) <= max_len:
            cur += '\n\n' + candidate
        else:
            chunks.append(cur)
            if len(candidate) <= max_len:
                cur = candidate
            else:
                lines = candidate.splitlines()
                sub = ''
                for line in lines:
                    line = line.rstrip()
                    if not sub:
                        if len(line) <= max_len:
                            sub = line
                        else:
                            for i in range(0, len(line), max_len):
                                chunks.append(line[i:i+max_len])
                    elif len(sub) + 1 + len(line) <= max_len:
                        sub += '\n' + line
                    else:
                        chunks.append(sub)
                        if len(line) <= max_len:
                            sub = line
                        else:
                            for i in range(0, len(line), max_len):
                                chunks.append(line[i:i+max_len])
                            sub = ''
                cur = sub
    if cur:
        chunks.append(cur)
    return chunks


def load_inputs(paths):
    parts = []
    for p in paths:
        path = Path(p)
        if path.exists():
            parts.append(path.read_text(encoding='utf-8').strip())
    return '\n\n'.join(x for x in parts if x)


def main(argv):
    paths = argv[1:]
    if not paths:
        print(json.dumps({'ok': False, 'error': 'no input paths'}, ensure_ascii=False))
        return 1
    text = load_inputs(paths)
    chunks = chunk_text(text)
    out = {
        'ok': True,
        'input_paths': paths,
        'chunk_count': len(chunks),
        'max_len': MAX_LEN,
        'chunks': chunks,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
