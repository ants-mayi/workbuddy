#!/bin/bash
# env.sh —— macOS/Linux 启动环境控制台 CLI（对应 Windows 的 env.bat）
# 用法：./env.sh status | doctor | recap | services | cache | web ...
cd "$(dirname "$0")" || exit 1

# 优先用 AI 环境（pytorch）解释器，缺失则退回 python3
PY="/Users/masc/miniconda3/envs/pytorch/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"

exec "$PY" engine/cli.py "$@"
