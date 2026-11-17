# -*- coding: utf-8 -*-
"""校验 notes 文档的目录锚点与跨文档跳转链接（复刻前端 slug 规则）"""
import re, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# 相对项目根解析（Windows / Mac 通用；项目根 = 本文件所在目录）
NOTES = Path(__file__).resolve().parent / "notes"
files = sorted(NOTES.glob("*.md"))

# 与 engine/index.html 完全一致的 slug 规则
PUNCT = re.compile(r'[./?%#^`{}"\'<>=!:;,\\|*+~()\[\]（）【】《》、]')
def slug(t):
    t = str(t).strip().lower()
    t = PUNCT.sub('', t)
    t = re.sub(r'\s', '-', t)
    return t

def headings(text):
    """返回 (行号, 原文本, slug) 列表，跳过代码块内的行"""
    out, in_code = [], False
    for ln, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r'^(#{1,6})\s+(.*?)\s*#*\s*$', line)
        if m:
            raw = re.sub(r'<[^>]*>', '', m.group(2))       # 去内联 HTML
            raw = re.sub(r'[*_`]', '', raw)                # 去强调标记
            out.append((ln, m.group(2), slug(raw)))
    return out

doc_heads = {f.name: headings(f.read_text(encoding='utf-8')) for f in files}
problems = []

def anchor_of(links_target):
    pass

for f in files:
    text = f.read_text(encoding='utf-8')
    in_code = False
    slugs_in_doc = [s for _, _, s in doc_heads[f.name]]
    # 重复 slug 检测（GitHub 会自动 -1 后缀，前端没有，跳转会落在第一个）
    seen = {}
    for _, _, s in doc_heads[f.name]:
        seen[s] = seen.get(s, 0) + 1
    for s, n in seen.items():
        if n > 1:
            problems.append(f"[{f.name}] 重复标题 slug ({n} 次): #{s}")

    for ln, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        # 找 markdown 链接 [text](target)
        for m in re.finditer(r'\[[^\]]*\]\(([^)\s]+)\)', line):
            t = m.group(1)
            if t.startswith(('http://', 'https://', 'mailto:')):
                continue
            if t.startswith('#'):
                # 文内锚点
                a = t[1:]
                # 链接锚点本身也可能带标点，前端点击时浏览器自动解码；按原始串比对
                if a not in slugs_in_doc:
                    problems.append(f"[{f.name}:{ln}] 文内锚点失效: {t}")
            elif t.lower().endswith('.md') or '.md#' in t.lower():
                if '#' in t:
                    fn, a = t.split('#', 1)
                    a = a.replace('%20', ' ')
                else:
                    fn, a = t, None
                target = NOTES / fn
                if not target.exists():
                    problems.append(f"[{f.name}:{ln}] 目标文件不存在: {t}")
                elif a is not None:
                    tgt_slugs = [s for _, _, s in doc_heads.get(fn, [])]
                    if a not in tgt_slugs:
                        problems.append(f"[{f.name}:{ln}] 跨文档锚点失效: {t}")

print(f"共检查 {len(files)} 份文档")
if problems:
    print(f"发现 {len(problems)} 个问题:")
    for p in problems:
        print(" -", p)
else:
    print("全部目录锚点与跨文档链接均有效 ✓")
