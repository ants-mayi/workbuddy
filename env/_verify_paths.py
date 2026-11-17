# -*- coding: utf-8 -*-
"""三层核验第一步：提取 config.py 全部声明路径并测存在性 + 读配置文件内容"""
import io, re, sys, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = open("config.py", encoding="utf-8").read()
# config.py 为 PROFILE_WIN + PROFILE_MAC 双覆盖层结构：取 WIN 段
i0 = src.find("PROFILE_WIN = {")
i1 = src.find("PROFILE_MAC = {")
win = src[i0:i1] if (i0 >= 0 and i1 > i0) else src

# 提取绝对路径：盘符 + 反斜杠（原始字符串里是单反斜杠）
paths = set()
for m in re.finditer(r'"([A-Za-z]:\\[^"]+)"', win):
    p = m.group(1)
    if not p.lower().endswith((".py", ".md")):
        paths.add(p)
print(f"共提取 {len(paths)} 个声明路径，逐个测存在性：")
missing = []
for p in sorted(paths):
    ok = os.path.exists(p)
    if not ok:
        missing.append(p)
print(f"存在 {len(paths)-len(missing)} / {len(paths)}")
if missing:
    print("!! 不存在的路径：")
    for p in missing:
        print("   ", p)

print("\n===== ② 内容核验：读取列出的配置文件 =====")
def head(path, n=15):
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
        return lines[:n]
    except Exception as e:
        return [f"<读取失败: {e}>"]

for f, n in [(r"C:\Users\marco\.gitconfig", 10),
             (r"C:\Users\marco\.workbuddy\mcp.json", 10),
             (r"C:\Users\marco\.condarc", 12)]:
    print(f"--- {f} ---")
    for l in head(f, n):
        print("   ", l)

# mcp.json 是否合法 JSON
try:
    json.load(open(r"C:\Users\marco\.workbuddy\mcp.json", encoding="utf-8"))
    print("mcp.json: 合法 JSON")
except Exception as e:
    print("mcp.json: 解析失败 ->", e)

print("\n===== ③ 生效链路核验：环境变量 vs 工具实际使用 =====")
for k in ("HF_HOME", "JAVA_HOME", "MAVEN_HOME", "GRADLE_HOME", "CONDA_PREFIX"):
    print(f"  {k} = {os.environ.get(k, '(未设置)')}")
# HF_HOME 声明值
declared_hf = r"G:\study\AI\cache\huggingface"
print(f"  HF_HOME 实际: {os.environ.get('HF_HOME','(未设置)')}  声明: {declared_hf}  一致: {os.environ.get('HF_HOME','')==declared_hf}")
# java 生效链路：PATH 里的 java 是哪个
import subprocess
try:
    out = subprocess.run(["where", "java"], capture_output=True, text=True, timeout=15).stdout
    print("  where java:", out.strip().replace("\n", " | "))
except Exception as e:
    print("  where java 失败:", e)
try:
    r = subprocess.run([r"D:\wofkIns\jdk-17.0.0.1\bin\java.exe", "-version"],
                       capture_output=True, text=True, timeout=20)
    print("  声明的 java.exe 可用:", (r.stderr or r.stdout).splitlines()[0])
except Exception as e:
    print("  声明的 java.exe 不可用:", e)
