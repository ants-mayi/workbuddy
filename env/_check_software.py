# -*- coding: utf-8 -*-
"""
软件信息覆盖检查 —— 以 config.py 两份 PROFILE 的 software 清单为事实源，
核对 notes/ 各文档对每项软件的覆盖情况，输出覆盖矩阵 + 缺口清单。

用法:
    python3 _check_software.py            # 检查全部（MAC + WIN）
    python3 _check_software.py mac        # 只检查本机 Mac 清单
    python3 _check_software.py win        # 只检查 Windows 清单

判定规则（对"已安装"软件要求更严）:
    - 01 版本与路径速查: 必须提及（版本总表）
    - 05 一页纸速查卡:  建议提及
    - 06 跨平台命令速查: 必须提及（命令手册）
    - 04 三层验证法:     建议提及（有验证意义的软件）
退出码: 有"必须"级缺口时为 1，方便挂到 CI / 提交前检查。
"""
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import config  # noqa: E402

# 每项软件名 → 文档检索关键词（正则，不区分大小写）。
# 新增软件时在这里加一行映射即可纳入检查。
KEYWORDS = {
    "JDK 17":            r"JDK|Java",
    "Maven 3.9":         r"Maven",
    "Gradle":            r"Gradle",
    "Node.js 22":        r"Node\.?js|\bNode \d|node -v",
    "npm 10":            r"npm",
    "Git":               r"\bGit\b",
    "Go":                r"\bGo\b|Golang|go version|go1\.",
    "Conda":             r"Conda|conda",
    "Conda (D 盘)":      r"Conda|conda",
    "Python (AI 环境)":  r"Python",
    "PyTorch":           r"PyTorch|torch",
    "Transformers":      r"Transformers",
    "Flask":             r"Flask",
    "Ollama":            r"Ollama",
    "Homebrew":          r"Homebrew|\bbrew\b",
    "ffmpeg":            r"ffmpeg",
    "VSCode":            r"VSCode|Visual Studio Code|\bcode\b.*扩展|code 命令",
    "Tailscale":         r"Tailscale",
    "Deno":              r"Deno",
    "Xcode CLT":         r"Xcode",
    "Docker":            r"Docker",
    "DBeaver 25.1":      r"DBeaver",
    "Postman 12":        r"Postman",
    "IDEA Ultimate":     r"IDEA",
    "IntelliJ IDEA":     r"IDEA|IntelliJ",
    "Postman":           r"Postman",
    "KuliCloud":         r"KuliCloud|kuli云|7892",
    "UU远程 GameViewer": r"UU远程|UURemote|GameViewer",
    "千问办公 QwenWork": r"千问办公|QwenWork|qwenwork",
    "千问 Qianwen":      r"千问(?!办公)|Qianwen",
    "豆包":              r"豆包|Doubao",
    "WorkBuddy":         r"WorkBuddy",
    "Trae CN":           r"TRAE|Trae CN",
    "wget":              r"\bwget\b",
}

# 软件形态：cli = 有常用命令行（06 必须）；gui/lib = 桌面应用或库（06 降为建议）。
# 新增软件若不是 CLI 工具，在这里标注形态。
SOFT_KIND = {
    "Flask": "lib", "PyTorch": "lib", "Transformers": "lib",
    "DBeaver 25.1": "gui", "Postman 12": "gui", "IDEA Ultimate": "gui",
    "Postman": "gui", "IntelliJ IDEA": "gui", "KuliCloud": "gui",
    "UU远程 GameViewer": "gui",
    "千问办公 QwenWork": "gui", "千问 Qianwen": "gui",
    "豆包": "gui", "WorkBuddy": "gui", "Trae CN": "gui",
}

# 各文档的"覆盖要求"：must = 缺了算失败；should = 缺了仅提示
DOC_RULES = {
    "01": {"must": True,  "desc": "版本与路径速查（版本总表）"},
    "04": {"must": False, "desc": "三层验证法（验证方法）"},
    "05": {"must": False, "desc": "一页纸速查卡"},
    "06": {"must": True,  "desc": "跨平台命令速查（命令手册）"},
    "09": {"must": False, "desc": "Mac 环境速查（仅 Mac 项要求）"},
}


def load_notes():
    docs = {}
    for p in sorted((ROOT / "notes").glob("*.md")):
        m = re.match(r"(\d+)", p.name)
        if m:
            docs[m.group(1)] = io.open(p, encoding="utf-8").read()
    return docs


def check(which="all"):
    docs = load_notes()
    inventories = []
    if which in ("all", "mac"):
        inventories += [(s["name"], "mac") for s in config.PROFILE_MAC["facts"]["software"]]
    if which in ("all", "win"):
        inventories += [(s["name"], "win") for s in config.PROFILE_WIN["facts"]["software"]]

    # 软件是否实际安装（available 字段；缺省视为已安装）
    installed = {}
    for P, tag in ((config.PROFILE_MAC, "mac"), (config.PROFILE_WIN, "win")):
        for s in P["facts"]["software"]:
            installed[(s["name"], tag)] = s.get("available", True)

    gaps_must, gaps_should = [], []
    print(f"{'软件':<18}{'装机':<6}", end="")
    for k in DOC_RULES:
        print(f"{k:<5}", end="")
    print("  备注")

    seen = set()
    for name, tag in inventories:
        key = (name, tag)
        if key in seen:
            continue
        seen.add(key)
        pat = KEYWORDS.get(name)
        if pat is None:
            print(f"{name:<18}{'?' if tag=='mac' else '🟦':<6}  —— 无关键词映射，请在 KEYWORDS 补充")
            gaps_should.append(f"{name}({tag}) 缺关键词映射")
            continue
        # 检查范围：win 项不要求 09（Mac 专属文档）
        cov = {}
        for k, rule in DOC_RULES.items():
            if k not in docs:
                cov[k] = None
                continue
            text = docs[k]
            hit = bool(re.search(pat, text, re.I))
            cov[k] = hit
        avail = installed.get(key, True)
        mark = "🟡" if (tag == "mac" and avail) else ("⬜" if tag == "mac" else "🟦")
        cells = ""
        for k in DOC_RULES:
            v = cov[k]
            cells += ("✓   " if v else "·   ") if v else ("✗   " if v is False else "—   ")
        note = "未安装" if not avail else ""
        print(f"{name:<18}{mark:<6}{cells}  {note}")

        for k, hit in cov.items():
            if hit or k not in docs:
                continue
            rule = DOC_RULES[k]
            # Mac 未装的软件不要求出现在 Mac 速查 09；win 项不查 09
            if k == "09" and (tag == "win" or not avail):
                continue
            # 未安装软件在 06 只作 should 级（文档可说明"未装"）
            level = rule["must"] if avail else False
            # GUI 应用 / 库类软件对命令手册降为建议级
            if k == "06" and level and SOFT_KIND.get(name) != "cli" and name in SOFT_KIND:
                level = False
            item = f"{name}({tag}) 缺少 {k}-{rule['desc']}"
            (gaps_must if level else gaps_should).append(item)

    print()
    if gaps_must:
        print("【必须补齐的缺口】")
        for g in gaps_must:
            print("  ✗", g)
    if gaps_should:
        print("【建议补齐 / 提示】")
        for g in gaps_should:
            print("  △", g)
    if not gaps_must and not gaps_should:
        print("✓ 全部软件覆盖完整，无缺口")
    print(f"\n共检查 {len(seen)} 项软件 × {len(docs)} 份文档")
    return 1 if gaps_must else 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    sys.exit(check(arg))
