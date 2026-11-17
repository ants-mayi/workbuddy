# -*- coding: utf-8 -*-
"""
Web 控制台内容同步检查（命令行版）—— 与 Web「环境体检」面板共用同一实现
（engine/web.py 的 _web_sync_checks，经 /api/web-sync 暴露）。

检查项（全部只读）:
    平台与前端: 平台标识 / 前端副本同步 / 硬编码残留
    数据一致性: AI 解释器 / 路径事实 / 软件清单 / 环境变量 / 服务探测
    信息覆盖:   版本探测覆盖 / 命令库覆盖 / AI 工具面板数据

用法:
    python3 _check_web_sync.py
退出码: 有不一致为 1。
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "engine"))


def main():
    try:
        from web import app, _web_sync_checks
    except ModuleNotFoundError:
        # 当前解释器没有 flask：用 config 指定的 AI 解释器重跑自身
        import config  # noqa: E402
        alt = str(config.PROFILE["env"]["python_exe"] or sys.executable)
        if os.path.exists(alt) and os.path.abspath(alt) != os.path.abspath(sys.executable):
            print(f"(当前解释器缺 flask，改用 {alt} 重跑)\n")
            os.execv(alt, [alt, __file__])
        raise

    with app.app_context():          # 视图函数需要 app 上下文
        checks = _web_sync_checks()
    cur_group = None
    for c in checks:
        if c["group"] != cur_group:
            cur_group = c["group"]
            print(f"【{cur_group}】")
        print(f"  {'✓' if c['ok'] else '✗'} {c['name']}"
              + (f" —— {c['detail']}" if c["detail"] and not c["ok"] else ""))

    failed = [c for c in checks if not c["ok"]]
    print()
    if failed:
        print(f"共 {len(failed)} 处不一致：")
        for c in failed:
            print("  ✗", c["name"], "——", c["detail"])
        return 1
    print(f"✓ Web 端显示内容与本机实际状态完全同步（{len(checks)} 项检查）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
