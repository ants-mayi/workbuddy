#!/bin/bash
# env-web.sh —— macOS/Linux 启动 Web 控制台（对应 Windows 的 env-web.bat）
# 启动后自动打开浏览器；Ctrl+C 退出
cd "$(dirname "$0")" || exit 1

# 优先用 AI 环境（pytorch）解释器，缺失则退回 python3
PY="/Users/masc/miniconda3/envs/pytorch/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"

exec "$PY" engine/web.py
