# -*- coding: utf-8 -*-
"""
web.py —— 通用 Web 控制台后端（配置驱动，仅监听 127.0.0.1）
复用 core 的探测缓存；所有数据接口返回 JSON，供 index.html 消费。
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, send_from_directory, request

from core import (
    P, SHORT, ROOT, PROJ, EXP, DATA, NOTES, WEB, HF_HOME, PY_EXE,
    SERVE_PORT, WEB_PORT, PID_FILE, LOG_FILE, console,
    get_versions, port_open, port_listening, pid_alive, read_pid, write_pid, clear_pid,
    kill_pid, csv_count, free_gb, _resolve,
    pick_web_port, write_web_port, read_web_port,
    service_state, service_action, open_in_file_manager,
)

# Web 实际监听端口：由 pick_web_port 决策后写入，供接口回传
ACTIVE_PORT = read_web_port()

app = Flask(__name__, static_folder=None)
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


@app.after_request
def _no_cache(resp):
    """彻底禁用缓存：改了前端后浏览器必须拿到最新 HTML，避免旧 JS 残留报错。"""
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers.pop("ETag", None)
    resp.headers.pop("Last-Modified", None)
    return resp


def _clean(s):
    return ANSI_RE.sub("", s)


def run_cli(args, timeout=180):
    """调用 CLI 并回传去色文本（Web 与 CLI 共用同一逻辑，不重复实现）。"""
    code = (
        f"import sys; sys.path.insert(0, r'{Path(__file__).parent}'); "
        f"import cli; sys.argv=['{SHORT}'] + {args!r}; cli.app(standalone_mode=False)"
    )
    try:
        out = subprocess.run([str(PY_EXE), "-c", code], cwd=str(ROOT),
                             capture_output=True, text=True, timeout=timeout)
        return _clean((out.stdout or "") + (out.stderr or ""))
    except Exception as e:
        return f"执行失败：{e}"


# ── 页面与静态资源 ───────────────────────────────────────────────
# index.html 的唯一事实源是 engine/ 目录（本文件所在处）。
# 以前 web/ 另存一份副本，改了 engine 忘同步就会出现"菜单是旧的/面板空白"。
INDEX_DIR = Path(__file__).parent


@app.route("/")
def index():
    return send_from_directory(str(INDEX_DIR), "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    # 直接访问 /index.html 也走事实源；其余静态资源（marked.min.js 等）仍在 web/
    if filename == "index.html":
        return send_from_directory(str(INDEX_DIR), filename)
    return send_from_directory(str(WEB), filename)


# ── 元数据（前端据此渲染主题名/命令表）──────────────────────────
@app.route("/api/meta")
def api_meta():
    return jsonify({
        "name": P["name"], "short": SHORT, "desc": P["desc"],
        "platform": sys.platform,
        "os_name": {"darwin": "macOS", "win32": "Windows"}.get(sys.platform, "Linux"),
        "serve_predict": P["serve"].get("predict", "") if P["serve"]["enabled"] else "",
        "sections": P.get("ui", {}).get("sections"),   # 主题可定制面板列表；None=用默认
        "commands": [
            {"cmd": "status", "desc": "环境/版本/服务状态"},
            {"cmd": "doctor", "desc": "环境一键体检"},
            {"cmd": "quiz", "desc": "记忆抽测"},
            {"cmd": "data", "desc": "数据/标签/样例"},
            {"cmd": "inspect", "desc": "产物含义+指标"},
            {"cmd": "curve", "desc": "训练曲线"},
            {"cmd": "serve", "desc": "启动推理服务"},
            {"cmd": "stop", "desc": "停止推理服务"},
            {"cmd": "cache", "desc": "缓存管理"},
        ],
    })


@app.route("/api/health")
def api_health():
    return jsonify({"ok": True, "topic": P["name"]})


@app.route("/api/status")
def api_status():
    v = get_versions()
    return jsonify({
        "interpreter": str(PY_EXE),
        "interpreter_exists": PY_EXE.exists(),
        "versions": v["versions"],
        "cuda": v.get("cuda"),
        "gpu": v.get("gpu"),
        "cache": str(HF_HOME) if HF_HOME else "未配置",
        "serve": {"port": SERVE_PORT, "running": port_open(SERVE_PORT)} if SERVE_PORT else None,
        "web_port": ACTIVE_PORT, "configured_port": WEB_PORT,
    })


def _with_exists(items):
    """给一组 {name,path,...} 补上 exists 字段。"""
    out = []
    for it in items:
        d = dict(it)
        d["exists"] = _resolve(it["path"]).exists() if it.get("path") else None
        out.append(d)
    return out


@app.route("/api/facts")
def api_facts():
    """主题自带的静态事实（关键路径 / 配置文件 / 产物路径 / 端口 / 磁盘）。"""
    facts = P.get("facts", {})
    return jsonify({
        "paths": _with_exists(facts.get("paths", [])),
        "config_files": _with_exists(facts.get("config_files", [])),
        "products": _with_exists(facts.get("products", [])),
        "ports": facts.get("ports", []),
        "disks": facts.get("disks", []),
        "command_lib": facts.get("command_lib", []),
    })


@app.route("/api/services")
def api_services():
    """实测服务/常驻进程运行状态（只读），并回传启动/停止命令供复制。
    Windows：Get-Service；macOS/Linux：config 里每条服务的 probe 命令。"""
    out = []
    for it in P.get("facts", {}).get("services", []):
        svc = it.get("svc", "")
        state = service_state(it)
        ok = state.lower() == str(it.get("expect", "")).lower()
        out.append({"name": it["name"], "svc": svc, "state": state,
                    "expect": it.get("expect", ""), "ok": ok,
                    "start": it.get("start", ""),
                    "stop": it.get("stop", "") or (f"net stop {svc}  (管理员)" if svc else ""),
                    "note": it.get("note", "")})
    return jsonify({"services": out})


@app.route("/api/ai-tools")
def api_ai_tools():
    """AI 工具关键信息：版本/应用位置/配置文件/记忆体/项目目录，附存在性标记。"""
    out = []
    for t in P.get("facts", {}).get("ai_tools", []):
        items = []
        for it in t.get("items", []):
            raw = it.get("path") or ""
            if raw.startswith("~"):            # ~ 路径先展开，避免被 _resolve 拼进项目根
                path = os.path.expanduser(raw)
            elif raw:
                path = str(_resolve(raw))
            else:
                path = ""
            try:
                exists = os.path.exists(path) if path else None
            except Exception:
                exists = None
            items.append({"name": it.get("name", ""), "path": path,
                          "note": it.get("note", ""), "exists": exists})
        app_path = str(_resolve(t["app"])) if t.get("app") else ""
        out.append({"name": t.get("name", ""), "version": t.get("version", ""),
                    "app": app_path, "home": t.get("home", ""),
                    "size": t.get("size", ""), "note": t.get("note", ""),
                    "items": items,
                    "app_exists": os.path.exists(app_path) if app_path else None})
    return jsonify({"tools": out})


@app.route("/api/ai-local")
def api_ai_local():
    """本机 AI 全景：安装/环境、产物、日志、数据路径四类，附存在性标记。
    体积信息写在 config 的 note 里（实测快照），此处只做轻量 exists 判断，不遍历大目录。"""
    GROUPS = [
        ("installs", "安装 / 环境"),
        ("artifacts", "产物（模型 / 数据集）"),
        ("logs", "日志 / 训练状态"),
        ("data", "数据 / 缓存路径"),
    ]
    raw = P.get("facts", {}).get("ai_local", {})
    out = []
    for key, label in GROUPS:
        items = []
        for it in raw.get(key, []):
            r = it.get("path") or ""
            if r.startswith("~"):
                path = os.path.expanduser(r)
            elif r:
                path = str(_resolve(r))
            else:
                path = ""
            exists = os.path.exists(path) if path else None
            items.append({"name": it.get("name", ""), "path": path,
                          "note": it.get("note", ""), "exists": exists})
        out.append({"key": key, "label": label, "items": items})
    return jsonify({"groups": out})


def _app_bundle_version(app_path):
    """读取 macOS .app 的 CFBundleShortVersionString（无探测命令的 GUI 应用用）。"""
    try:
        import plistlib
        p = Path(app_path) / "Contents" / "Info.plist"
        if p.exists():
            with open(p, "rb") as f:
                return str(plistlib.load(f).get("CFBundleShortVersionString", "") or "")
    except Exception:
        pass
    return ""


@app.route("/api/software")
def api_software():
    """软件状态：实时版本（合并 get_versions）+ 路径存在性 + 启动命令。"""
    versions = get_versions().get("versions", {})
    items = []
    for s in P.get("facts", {}).get("software", []):
        label = s.get("probe_label", "")
        ver = versions.get(label, "") if label else ""
        path = _resolve(s["path"]) if s.get("path") else None
        if not ver and path is not None and str(path).endswith(".app"):
            ver = _app_bundle_version(path)  # GUI 应用从 Info.plist 读版本
        items.append({
            "name": s["name"], "category": s["category"],
            "version": ver if ver and ver != "-" else "",
            "available": bool(ver and ver != "-") if label else (path.exists() if path else False),
            "path": str(path) if path else "", "path_exists": path.exists() if path else None,
            "start": s.get("start", ""), "note": s.get("note", ""),
        })
    return jsonify({"software": items})


@app.route("/api/test")
def api_test():
    """快速自检：全部只读，不改系统。返回每项 PASS/WARN/FAIL。"""
    results = []

    def add(name, ok, detail, level_ok="PASS"):
        results.append({"name": name, "status": level_ok if ok else "FAIL", "detail": str(detail)})

    # 1) 解释器
    add("AI 解释器", PY_EXE.exists(), str(PY_EXE))
    # 2) 关键路径
    paths = _with_exists(P.get("facts", {}).get("paths", []))
    miss = [p["name"] for p in paths if not p["exists"]]
    add("关键路径", not miss, "全部存在" if not miss else "缺失：" + "、".join(miss))
    # 3) 版本探测
    versions = get_versions().get("versions", {})
    bad = [k for k, v in versions.items() if not v or v == "-"]
    add("版本探测", not bad,
        f"{len(versions) - len(bad)}/{len(versions)} 项可用" if not bad else "失败：" + "、".join(bad))
    # 4) GPU
    cuda = get_versions().get("cuda")
    gpu = get_versions().get("gpu")
    add("GPU 加速", bool(cuda), f"{gpu}（CUDA/MPS {'可用' if cuda else '不可用'}）", level_ok="PASS")
    # 5) Web 自身端口连通
    add("Web 服务", port_open(ACTIVE_PORT), f"127.0.0.1:{ACTIVE_PORT}")
    # 6) 服务端口连通（只读探测，报告状态不判定失败）
    port_rows = []
    facts = P.get("facts", {})
    # 从 services 里取 svc 名对应的端口不易，直接用 ports 快照做连通探测说明
    for it in facts.get("ports", []):
        raw = str(it.get("port", ""))
        first = raw.split("/")[0].strip()
        if first.isdigit():
            port_rows.append(f"{first}({it.get('use','')}):{'监听中' if port_listening(int(first)) else '未监听'}")
    results.append({"name": "常用端口连通", "status": "INFO",
                    "detail": "；".join(port_rows) if port_rows else "无可探测端口"})
    # 7) 配置文件 / 产物路径（报告存在性，缺失为 WARN 不判失败）
    for group_name, key in [("配置文件", "config_files"), ("产物路径", "products")]:
        items = _with_exists(facts.get(key, []))
        have = sum(1 for x in items if x["exists"])
        results.append({"name": group_name, "status": "PASS" if have == len(items) else "WARN",
                        "detail": f"{have}/{len(items)} 存在"})
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    return jsonify({"results": results, "passed": passed, "failed": failed})


@app.route("/api/service/action", methods=["POST"])
def api_service_action():
    """服务启停：仅允许 config 白名单里的服务，尝试执行并回传结果。
    Windows 走 net start/stop；macOS 走 config 里配置的 start/stop 命令。
    权限不足或失败时回传明确提示，前端展示命令供手动执行。"""
    data = request.get_json(silent=True) or {}
    svc = str(data.get("svc", ""))
    action = str(data.get("action", ""))
    allowed = {it.get("svc") for it in P.get("facts", {}).get("services", [])}
    if svc not in allowed:
        return jsonify({"ok": False, "msg": "服务名不在白名单，拒绝执行"})
    if action not in ("start", "stop"):
        return jsonify({"ok": False, "msg": "仅支持 start/stop"})
    item = next(it for it in P.get("facts", {}).get("services", [])
                if it.get("svc") == svc)
    ok, msg, cmd = service_action(item, action)
    return jsonify({"ok": ok, "msg": msg, "cmd": cmd})


@app.route("/api/path-truth")
def api_path_truth():
    """PATH 真相：where 实测每个命令的解析结果，多候选/期望未命中给预警。"""
    out = []
    for c in P.get("facts", {}).get("path_commands", []):
        cmd = c["cmd"]
        paths, multi, hit_expect = [], False, True
        try:
            if __import__("sys").platform == "win32":
                r = subprocess.run(["cmd", "/c", f"where {cmd}"], capture_output=True, text=True, timeout=20)
                paths = [x.strip() for x in (r.stdout or "").splitlines() if x.strip()]
            else:
                r = subprocess.run(["which", "-a", cmd], capture_output=True, text=True, timeout=20)
                paths = [x.strip() for x in (r.stdout or "").splitlines() if x.strip()]
        except Exception as e:
            paths = []
        multi = len(paths) > 1
        expect = c.get("expect", "")
        if expect:
            hit_expect = any(expect.lower().replace("/", "\\") in p.lower().replace("/", "\\") for p in paths)
        out.append({"cmd": cmd, "paths": paths, "effective": paths[0] if paths else "",
                    "count": len(paths), "multi": multi, "expect": expect,
                    "hit_expect": hit_expect, "note": c.get("note", "")})
    return jsonify({"commands": out})


@app.route("/api/env-vars")
def api_env_vars():
    """环境变量：只读展示当前值 + 与预期比对。PATH 不全文回传。"""
    import os as _os
    out = []
    for v in P.get("facts", {}).get("env_vars", []):
        name = v["name"]
        val = _os.environ.get(name, "")
        expect = v.get("expect", "")
        matched = (not expect) or (val.lower().replace("/", "\\") == expect.lower().replace("/", "\\"))
        shown = val
        if name == "PATH" and len(val) > 260:
            shown = val[:260] + f" …（共 {len(val)} 字符）"
        out.append({"name": name, "value": shown, "set": bool(val),
                    "expect": expect, "matched": matched, "note": v.get("note", "")})
    return jsonify({"vars": out})


def _probe_threads(pid):
    """尽力读取某进程的线程数与 TID。

    优先 psutil.threads()；被系统拒绝时（macOS 新版对第三方进程线程表有保护，
    终端环境也可能被拒）回退 `/bin/ps -M -p <pid>`——沙箱内 ps 被禁会静默失败，
    正常终端环境可用。TID 列表仅 psutil 可用时提供（ps -M 格式跨版本不稳）。
    """
    try:
        import psutil
        th = psutil.Process(pid).threads()
        return len(th), [t[0] for t in th][:60]
    except Exception:
        pass
    try:
        import subprocess as _sp
        r = _sp.run(["/bin/ps", "-M", "-p", str(pid)], capture_output=True,
                    text=True, timeout=10)
        if r.returncode == 0:
            lines = [l for l in (r.stdout or "").splitlines() if l.strip()]
            if len(lines) > 1:
                return len(lines) - 1, []  # 表头外的每行是一个线程
    except Exception:
        pass
    return None, []


@app.route("/api/ports-live")
def api_ports_live():
    """实时监听端口：psutil 扫描 LISTENING，关联进程；标注已知用途与冲突。"""
    # 已知端口用途（来自 facts.ports 的快照）
    known = {}
    for it in P.get("facts", {}).get("ports", []):
        for token in str(it.get("port", "")).split("/"):
            token = token.strip()
            if token.isdigit():
                known[int(token)] = it.get("use", "")
    rows = []
    conns = None
    try:
        import psutil
        conns = psutil.net_connections(kind="inet")
    except Exception:
        conns = None  # psutil 缺失或 macOS 权限受限 → 统一降级 lsof
    if conns is not None:
        for c in conns:
            try:
                if c.status != psutil.CONN_LISTEN or not c.laddr or not c.pid:
                    continue
                port = getattr(c.laddr, "port", None)
                ip = getattr(c.laddr, "ip", "")
                if not port:
                    continue
                pname = ""
                threads, tids = None, []
                try:
                    pname = psutil.Process(c.pid).name()
                except Exception:
                    pass
                threads, tids = _probe_threads(c.pid)
                rows.append({"port": port, "ip": ip, "pid": c.pid, "proc": pname,
                             "threads": threads, "tids": tids,
                             "use": known.get(port, ""), "known": port in known})
            except Exception:
                continue  # 单条连接读取失败（权限/进程消失）直接跳过
    elif conns is None:
        # psutil 缺失/受限：macOS/Linux 用 lsof 兜底（Windows 理论上不会走到这）
        import subprocess as _sp
        _psu = None
        try:
            import psutil as _psu  # 线程信息尽力探测（连接被拒时进程线程可能仍可读）
        except Exception:
            _psu = None
        try:
            r = _sp.run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"], capture_output=True,
                        text=True, timeout=20)
            for line in (r.stdout or "").splitlines()[1:]:
                f = line.split()
                if len(f) >= 9 and ":" in f[8]:
                    try:
                        port = int(f[8].rsplit(":", 1)[1])
                    except ValueError:
                        continue
                    pid = int(f[1]) if f[1].isdigit() else None
                    pname = f[0]
                    if _psu is not None and pid:
                        try:
                            pname = _psu.Process(pid).name() or f[0]  # name() 沙箱内仍可读，避免 lsof 9 字符截断
                        except Exception:
                            pass
                    threads, tids = _probe_threads(pid) if pid else (None, [])
                    rows.append({"port": port, "ip": "*", "pid": pid,
                                 "proc": pname, "threads": threads, "tids": tids,
                                 "use": known.get(port, ""), "known": port in known})
        except Exception as e:
            return jsonify({"error": f"端口扫描失败（lsof 兜底也失败）：{e}", "rows": []})
    else:
        return jsonify({"error": "端口扫描失败", "rows": []})
    # 去重（IPv4/IPv6 双栈会对同一 port+pid 出现两行）+ 冲突检测：同端口多个不同 PID 监听
    seen, uniq = set(), []
    for r in rows:
        k = (r["port"], r["pid"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    rows = uniq
    from collections import defaultdict as _dd
    by_port = _dd(list)
    for r in rows:
        by_port[r["port"]].append(r)
    conflicts = [p for p, rs in by_port.items() if len({x["pid"] for x in rs}) > 1]
    for r in rows:
        r["conflict"] = r["port"] in conflicts
    rows.sort(key=lambda x: (not x["known"], x["port"]))
    # 运行环境自诊断：父进程链 + ps 可用性探测（前端据此给出准确提示）
    runtime = {"pid": os.getpid(), "parents": [], "ps_ok": None, "ps_sample": ""}
    try:
        import psutil as _p
        pr, hops = _p.Process(os.getpid()), 0
        while pr is not None and hops < 5:
            try:
                runtime["parents"].append(pr.name())
                pr = pr.parent()
            except Exception:
                break
            hops += 1
    except Exception:
        pass
    for r in rows:
        if r["pid"] and r["pid"] != os.getpid():
            try:
                import subprocess as _sp
                rr = _sp.run(["/bin/ps", "-M", "-p", str(r["pid"])], capture_output=True,
                             text=True, timeout=10)
                runtime["ps_ok"] = (rr.returncode == 0 and
                                    len(rr.stdout.strip().splitlines()) > 1)
                runtime["ps_sample"] = (rr.stdout or "")[:300]
            except Exception as e:
                runtime["ps_ok"] = False
                runtime["ps_sample"] = f"{type(e).__name__}: {e}"
            break
    return jsonify({"rows": rows, "conflicts": conflicts,
                    "total": len(rows), "known_count": sum(1 for r in rows if r["known"]),
                    "runtime": runtime})


@app.route("/api/processes")
def api_processes():
    """关键进程检测：扫描命令行含 watch 关键字的进程（避免重复启动 Web）。"""
    keys = P.get("facts", {}).get("watch_processes", [])
    found = []
    try:
        import psutil
        for p in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
            try:
                info = p.info
                cmd = " ".join(info.get("cmdline") or [])
                if any(k in cmd for k in keys):
                    import datetime as _dt
                    ct = info.get("create_time")
                    found.append({"pid": info["pid"], "name": info.get("name", ""),
                                  "cmd": cmd,
                                  "start": _dt.datetime.fromtimestamp(ct).strftime("%m-%d %H:%M:%S") if ct else "",
                                  "is_self": info["pid"] == __import__("os").getpid()})
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        # psutil 未安装：用 ps 兜底（macOS/Linux）
        import subprocess as _sp
        import datetime as _dt
        try:
            r = _sp.run(["ps", "-axo", "pid=,lstart=,command="], capture_output=True,
                        text=True, timeout=20)
            for line in (r.stdout or "").splitlines():
                parts = line.split()
                if len(parts) < 9:
                    continue
                pid_txt, cmd = parts[0], " ".join(parts[5:])
                if any(k in cmd for k in keys):
                    try:
                        ct = _dt.datetime.strptime(
                            " ".join(parts[1:5]), "%a %b %d %H:%M:%S %Y")
                        start = ct.strftime("%m-%d %H:%M:%S")
                    except Exception:
                        start = ""
                    found.append({"pid": int(pid_txt), "name": parts[5], "cmd": cmd,
                                  "start": start,
                                  "is_self": int(pid_txt) == __import__("os").getpid()})
        except Exception as e:
            return jsonify({"error": str(e), "processes": []})
    except Exception as e:
        return jsonify({"error": str(e), "processes": []})
    return jsonify({"processes": found, "keys": keys})


@app.route("/api/open-path", methods=["POST"])
def api_open_path():
    """在资源管理器中打开路径：仅允许 facts 里登记过的目录，白名单防越权。"""
    data = request.get_json(silent=True) or {}
    target = str(data.get("path", "")).strip()
    allowed = set()
    facts = P.get("facts", {})
    for key in ("paths", "config_files", "products"):
        for it in facts.get(key, []):
            if it.get("path"):
                allowed.add(str(_resolve(it["path"])))
    # 也允许打开这些路径的父目录（如打开解释器所在文件夹）
    q = _resolve(target) if target else None
    if not q or str(q) not in allowed:
        return jsonify({"ok": False, "msg": "路径不在白名单，拒绝打开"})
    if not q.exists():
        return jsonify({"ok": False, "msg": "路径不存在"})
    try:
        folder = str(q) if q.is_dir() else str(q.parent)
        open_in_file_manager(folder)
        return jsonify({"ok": True, "msg": f"已打开：{folder}"})
    except Exception as e:
        return jsonify({"ok": False, "msg": f"打开失败：{e}"})


@app.route("/api/doctor")
def api_doctor():
    return jsonify({"text": run_cli(["doctor"])})


# ── Web 显示同步检查（环境体检面板与 _check_web_sync.py 共用同一实现）──
_VERSION_LABELS = {
    "mac": {"JDK 17": "JDK", "Maven 3.9": "Maven", "Node.js 22": "Node.js",
            "npm 10": "npm", "Git": "Git", "Go": "Go", "Conda": "Conda",
            "Python (AI 环境)": "Python", "PyTorch": "torch",
            "Transformers": "transformers", "Flask": "Flask", "Ollama": "Ollama",
            "Homebrew": "Homebrew", "ffmpeg": "ffmpeg", "Deno": "Deno",
            "Xcode CLT": "clang (Xcode CLT)"},
    "win": {"JDK 17": "JDK", "Maven 3.9": "Maven", "Node.js 22": "Node.js",
            "npm 10": "npm", "Git": "Git", "Conda (D 盘)": "Conda",
            "Python (AI 环境)": "Python", "PyTorch": "torch",
            "Transformers": "transformers", "Flask": "Flask"},
}
_CMDLIB_EXPECT = {"mac": ["go", "deno", "ffmpeg", "ollama", "tailscale", "clang",
                          "workbuddy", "codex", "brew", "git", "mvn", "node", "java", "flask",
                          "tar", "unzip"],
                  "win": []}


def _web_sync_checks():
    """核对 Web 各面板显示内容与本机实际状态是否一致，返回检查结果列表。"""
    import io as _io
    import re as _re
    C = []

    def add(group, name, ok, detail=""):
        C.append({"group": group, "name": name, "ok": bool(ok), "detail": str(detail)})

    eng_path = Path(__file__).parent / "index.html"
    web_copy = Path(__file__).parent.parent / "web" / "index.html"
    is_win = sys.platform == "win32"
    plat_key = "win" if is_win else "mac"

    # 【1】平台标识
    meta = api_meta().get_json()
    expect_os = {"darwin": "macOS", "win32": "Windows"}.get(sys.platform, "Linux")
    add("平台与前端", "平台标识与本机一致", meta.get("platform") == sys.platform,
        f"web={meta.get('platform')} 实际={sys.platform}")
    add("平台与前端", "系统名称与本机一致", meta.get("os_name") == expect_os,
        f"web={meta.get('os_name')} 实际={expect_os}")

    # 【2】前端副本同步
    try:
        same = (_io.open(eng_path, encoding="utf-8").read()
                == _io.open(web_copy, encoding="utf-8").read())
        add("平台与前端", "前端副本同步（engine = web）", same,
            "两份副本不一致：cp engine/index.html web/index.html 后刷新")
    except OSError as e:
        add("平台与前端", "前端副本同步（engine = web）", False, str(e))

    # 【3】硬编码残留
    try:
        eng_html = _io.open(eng_path, encoding="utf-8").read()
        if is_win:
            add("平台与前端", "盘符路径残留检查", True, "Windows 机器跳过")
        else:
            stale = _re.findall(r"[A-Z]:\\(?:wofk|work|study|AI|Game)[^\"'<\s]*", eng_html)
            add("平台与前端", "无写死 Windows 盘符路径", not stale, f"发现: {stale[:3]}")
    except OSError as e:
        add("平台与前端", "盘符路径残留检查", False, str(e))

    # 【4】AI 解释器
    status = api_status().get_json()
    py = status.get("interpreter", "")
    py_ok = bool(py) and os.path.exists(py)
    add("数据一致性", "AI 解释器真实存在", py_ok, f"面板显示: {py or '(空)'}")
    if py_ok:
        r = subprocess.run([py, "-c", "import sys;print(1)"], capture_output=True, timeout=30)
        add("数据一致性", "AI 解释器可执行", r.returncode == 0,
            r.stderr.decode(errors="replace")[:120])
    if not is_win:
        add("数据一致性", "GPU 标识为 Apple MPS", "MPS" in str(status.get("gpu", "")),
            f"gpu={status.get('gpu')}")

    # 【5】路径事实
    facts = api_facts().get_json()
    bad = [p["path"] for p in facts.get("paths", [])
           if bool(p.get("exists")) != os.path.exists(p["path"])]
    add("数据一致性", f"路径存在性标记与实际一致（{len(facts.get('paths', []))} 项）",
        not bad, f"不一致: {bad}")

    # 【6】软件清单
    sw = api_software().get_json()["software"]
    bad_sw = [f"{s['name']}({s['path']})" for s in sw
              if s.get("available") and s.get("path") and not os.path.exists(s["path"])]
    add("数据一致性", f"在用软件路径真实存在（{len(sw)} 项）", not bad_sw, f"不一致: {bad_sw}")

    # 【7】环境变量
    ev = api_env_vars().get_json().get("vars", [])
    bad_ev = [v["name"] for v in ev if bool(v.get("set")) != (v["name"] in os.environ)]
    add("数据一致性", f"环境变量 set 标记与实际一致（{len(ev)} 项）", not bad_ev, f"不一致: {bad_ev}")

    # 【8】服务探测
    svcs = api_services().get_json().get("services", [])
    empty = [s["name"] for s in svcs if not s.get("state")]
    add("数据一致性", f"服务探测均有状态（{len(svcs)} 项）", not empty, f"空状态: {empty}")

    # 【9】版本探测覆盖
    ver_labels = set(status.get("versions", {}).keys())
    mapping = _VERSION_LABELS.get(plat_key, {})
    missing = [s["name"] for s in P.get("facts", {}).get("software", [])
               if s.get("available", True) and s["name"] in mapping
               and mapping[s["name"]] not in ver_labels]
    add("信息覆盖", f"已装 CLI 软件均有版本探测（versions 共 {len(ver_labels)} 项）",
        not missing, f"缺探测: {missing}")

    # 【10】命令库覆盖
    lib = P.get("facts", {}).get("command_lib", [])
    lib_text = " ".join(g.get("group", "") for g in lib).lower() + " " + \
        " ".join(it.get("cmd", "") for g in lib for it in g.get("items", [])).lower()
    missing_lib = [t for t in _CMDLIB_EXPECT.get(plat_key, []) if t not in lib_text]
    add("信息覆盖", f"关键 CLI 软件均有命令组（共 {len(lib)} 组）",
        not missing_lib, f"命令库缺: {missing_lib}")

    # 【11】AI 工具面板
    tools = api_ai_tools().get_json().get("tools", [])
    bad_tools = []
    for t in tools:
        if t.get("app") and t.get("app_exists") is False:
            bad_tools.append(f"{t['name']}(应用缺失)")
        bad_tools += [f"{t['name']}/{i['name']}" for i in t.get("items", [])
                      if i.get("exists") is False]
    add("信息覆盖",
        f"AI 工具路径与实际一致（{len(tools)} 工具 / "
        f"{sum(len(t.get('items', [])) for t in tools)} 项路径）",
        not bad_tools, f"不一致: {bad_tools}")

    # 【12】配置文件 / 产物路径存在性（与快速测试第 7/8 项同源；相对路径按项目根解析）
    _root = Path(__file__).parent.parent

    def _real(p):
        q = Path(os.path.expanduser(str(p)))
        return q if q.is_absolute() else _root / q
    bad_cfg = [c["name"] for c in facts.get("config_files", [])
               if bool(c.get("exists")) != _real(c["path"]).exists()]
    add("数据一致性", f"配置文件存在性标记与实际一致（{len(facts.get('config_files', []))} 项）",
        not bad_cfg, f"不一致: {bad_cfg}")
    bad_prod = [p["name"] for p in facts.get("products", [])
                if bool(p.get("exists")) != _real(p["path"]).exists()]
    add("数据一致性", f"产物路径存在性标记与实际一致（{len(facts.get('products', []))} 项）",
        not bad_prod, f"不一致: {bad_prod}")

    # 【13】服务状态与预期一致（expect=按需/无 的不比对）
    mism = [f"{s['name']}(实际 {s.get('state')} / 预期 {s.get('expect')})"
            for s in svcs if s.get("expect") in ("Running", "Stopped")
            and s.get("state", "").lower() != s["expect"].lower()]
    add("数据一致性", f"服务运行状态与预期一致（{len(svcs)} 项）",
        not mism, f"不符: {mism}")

    # 【14】端口快照不过期：标"监听中"的端口必须实测在监听
    stale_ports = []
    for p in facts.get("ports", []):
        first = str(p.get("port", "")).split("/")[0].strip()
        if "监听中" in str(p.get("state", "")) and first.isdigit() and not port_listening(int(first)):
            stale_ports.append(f"{first}({p.get('use', '')})")
    add("数据一致性", f"端口快照『监听中』与实机一致（{len(facts.get('ports', []))} 行）",
        not stale_ports, f"快照过期: {stale_ports}")
    return C


@app.route("/api/web-sync")
def api_web_sync():
    """Web 显示同步检查结果（环境体检面板展示，_check_web_sync.py 复用）。"""
    checks = _web_sync_checks()
    return jsonify({"checks": checks,
                    "passed": sum(1 for c in checks if c["ok"]),
                    "failed": sum(1 for c in checks if not c["ok"])})


@app.route("/api/data")
def api_data():
    files = []
    for spec in P["data"]["files"]:
        p = DATA / spec["name"]
        files.append({"name": spec["name"], "exists": p.exists(),
                      "count": csv_count(p) if p.exists() else None,
                      "expect": spec.get("expect"), "columns": spec.get("columns", "")})
    labels = None
    src = EXP / P["data"]["label_source"] if P["data"].get("label_source") else None
    if src and src.exists():
        try:
            labels = json.loads(src.read_text(encoding="utf-8")).get("id2label")
        except Exception:
            pass
    return jsonify({"files": files, "label_note": P["data"].get("label_note"),
                    "labels": labels})


@app.route("/api/inspect")
def api_inspect():
    out = []
    if EXP.exists():
        meanings = P["artifacts"]["meanings"]
        for p in sorted(EXP.iterdir()):
            out.append({"name": p.name,
                        "size_mb": round(p.stat().st_size / 1024 ** 2, 1) if p.is_file() else None,
                        "meaning": meanings.get(p.name, "检查点 / 其它产物" if p.is_dir() else "辅助文件")})
    metrics = {}
    for fn in P["artifacts"].get("metrics_files", []):
        p = EXP / fn
        if p.exists():
            try:
                metrics[fn] = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return jsonify({"files": out, "metrics": metrics})


@app.route("/api/curve")
def api_curve():
    hf = EXP / P["artifacts"]["history_file"]
    if not hf.exists():
        return jsonify({"error": "未找到训练历史", "path": str(hf)})
    d = json.loads(hf.read_text(encoding="utf-8"))
    hist = d.get(P["artifacts"]["history_key"], [])
    xkey = P["artifacts"]["x_key"]
    series = {m: [] for m in P["artifacts"]["curve_metrics"]}
    for h in hist:
        for m in series:
            if m in h and isinstance(h[m], (int, float)):
                series[m].append({"x": h.get(xkey), "y": h[m]})
    return jsonify({"series": series})


@app.route("/api/quiz/questions")
def api_quiz_questions():
    mod_name = P["question_module"].replace(".py", "")
    try:
        bank = __import__(mod_name).QUESTION_BANK
    except Exception as e:
        return jsonify({"error": str(e)})
    for q in bank:
        q["a"] = q.get("a", "").replace("<short>", SHORT)
        q["q"] = q.get("q", "").replace("<short>", SHORT)
    topics = {}
    for q in bank:
        topics[q["t"]] = topics.get(q["t"], 0) + 1
    return jsonify({"total": len(bank), "topics": topics, "questions": bank})


# 缓存大小后台计算 + TTL 缓存 + 持久化：
# 1) 目录全量遍历在大缓存(40+GB)下要几十秒，不能在请求线程里同步算
# 2) 结果落盘 .cache.sizes.json，重启后立即显示上次数值而非"计算中"
# 3) scandir 迭代代替 rglob+stat（Windows 上数倍快）
_CACHE_TTL = 600  # 秒
_CACHE_SIZES_FILE = ROOT / ".cache.sizes.json"
_cache_size_state = {"sizes": {}, "ts": 0.0, "computing": False, "lock": None}

def _dir_size_fast(p):
    """os.scandir 迭代求目录大小（比 rglob+stat 快数倍，symlink 不跟随）。"""
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

def _cache_state_lock():
    if _cache_size_state["lock"] is None:
        _cache_size_state["lock"] = threading.Lock()
    return _cache_size_state["lock"]

def _load_cache_sizes():
    """启动时读上次结果，让面板秒出真实数值。"""
    try:
        d = json.loads(_CACHE_SIZES_FILE.read_text(encoding="utf-8"))
        _cache_size_state["sizes"] = d.get("sizes", {})
        _cache_size_state["ts"] = d.get("ts", 0.0)
    except Exception:
        pass

def _save_cache_sizes():
    try:
        _CACHE_SIZES_FILE.write_text(json.dumps(
            {"sizes": _cache_size_state["sizes"], "ts": _cache_size_state["ts"]},
            ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

def _compute_cache_sizes_async():
    with _cache_state_lock():
        if _cache_size_state["computing"]:
            return
        _cache_size_state["computing"] = True
    def _work():
        sizes = {}
        for it in P["cache"]["items"]:
            try:
                p = _resolve(it["path"])
                sizes[it["name"]] = (_dir_size_fast(p) if p.is_dir() else p.stat().st_size) \
                    if p.exists() else None
            except Exception:
                sizes[it["name"]] = None
        _cache_size_state["sizes"] = sizes
        _cache_size_state["ts"] = time.time()
        _cache_size_state["computing"] = False
        _save_cache_sizes()
    threading.Thread(target=_work, daemon=True).start()

@app.route("/api/cache")
def api_cache():
    fresh = (time.time() - _cache_size_state["ts"]) < _CACHE_TTL
    sizes = dict(_cache_size_state["sizes"])
    if not fresh:
        _compute_cache_sizes_async()  # 后台重算，本次先回上次值
    items = []
    for it in P["cache"]["items"]:
        s = sizes.get(it["name"])
        items.append({"name": it["name"], "path": str(_resolve(it["path"])),
                      "safe": it.get("safe", False),
                      "size_mb": round(s / 1024 ** 2, 1) if s is not None else None,
                      "note": it.get("note", "")})
    return jsonify({"items": items, "computed_at": _cache_size_state["ts"],
                    "computing": _cache_size_state["computing"]})


@app.route("/api/cache/clean", methods=["POST"])
def api_cache_clean():
    import shutil as _sh
    cleaned = []
    for it in P["cache"]["items"]:
        if not it.get("safe"):
            continue
        p = _resolve(it["path"])
        try:
            if p.is_dir():
                _sh.rmtree(p)
            elif p.exists():
                p.unlink()
            cleaned.append(it["name"])
        except Exception:
            pass
    return jsonify({"cleaned": cleaned})


@app.route("/api/serve", methods=["POST"])
def api_serve():
    if not P["serve"]["enabled"]:
        return jsonify({"ok": False, "msg": "本主题未启用服务"})
    if not PY_EXE.exists():
        return jsonify({"ok": False, "msg": f"解释器不存在：{PY_EXE}"})
    d = request.get_json(silent=True) or {}
    port = int(d.get("port") or SERVE_PORT)
    if port_open(port):
        return jsonify({"ok": False, "msg": f"端口 {port} 已占用"})
    script = _resolve(P["serve"]["script"]) if P["serve"].get("script") else None
    if not script or not script.exists():
        return jsonify({"ok": False, "msg": f"服务脚本不存在：{script}"})
    import os
    env = dict(os.environ)
    env["HFKIT_SERVE_PORT"] = str(port)
    log = LOG_FILE.open("a", encoding="utf-8")
    flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS if __import__("sys").platform == "win32" else 0
    proc = subprocess.Popen([str(PY_EXE), str(script)], cwd=str(ROOT), env=env,
                            stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
    write_pid(proc.pid)
    for _ in range(30):
        if port_open(port):
            return jsonify({"ok": True, "pid": proc.pid, "port": port})
        if not pid_alive(proc.pid):
            return jsonify({"ok": False, "msg": "进程提前退出，请查看日志"})
        import time as _t
        _t.sleep(1)
    return jsonify({"ok": True, "pid": proc.pid, "port": port, "msg": "已启动，仍在加载"})


@app.route("/api/stop", methods=["POST"])
def api_stop():
    pid = read_pid()
    stopped = False
    if pid and pid_alive(pid):
        stopped = kill_pid(pid)
    clear_pid()
    return jsonify({"ok": stopped or pid is None, "stopped_pid": pid})


@app.route("/api/docs")
def api_docs():
    docs = []
    if NOTES.exists():
        for p in sorted(NOTES.glob("*.md")):
            docs.append({"name": p.stem, "content": p.read_text(encoding="utf-8", errors="replace")})
    return jsonify({"docs": docs})


def _preflight():
    """启动前预检：智能选端口（原服务自动关闭 / 其它程序顺延），失败给中文提示。"""
    if not PY_EXE.exists():
        print(f"\n  [解释器缺失] {PY_EXE}", flush=True)
        print("  请修改 config.py 的 env.python_exe。\n", flush=True)
        return None
    import os as _os
    preset = _os.environ.get("HFKIT_WEB_PORT")
    if preset and preset.isdigit():
        # CLI 已完成端口决策，直接采用，避免二次决策把顺延端口再次 +1
        return int(preset)
    port, action, killed = pick_web_port(WEB_PORT)
    if not port:
        print(f"\n  [端口耗尽] {WEB_PORT} 起的 20 个端口都被占用，无法启动。", flush=True)
        print("  请手动结束占用进程，或在 config.py 调整 web_port。\n", flush=True)
        return None
    if action == "reused":
        print(f"  → 已关闭上次的 Web（PID {killed}），复用端口 {port}", flush=True)
    elif action == "shifted":
        print(f"  → 端口顺延，改用 {port}（配置端口 {WEB_PORT} 被其它程序占用）", flush=True)
    return port


if __name__ == "__main__":
    active = _preflight()
    if not active:
        raise SystemExit(1)
    ACTIVE_PORT = active
    write_web_port(active)
    print(f"[{SHORT}-web] {P['name']} http://127.0.0.1:{ACTIVE_PORT}", flush=True)
    threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{ACTIVE_PORT}")).start()
    _load_cache_sizes()            # 先读上次结果，面板秒出真实数值
    threading.Thread(target=lambda: (time.sleep(1), _compute_cache_sizes_async()),
                     daemon=True).start()  # 启动即后台开算，不等用户打开面板
    app.run(host="127.0.0.1", port=ACTIVE_PORT, threaded=True, debug=False, use_reloader=False)
