# -*- coding: utf-8 -*-
"""
cli.py —— 通用 CLI 主程序（配置驱动，12 条命令）
所有主题特有关系来自 config.PROFILE；本文件不含任何主题硬编码。
"""
import json
import os
import random
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import typer
from rich.panel import Panel
from rich.table import Table

from core import (
    P, SHORT, ROOT, PROJ, EXP, DATA, NOTES, WEB, HF_HOME, PY_EXE,
    SERVE_PORT, WEB_PORT, SERVE_SCRIPT, PID_FILE, LOG_FILE, console,
    rule, ok, warn, bad, file_size_mb, assert_interpreter, py_probe,
    get_versions, port_open, pid_alive, read_pid, write_pid, clear_pid,
    kill_pid, csv_count, free_gb, pick_web_port, read_web_port,
    service_state, service_action,
)

app = typer.Typer(add_completion=False, no_args_is_help=False)


# ==================================================================
# status —— 状态总览
# ==================================================================
@app.command()
def status():
    """环境/版本/服务/产物状态，一条看清。忘记时先跑这条。"""
    rule(f"{SHORT.upper()} 状态总览 STATUS")
    v = get_versions()
    t = Table(show_header=False, box=None, pad_edge=False)
    t.add_column("项", style="cyan", width=18)
    t.add_column("值")
    t.add_row("解释器", str(PY_EXE) + ("" if PY_EXE.exists() else "  [red]缺失[/red]"))
    for k, val in v["versions"].items():
        t.add_row(k, str(val))
    if v.get("cuda") is not None:
        t.add_row("GPU 加速", "[green]是[/green]" if v["cuda"] else "[red]否[/red]")
        t.add_row("GPU", str(v.get("gpu") or "-"))
    t.add_row("缓存目录", (str(HF_HOME) + ("" if HF_HOME.exists() else "  [yellow]不存在[/yellow]")) if HF_HOME else "[yellow]未配置[/yellow]")
    if SERVE_PORT:
        t.add_row("推理服务", "[green]运行中[/green]" if port_open(SERVE_PORT) else "未运行")
    t.add_row("Web 控制台", "[green]运行中[/green]" if port_open(WEB_PORT) else "未运行")
    console.print(t)
    m = EXP / "model.safetensors"
    if m.exists():
        console.print(f"  主产物大小：{file_size_mb(m):.1f} MB")


# ==================================================================
# serve / stop —— 服务启停
# ==================================================================
@app.command()
def serve(
    foreground: bool = typer.Option(False, "-f", "--foreground", help="前台运行（调试用）"),
    port: int = typer.Option(None, "-p", "--port", help="覆盖默认端口"),
):
    """启动推理服务（后台），自动等就绪并打印 PID。"""
    if not P["serve"]["enabled"]:
        console.print(warn("本主题未启用推理服务（config: serve.enabled=False）"))
        return
    if not assert_interpreter():
        raise typer.Exit(1)
    if not SERVE_SCRIPT or not SERVE_SCRIPT.exists():
        console.print(bad(f"服务脚本不存在：{SERVE_SCRIPT}"))
        console.print("  请在 config.py 的 serve.script 指向你的服务脚本，或用生成器生成钩子模板。")
        raise typer.Exit(1)

    p = int(port or SERVE_PORT)
    if port_open(p):
        console.print(warn(f"端口 {p} 已被占用。先运行 {SHORT} stop，或用 -p 换端口。"))
        raise typer.Exit(1)
    env = dict(os.environ)
    env["HFKIT_SERVE_PORT"] = str(p)

    rule(f"启动服务 SERVE（端口 {p}）")
    if foreground:
        console.print("前台模式，Ctrl+C 结束。")
        subprocess.call([str(PY_EXE), str(SERVE_SCRIPT)], cwd=str(ROOT), env=env)
        return

    log = LOG_FILE.open("a", encoding="utf-8")
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    proc = subprocess.Popen(
        [str(PY_EXE), str(SERVE_SCRIPT)], cwd=str(ROOT), env=env,
        stdout=log, stderr=subprocess.STDOUT, creationflags=creationflags,
    )
    write_pid(proc.pid)
    console.print(f"  已启动 PID={proc.pid}，日志：{LOG_FILE}")
    for _ in range(30):
        if port_open(p):
            console.print(ok(f"服务就绪：{P['serve'].get('health', f'http://127.0.0.1:{p}')}"))
            console.print(f"  预测接口：{P['serve'].get('predict', '（见服务脚本）')}")
            return
        if not pid_alive(proc.pid):
            console.print(bad("进程提前退出，请查看日志："))
            console.print(LOG_FILE.read_text(encoding="utf-8", errors="replace")[-1500:])
            raise typer.Exit(1)
        time.sleep(1)
    console.print(warn("等待超时，服务可能仍在加载模型。用 status 查看。"))


@app.command()
def stop():
    """按 PID 终止服务进程树并释放端口。"""
    rule("停止服务 STOP")
    pid = read_pid()
    if pid and pid_alive(pid):
        kill_pid(pid)
        clear_pid()
        console.print(ok(f"已终止 PID={pid}"))
    else:
        console.print(warn("没有找到运行中的服务 PID（可能已停止）。"))
        clear_pid()
    if SERVE_PORT and not port_open(SERVE_PORT):
        console.print(ok(f"端口 {SERVE_PORT} 已释放"))


# ==================================================================
# data —— 数据速览
# ==================================================================
@app.command()
def data():
    """测试数据长什么样、标签什么意思、各集多少条。"""
    rule("测试数据 DATA")
    if not DATA.exists():
        console.print(bad(f"数据目录不存在：{DATA}"))
        raise typer.Exit(1)

    t = Table(show_header=True, header_style="bold magenta")
    t.add_column("文件")
    t.add_column("记录数", justify="right")
    t.add_column("列名")
    for spec in P["data"]["files"]:
        p = DATA / spec["name"]
        if not p.exists():
            t.add_row(spec["name"], "-", "缺失")
            continue
        n = csv_count(p)
        expect = spec.get("expect")
        mark = "" if not expect or n == expect else f"  [yellow](基线 {expect})[/yellow]"
        t.add_row(spec["name"], f"{n}{mark}", spec.get("columns", ""))
    console.print(t)

    if P["data"].get("label_note"):
        rule("标签含义")
        console.print(f"  {P['data']['label_note']}")
    src = EXP / P["data"]["label_source"] if P["data"].get("label_source") else None
    if src and src.exists():
        try:
            c = json.loads(src.read_text(encoding="utf-8"))
            if "id2label" in c:
                console.print(f"  id2label = {c['id2label']}")
        except Exception:
            pass

    sample = DATA / P["data"]["sample_file"] if P["data"].get("sample_file") else None
    if sample and sample.exists():
        rule("输入样例 SAMPLES")
        col = P["data"].get("sample_col")
        import csv
        with sample.open("r", encoding="utf-8", errors="replace") as f:
            for i, row in enumerate(csv.DictReader(f)):
                if i >= 3:
                    break
                text = row.get(col) if col else list(row.values())[-1]
                console.print(Panel(str(text)[:160], title=f"样例 {i + 1}", border_style="blue"))


# ==================================================================
# inspect —— 产物解读
# ==================================================================
@app.command()
def inspect():
    """产物目录每个文件什么意思 + 真实指标。"""
    rule("产物解读 INSPECT")
    if not EXP.exists():
        console.print(bad(f"产物目录不存在：{EXP}"))
        raise typer.Exit(1)
    meanings = P["artifacts"]["meanings"]
    t = Table(show_header=True, header_style="bold magenta")
    t.add_column("文件", style="cyan")
    t.add_column("大小")
    t.add_column("含义")
    for p in sorted(EXP.iterdir()):
        mb = file_size_mb(p)
        size = f"{mb:.1f} MB" if mb is not None else "-"
        t.add_row(p.name, size, meanings.get(p.name, "检查点 / 其它产物" if p.is_dir() else "辅助文件"))
    console.print(t)

    for fn in P["artifacts"].get("metrics_files", []):
        p = EXP / fn
        if p.exists():
            rule(fn)
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            tb = Table(show_header=False, box=None, pad_edge=False)
            tb.add_column("指标", style="cyan", width=22)
            tb.add_column("值")
            for k, val in d.items():
                tb.add_row(k, str(round(val, 4) if isinstance(val, float) else val))
            console.print(tb)


# ==================================================================
# recap —— 核心速记
# ==================================================================
@app.command()
def recap():
    """核心必背 + 铁律 + 常用命令。忘记时看这个最快进入状态。"""
    rule("核心必背 CORE")
    console.print(Panel(P["recap"]["core"], border_style="green", title="记住这几行"))
    if P["recap"].get("rules"):
        rule("本机铁律")
        for i, r in enumerate(P["recap"]["rules"], 1):
            console.print(f"[bold]{i}[/bold] {r}")
    rule("常用命令")
    cmds = [
        ("status", "环境/版本/GPU 状态"), ("doctor", "环境一键体检"),
        ("quiz", "主动回忆抽测"), ("services", "服务/端口状态"),
        ("cache", "缓存占用"), ("web", "启动网页控制台"),
    ]
    for c, d in cmds:
        console.print(f"  {SHORT} {c:<9} {d}")
    console.print(f"\n[dim]{P['recap'].get('commands_note', '')}[/dim]")


# ==================================================================
# doctor —— 环境体检
# ==================================================================
@app.command()
def doctor():
    """一键体检：版本/依赖/GPU/镜像/缓存/数据/产物/端口/磁盘。"""
    rule("环境体检 DOCTOR")
    rows, issues = [], []

    def add(name, state, detail, fix=""):
        rows.append((name, state, detail))
        if state in ("warn", "bad"):
            issues.append((name, state, fix))

    # 解释器
    add("解释器", "ok" if PY_EXE.exists() else "bad", str(PY_EXE),
        "改 config.py 的 env.python_exe" if not PY_EXE.exists() else "")

    # 版本
    v = get_versions()
    for spec in P["env"]["versions"]:
        label = spec["label"]
        val = v["versions"].get(label, "-")
        expect = spec.get("expect_major")
        if val in (None, "-", "ERR", "导入失败"):
            add(label, "bad", "导入失败", "用专用解释器手动 import 排查")
        elif expect and not str(val).startswith(str(expect)):
            add(label, "warn", f"{val}（预期 {expect}.x）", "版本与基线不符，注意 API 差异")
        else:
            add(label, "ok", str(val))

    # GPU / CUDA
    if v.get("cuda") is not None:
        if v["cuda"]:
            add("GPU 加速", "ok", f"可用 · {v.get('gpu') or '未知'}")
        else:
            add("GPU 加速", "warn", "CUDA/MPS 不可用（将用 CPU）", "检查驱动与 torch 版本匹配（Mac 看 torch.backends.mps）")

    # 镜像连通
    host = P["env"].get("mirror_host")
    if host:
        try:
            socket.create_connection((host, 443), timeout=3).close()
            add("镜像连通", "ok", P["env"].get("mirror_url") or host)
        except OSError:
            add("镜像连通", "warn", f"连接 {host}:443 失败", "检查网络；离线时用本地缓存")

    # 缓存
    if HF_HOME:
        add("缓存目录", "ok" if HF_HOME.exists() else "warn", str(HF_HOME),
            "" if HF_HOME.exists() else "首次下载会自动创建")

    # 数据
    for spec in P["data"]["files"]:
        p = DATA / spec["name"]
        if not p.exists():
            add(f"数据 {spec['name']}", "bad", "缺失", f"确认 {DATA} 完整")
            continue
        n = csv_count(p)
        expect = spec.get("expect")
        if expect and n != expect:
            add(f"数据 {spec['name']}", "warn", f"{n} 条（基线 {expect}）", "数据被改动，结果可能不同")
        else:
            add(f"数据 {spec['name']}", "ok", f"{n} 条")

    # 产物（未定义必需产物则跳过）
    must = P["artifacts"].get("must_exist", [])
    if must:
        missing = [m for m in must if not (EXP / m).exists()]
        if not missing:
            main_art = must[0]
            mb = file_size_mb(EXP / main_art) or 0
            add("主产物", "ok", f"齐全 · {main_art} {mb:.0f} MB")
        else:
            add("主产物", "bad", "缺失：" + ", ".join(missing), "先重新生成产物")

    # 附加检查（配置驱动）
    for chk in P.get("extra_checks", []):
        kind = chk.get("kind")
        fp = EXP / chk["file"] if chk.get("file") else None
        if kind == "json_key" and fp and fp.exists():
            try:
                d = json.loads(fp.read_text(encoding="utf-8"))
                add(chk["name"], "ok" if chk["key"] in d else "warn", f"{chk['key']}={d.get(chk['key'])}")
            except Exception:
                add(chk["name"], "warn", "JSON 解析失败")

    # 端口 & 磁盘
    if SERVE_PORT:
        add(f"端口 {SERVE_PORT}", "warn" if port_open(SERVE_PORT) else "ok",
            "已被占用" if port_open(SERVE_PORT) else "空闲")
    cap = free_gb()
    if cap is not None:
        state = "ok" if cap > 10 else ("warn" if cap > 3 else "bad")
        add("磁盘剩余", state, f"{cap:.1f} GB")

    # 渲染
    t = Table(show_header=True, header_style="bold magenta")
    t.add_column("检查项", style="cyan", width=20)
    t.add_column("状态", width=6)
    t.add_column("详情")
    for name, state, detail in rows:
        mark = {"ok": "[green]通过[/green]", "warn": "[yellow]注意[/yellow]", "bad": "[red]异常[/red]"}[state]
        t.add_row(name, mark, detail)
    console.print(t)
    n_ok = sum(1 for _, s, _ in rows if s == "ok")
    console.print(f"\n  通过 [green]{n_ok}[/green] / 共 {len(rows)} 项")
    if issues:
        console.print("[bold]需要关注：[/bold]")
        for name, state, fix in issues:
            color = "yellow" if state == "warn" else "red"
            console.print(f"  [{color}]·[/{color}] {name}" + (f" → {fix}" if fix else ""))
    else:
        console.print(ok("环境健康。"))


# ==================================================================
# quiz —— 主动回忆抽测
# ==================================================================
@app.command()
def quiz(
    count: int = typer.Option(10, "-n", "--count", min=1, max=50, help="抽题数量"),
    topic: str = typer.Option(None, "-t", "--topic", help="只练某主题"),
    list_topics: bool = typer.Option(False, "--list-topics", help="列出所有主题"),
):
    """主动回忆抽测：先答后看详解，统计正确率。"""
    mod_name = P["question_module"].replace(".py", "")
    try:
        bank_mod = __import__(mod_name)
        bank = bank_mod.QUESTION_BANK
    except Exception as e:
        console.print(bad(f"题库加载失败（{P['question_module']}）：{e}"))
        raise typer.Exit(1)

    # 占位符替换
    for q in bank:
        q["a"] = q["a"].replace("<short>", SHORT)
        q["q"] = q["q"].replace("<short>", SHORT)

    topics = sorted({q["t"] for q in bank})
    if list_topics:
        console.print("题库主题：" + " · ".join(topics) + f"（共 {len(bank)} 题）")
        return

    pool = [q for q in bank if q["t"] == topic] if topic else bank[:]
    if not pool:
        console.print(bad(f"没有主题为「{topic}」的题。可选：{' · '.join(topics)}"))
        raise typer.Exit(1)
    random.shuffle(pool)
    pool = pool[:count]

    rule(f"记忆抽测 QUIZ（{len(pool)} 题）")
    right = 0
    wrong_topics = []
    for i, q in enumerate(pool, 1):
        console.print(f"\n[bold]({i}/{len(pool)}) [{q['t']}][/bold] {q['q']}")
        answer = console.input("  你的答案（回车跳过 / q 退出）：").strip()
        if answer.lower() == "q":
            break
        if answer and any(k.lower() in answer.lower() for k in q["k"]):
            console.print(ok("答对了"))
            right += 1
        else:
            console.print(bad(f"参考答案：{q['a']}"))
            wrong_topics.append(q["t"])
        console.print(f"  [dim]详解：{q['d']}[/dim]")

    total = right + len(wrong_topics)
    if total:
        rule("成绩")
        console.print(f"  正确 {right} / {total} · 正确率 [green]{right / total:.0%}[/green]")
        if wrong_topics:
            console.print(f"  薄弱主题：{' · '.join(sorted(set(wrong_topics)))} → 建议 {SHORT} quiz -t <主题> 专项练")


# ==================================================================
# cache —— 缓存管理（默认只读）
# ==================================================================
@app.command()
def cache(
    clean: bool = typer.Option(False, "--clean", help="进入清理模式（默认只读报告）"),
    yes: bool = typer.Option(False, "--yes", help="真正删除（须配合 --clean）"),
):
    """缓存/检查点占用报告；清理须 --clean --yes 二次确认。"""
    rule("缓存管理 CACHE")
    for item in P["cache"]["items"]:
        p = _rp(item["path"])
        size = _dir_size(p) if p.exists() else None
        tag = "[green]可安全清理[/green]" if item.get("safe") else "[yellow]谨慎[/yellow]"
        s = f"{size / 1024 ** 2:.0f} MB" if size is not None else "不存在"
        console.print(f"  {item['name']}: {s}  {tag}")
        if item.get("note"):
            console.print(f"    [dim]{item['note']}[/dim]")

    if not clean:
        console.print(f"\n[dim]只读报告。要清理加 --clean（会再让你确认）。[/dim]")
        return
    targets = [it for it in P["cache"]["items"] if it.get("safe")]
    if not targets:
        console.print(warn("配置里没有标记为 safe=True 的可清理项。"))
        return
    total_mb = sum((_dir_size(_rp(it["path"])) or 0) for it in targets) / 1024 ** 2
    console.print(f"\n将清理 {len(targets)} 项，约 {total_mb:.0f} MB：")
    for it in targets:
        console.print(f"  · {it['name']}: {_rp(it['path'])}")
    if not yes:
        console.print(warn("这是预演。确认无误后加 --yes 真正删除。"))
        return
    for it in targets:
        p = _rp(it["path"])
        try:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            console.print(ok(f"已清理 {it['name']}"))
        except Exception as e:
            console.print(bad(f"清理失败 {it['name']}：{e}"))


# ==================================================================
# services —— 服务/常驻进程状态（跨平台）
# ==================================================================
@app.command()
def services():
    """查看本机关键服务/常驻进程运行状态、启动命令、端口快照（只读）。"""
    rule("服务与端口 SERVICES")
    facts = P.get("facts", {})

    t = Table(show_header=True, header_style="bold magenta")
    t.add_column("软件", style="cyan", width=18)
    t.add_column("当前状态", width=14)
    t.add_column("预期")
    t.add_column("启动命令 / 备注")
    for it in facts.get("services", []):
        state = service_state(it)
        running = str(state).lower() == str(it.get("expect", "")).lower()
        mark = ok(state) if running else warn(state)
        detail = it.get("start", "") + (("  · " + it["note"]) if it.get("note") else "")
        t.add_row(it["name"], mark, it.get("expect", ""), detail)
    if facts.get("services"):
        console.print(t)
    else:
        console.print(warn("config 未配置 facts.services"))

    ports = facts.get("ports", [])
    if ports:
        rule("常用端口")
        tp = Table(show_header=True, header_style="bold magenta")
        for col in ("端口", "协议", "用途", "状态"):
            tp.add_column(col)
        for p in ports:
            tp.add_row(p["port"], p["proto"], p["use"], p["state"])
        console.print(tp)
    console.print("\n[dim]服务状态为实时只读查询；启动/停止需管理员权限。完整信息见「学习文档」。[/dim]")


# ==================================================================
# curve —— 训练曲线（终端 ASCII + 可选 SVG）
# ==================================================================
@app.command()
def curve(export: bool = typer.Option(False, "--export", help="导出 SVG 到笔记目录")):
    """从产物日志画 loss/accuracy 曲线。"""
    hf = EXP / P["artifacts"]["history_file"]
    if not hf.exists():
        console.print(bad(f"未找到训练历史：{hf}"))
        raise typer.Exit(1)
    d = json.loads(hf.read_text(encoding="utf-8"))
    hist = d.get(P["artifacts"]["history_key"], [])
    xkey = P["artifacts"]["x_key"]
    points = [(h.get(xkey), {m: h[m] for m in P["artifacts"]["curve_metrics"] if m in h}) for h in hist]
    points = [(x, m) for x, m in points if m]
    if not points:
        console.print(warn("日志里没有可画的指标。"))
        return
    rule("训练曲线 CURVE")
    for metric in P["artifacts"]["curve_metrics"]:
        series = [(x, m[metric]) for x, m in points if metric in m]
        if series:
            console.print(_ascii_chart(series, metric))
    if export:
        out = NOTES / "训练曲线.svg"
        _export_svg(points, out)
        console.print(ok(f"已导出：{out}"))


# ==================================================================
# web —— 启动网页控制台
# ==================================================================
@app.command()
def web():
    """启动本地 Web 控制台并打开浏览器。"""
    if not assert_interpreter():
        raise typer.Exit(1)
    webctl = HERE / "web.py"
    rule("启动网页控制台 WEB")
    port, action, killed = pick_web_port(WEB_PORT)
    if not port:
        bad("端口全部被占用，无法启动 Web 控制台")
        raise typer.Exit(1)
    if action == "reused":
        console.print(f"  [dim]已关闭上次的 Web（PID {killed}），复用端口 {port}[/dim]")
    elif action == "shifted":
        warn(f"端口 {WEB_PORT} 被其它程序占用，改用 {port}")
    console.print(f"  地址：http://127.0.0.1:{port}")
    console.print("  关闭：在当前窗口按 Ctrl+C")
    import os as _os
    env = dict(_os.environ)
    env["HFKIT_WEB_PORT"] = str(port)   # 交给 web.py，避免二次决策
    subprocess.call([str(PY_EXE), str(webctl)], cwd=str(ROOT), env=env)


# ==================================================================
# 辅助函数（曲线绘图）
# ==================================================================
def _ascii_chart(points, title, width=56, height=10):
    vals = [v for _, v in points if isinstance(v, (int, float))]
    if not vals:
        return f"  {title}: 无数据"
    lo, hi = min(vals), max(vals)
    span = hi - lo or 1
    grid = [[" "] * width for _ in range(height)]
    xs = [int((i / max(len(points) - 1, 1)) * (width - 1)) for i in range(len(points))]
    for x, (_, v) in zip(xs, points):
        if not isinstance(v, (int, float)):
            continue
        row = height - 1 - int((v - lo) / span * (height - 1))
        grid[row][x] = "*"
    lines = [f"  {title}  [{lo:.4f} ~ {hi:.4f}]"]
    for r, row in enumerate(grid):
        label = f"{hi - (r / (height - 1)) * span:>8.4f} |"
        lines.append("  " + label + "".join(row))
    # X 轴刻度（稀疏；末尾补上最后一个真实 step，避免被截断）
    ticks = [" "] * width
    step = max(len(points) // 5, 1)
    idxs = sorted(set(list(range(0, len(points), step)) + [len(points) - 1]))
    for i in idxs:
        s = str(points[i][0])
        x = min(xs[i], width - len(s) // 2 - 1)  # 防止末尾标签越界截断
        start = max(0, x - len(s) // 2)
        for j, ch in enumerate(s):
            if start + j < width:
                ticks[start + j] = ch
    lines.append("  " + " " * 9 + "".join(ticks))
    return "\n".join(lines)


def _export_svg(points, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    W, H = 640, 360
    pad = 40
    series = {m: [(x, d[m]) for x, d in points if m in d] for m in P["artifacts"]["curve_metrics"]}
    allv = [v for arr in series.values() for _, v in arr if isinstance(v, (int, float))]
    lo, hi = (min(allv), max(allv)) if allv else (0, 1)
    span = hi - lo or 1
    colors = ["#2563eb", "#dc2626", "#16a34a", "#d97706"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">',
             f'<rect width="100%" height="100%" fill="#ffffff"/>',
             f'<text x="{pad}" y="24" font-size="16" fill="#1f2937">训练曲线 · {P["name"]}</text>']
    for gi, (m, arr) in enumerate([(k, v) for k, v in series.items() if v]):
        col = colors[gi % len(colors)]
        pts = []
        for i, (_, v) in enumerate(arr):
            x = pad + i / max(len(arr) - 1, 1) * (W - 2 * pad)
            y = H - pad - (v - lo) / span * (H - 2 * pad)
            pts.append(f"{x:.1f},{y:.1f}")
        parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="2"/>')
        parts.append(f'<text x="{pad + gi * 130}" y="{H - 10}" font-size="12" fill="{col}">{m}</text>')
    parts.append("</svg>")
    out.write_text("\n".join(parts), encoding="utf-8")


def _rp(p):
    q = Path(str(p).replace("\\", "/"))
    return q if q.is_absolute() else ROOT / q


def _dir_size(p):
    if p.is_file():
        return p.stat().st_size
    # scandir 迭代比 rglob+stat 快数倍（Windows 上尤其明显）
    total, stack = 0, [str(p)]
    while stack:
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=False):
                            stack.append(e.path)
                        elif e.is_file(follow_symlinks=False):
                            total += e.stat(follow_symlinks=False).st_size
                    except OSError:
                        pass
        except OSError:
            pass
    return total


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """一条龙控制台。无参数时显示提示。"""
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(
            f"[bold cyan]{P['name']} · 一条龙控制台[/bold cyan]\n"
            f"忘记时先跑 {SHORT} status / {SHORT} recap，检验记忆用 {SHORT} quiz，环境异常用 {SHORT} doctor。\n"
            f"用 {SHORT} --help 查看全部命令。",
            border_style="cyan"))


if __name__ == "__main__":
    app()
