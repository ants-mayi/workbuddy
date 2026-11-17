#!/bin/bash
# 启动Web控制台.command —— Finder 双击启动（macOS），终端窗口保持打开
cd "$(dirname "$0")" || exit 1
exec ./env-web.sh
