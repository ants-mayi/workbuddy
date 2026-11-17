# -*- coding: utf-8 -*-
"""
core.py —— 通用引擎的公共基础（与主题无关，全部读 config.PROFILE）
提供：路径解析 / 版本探测(合并+缓存) / 子进程探测 / 进程管理 / 端口 / 渲染 / CSV / 磁盘
"""
import csv
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# ── 定位项目根：engine/ 的上级 = 生成后的项目根 ──────────────────
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# ── 载入配置（项目根下的 config.py）─────────────────────────────
sys.path.insert(0, str(ROOT))
import config as _cfg  # noqa: E402
P = _cfg.PROFILE

console = Console()


def _resolve(p):
    """相对路径按项目根解析，绝对路径原样返回。"""
    q = Path(str(p).replace("\\", "/"))
    return q if q.is_absolute() else ROOT / q


# ── 由配置派生的常量（须在 _resolve 定义之后）───────────────────
SHORT = P["name"] and P["short"]


def _pick_py_exe():
    """跨平台解释器选择：
    - 配置的解释器存在 → 直接用；
    - 配置的是 Windows 路径（盘符/.exe）但当前不是 Windows → 兜底用当前解释器，
      使同一份 config 拷到 mac/linux 也能跑（config 内对应平台请填真实路径）。"""
    cfg = P["env"].get("python_exe") or ""
    if not cfg:
        return Path(sys.executable)
    q = Path(cfg.replace("\\", "/"))
    if q.is_absolute() and q.exists():
        return q
    looks_win = (":" in cfg) or cfg.lower().endswith(".exe")
    if looks_win and os.name != "nt":
        return Path(sys.executable)
    return q


PY_EXE = _pick_py_exe()


def path(key, *sub):
    """取 paths 里的路径，可追加子路径。"""
    base = _resolve(P["paths"][key])
    return base.joinpath(*sub) if sub else base


PROJ = path("project")
EXP = path("artifacts")
DATA = path("data")
NOTES = path("notes")
WEB = path("web")
_cache_val = P["paths"].get("cache", "")
HF_HOME = path("cache") if _cache_val else None   # 未配置缓存时为 None
SERVE_PORT = int(P["serve"]["port"]) if P["serve"]["enabled"] else None
WEB_PORT = int(P["web_port"])

# 服务脚本 / PID / 日志
SERVE_SCRIPT = _resolve(P["serve"]["script"]) if P["serve"].get("script") else None
PID_FILE = HERE / ".serve.pid"
LOG_FILE = HERE / "serve.log"

# ── 渲染小工具 ───────────────────────────────────────────────────
def rule(title=""):
    console.rule(f"[bold cyan]{title}[/bold cyan]" if title else "")


def ok(t):
    return f"[green]✓[/green] {t}"


def warn(t):
    return f"[yellow]![/yellow] {t}"


def bad(t):
    return f"[red]✗[/red] {t}"


def file_size_mb(p):
    p = Path(p)
    if p.is_file():
        return p.stat().st_size / 1024 ** 2
    return None


def assert_interpreter():
    """解释器缺失时给出明确提示，不静默改用 sys.executable。"""
    if not PY_EXE.exists():
        console.print(bad(f"配置的解释器不存在：{PY_EXE}"))
        console.print("  请先修改 config.py 的 env.python_exe，指向装有依赖的 Python。")
        return False
    return True


# ── 子进程探测 ───────────────────────────────────────────────────
def py_probe(code, timeout=60, cwd=None):
    """用配置的解释器在安全目录执行探测代码，返回 stdout；失败返回 None。"""
    try:
        return subprocess.check_output(
            [str(PY_EXE), "-c", code],
            cwd=str(cwd or ROOT.parent), stderr=subprocess.DEVNULL,
            text=True, timeout=timeout,
        ).strip()
    except Exception:
        return None


# ── 合并版本探测（单进程，按配置顺序，含缓存）────────────────────
_VERSIONS_CACHE = None


def get_versions(force=False):
    """一次性探测所有版本 + GPU，返回 dict。Web 常驻服务首次探测后复用。

    本机 pyarrow 有导入竞态：datasets 必须先于 torch import。config 里
    env.versions 的顺序即 import 顺序，引擎严格按序拼接，不重排。
    """
    global _VERSIONS_CACHE
    if _VERSIONS_CACHE is not None and not force:
        return _VERSIONS_CACHE

    specs = P["env"]["versions"]
    gpu = P["env"].get("gpu", {})
    # 拼一个子进程脚本：每条 probe 自身 print 版本，用标记行包裹以便切分。
    # 严格按 config 顺序拼接（datasets 必须先于 torch），不重排。
    parts = []
    for i, spec in enumerate(specs):
        parts.append(f"print('__MARK{i}__')")
        parts.append(spec["probe"])
    if gpu.get("probe"):
        parts.append("print('__MARKGPU__')")
        parts.append(gpu["probe"])
        parts.append("print('__MARKGPUNAME__')")
        parts.append(gpu["name_probe"])

    code = "\n".join(parts)
    out = py_probe(code, cwd=ROOT.parent)
    result = {"versions": {}, "cuda": None, "gpu": None}

    if out:
        chunks = out.split("__MARK")
        # 解析：每段形如 "0__\n<value>\n"
        blocks = {}
        for ch in chunks:
            if "__" not in ch:
                continue
            key, _, val = ch.partition("__")
            blocks[key.strip()] = val.strip().splitlines()[0].strip() if val.strip() else "-"
        for i, spec in enumerate(specs):
            result["versions"][spec["label"]] = blocks.get(str(i), "-")
        if gpu.get("probe"):
            result["cuda"] = blocks.get("GPU", "-") == "TRUE"
            result["gpu"] = blocks.get("GPUNAME", "-")
    else:
        # 降级：逐条独立子进程（慢但稳）
        for spec in specs:
            result["versions"][spec["label"]] = py_probe(spec["probe"]) or "-"
        if gpu.get("probe"):
            result["cuda"] = py_probe(gpu["probe"]) == "TRUE"
            result["gpu"] = py_probe(gpu.get("name_probe", "")) if gpu.get("name_probe") else None

    _VERSIONS_CACHE = result
    return result


# ── 端口 / 进程 ──────────────────────────────────────────────────
def port_open(port, host="127.0.0.1", timeout=0.3):
    if not port:
        return False
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def port_listening(port):
    """端口是否有进程在 LISTEN（不限 127.0.0.1——服务可能只绑具体网卡/IPv6）。
    macOS/Linux 用 lsof；Windows 用 netstat 解析。失败时退回 port_open。"""
    try:
        if os.name != "nt":
            r = subprocess.run(["lsof", "-nP", f"-iTCP:{int(port)}", "-sTCP:LISTEN"],
                               capture_output=True, timeout=10)
            if r.returncode == 0 and len(r.stdout.decode(errors="replace").splitlines()) > 1:
                return True
            return False
        r = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, timeout=15)
        for line in r.stdout.decode(errors="replace").splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[1].endswith(f":{int(port)}") and parts[3] == "LISTENING":
                return True
        return False
    except Exception:
        return port_open(port)


def pid_alive(pid):
    if not pid:
        return False
    try:
        if os.name == "nt":
            out = subprocess.check_output(
                ["tasklist", "/FI", f"PID eq {pid}"], text=True,
                stderr=subprocess.DEVNULL,
            )
            return str(pid) in out
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False


def read_pid():
    try:
        return int(PID_FILE.read_text().strip())
    except Exception:
        return None


def write_pid(pid):
    PID_FILE.write_text(str(pid))


def clear_pid():
    try:
        PID_FILE.unlink()
    except Exception:
        pass


def kill_pid(pid):
    if not pid:
        return False
    try:
        if os.name == "nt":
            subprocess.call(["taskkill", "/PID", str(pid), "/T", "/F"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.kill(int(pid), 15)
        return True
    except Exception:
        return False


# ── Web 端口智能选择（占用时：原服务自动关闭 / 其它程序顺延 +1）──
WEB_PORT_FILE = HERE / ".web.port"


def port_owner(port):
    """返回监听 port 的进程 PID；无监听者返回 None。"""
    try:
        import psutil
        for c in psutil.net_connections(kind="inet"):
            if c.status != psutil.CONN_LISTEN or not c.laddr or not c.pid:
                continue
            la = c.laddr
            ip = getattr(la, "ip", None)
            prt = getattr(la, "port", None)
            if prt == int(port) and ip in (None, "127.0.0.1", "0.0.0.0", "::", "::1"):
                return c.pid
    except Exception:
        pass
    # 回退：Windows netstat / macOS·Linux lsof
    try:
        if os.name == "nt":
            out = subprocess.check_output(["netstat", "-ano", "-p", "TCP"], text=True,
                                          stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                f = line.split()
                if len(f) >= 5 and f[3] == "LISTENING" and f[1].endswith(f":{port}"):
                    return int(f[4])
        else:
            out = subprocess.check_output(
                ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"], text=True,
                stderr=subprocess.DEVNULL)
            for line in out.splitlines()[1:]:
                f = line.split()
                if len(f) >= 2 and f[1].isdigit():
                    return int(f[1])
    except Exception:
        pass
    return None


def is_project_web(pid, script_name="web.py"):
    """判断 PID 是否为本项目的 Web 控制台进程（靠命令行+工作目录，不依赖 PID 文件）。"""
    if not pid:
        return False

    def _norm(s):
        return str(s or "").replace("\\", "/").lower().rstrip("/")

    try:
        import psutil
        proc = psutil.Process(int(pid))
        cmdline = _norm(" ".join(proc.cmdline()))
        cwd = _norm(proc.cwd())
        root = _norm(ROOT)
        in_root = cwd == root or cwd.startswith(root + "/")
        return (script_name in cmdline) and (in_root or root in cmdline)
    except Exception:
        return False


def pick_web_port(start=None, max_scan=20, verbose=True):
    """
    智能挑选 Web 端口：
      - 空闲 → 直接用
      - 被本项目旧 Web 占用 → 关闭该旧进程后复用原端口
      - 被其它程序占用 → 端口 +1 继续
    返回 (port, action, killed_pid)；action ∈ free/reused/shifted/full。
    """
    import time as _t
    start = int(start or WEB_PORT)
    for i in range(max_scan):
        port = start + i
        owner = port_owner(port)
        if owner is None:
            return (port, "free" if i == 0 else "shifted", None)
        if is_project_web(owner):
            if verbose:
                print(f"  [端口清理] {port} 被本项目上次启动的 Web 占用（PID {owner}），"
                      f"自动关闭后复用该端口。", flush=True)
            kill_pid(owner)
            for _ in range(20):
                if not pid_alive(owner) and port_owner(port) is None:
                    break
                _t.sleep(0.15)
            return (port, "reused", owner)
        if verbose:
            print(f"  [端口顺延] {port} 被其它程序占用（PID {owner}），尝试 {port + 1} ...", flush=True)
    return (None, "full", None)


def write_web_port(port):
    try:
        WEB_PORT_FILE.write_text(str(port))
    except Exception:
        pass


def read_web_port():
    """读取 Web 实际监听端口；无记录时回退到配置端口。"""
    try:
        return int(WEB_PORT_FILE.read_text().strip())
    except Exception:
        return int(WEB_PORT)


# ── CSV 记录数（字段内换行不算新行）──────────────────────────────
def csv_count(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in csv.DictReader(f))


# ── 磁盘剩余 GB ──────────────────────────────────────────────────
def free_gb(drive=None):
    try:
        return shutil.disk_usage(str(drive or P["env"].get("disk_drive") or "/")).free / 1024 ** 3
    except Exception:
        return None


# ── 服务状态 / 启停（跨平台）────────────────────────────────────
def service_state(item):
    """查询一条服务/常驻进程的状态文本（只读）。
    Windows：Get-Service 查 item['svc']；macOS/Linux：执行 item['probe']（shell）。"""
    import subprocess as _sp
    if item.get("probe"):
        try:
            r = _sp.run(item["probe"], shell=True, capture_output=True, text=True, timeout=20)
            return (r.stdout or "").strip().splitlines()[0] if (r.stdout or "").strip() else "未知"
        except Exception as e:
            return f"查询失败：{e}"
    if os.name == "nt" and item.get("svc"):
        try:
            r = _sp.run(["powershell", "-NoProfile", "-Command",
                         f"(Get-Service -Name '{item['svc']}' -ErrorAction SilentlyContinue).Status"],
                        capture_output=True, text=True, timeout=15)
            return (r.stdout or "").strip().splitlines()[0] if (r.stdout or "").strip() else "未找到"
        except Exception as e:
            return f"查询失败：{e}"
    return "未知"


def service_action(item, action):
    """启停一条服务（调用方须先用 config 白名单校验）。返回 (ok, msg, cmd)。
    Windows：net start/stop <svc>；macOS/Linux：执行 item['start']/item['stop']。"""
    import subprocess as _sp
    if os.name == "nt":
        cmd = f"net {action} {item.get('svc', '')}"
        try:
            r = _sp.run(["cmd", "/c", cmd], capture_output=True, text=True, timeout=40)
            text = ((r.stdout or "") + (r.stderr or "")).strip()
            ok = r.returncode == 0
            msg = text if text else ("操作已提交" if ok else "操作失败")
            if not ok and ("权限" in text or "denied" in text.lower() or "5" == str(r.returncode)):
                msg = "需要管理员权限。请以管理员身份运行终端后执行：" + cmd + "\n" + text
            return ok, msg, cmd
        except Exception as e:
            return False, f"执行失败：{e}；请手动运行 {cmd}", cmd
    cmd = item.get(action, "")
    if not cmd:
        return False, "该服务未配置启动/停止命令，请手动操作", cmd
    try:
        r = _sp.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        ok = r.returncode == 0
        msg = ((r.stdout or "") + (r.stderr or "")).strip() or ("操作已提交" if ok else "操作失败")
        return ok, msg, cmd
    except Exception as e:
        return False, f"执行失败：{e}；请手动运行：{cmd}", cmd


def open_in_file_manager(folder):
    """用系统文件管理器打开目录（Windows 资源管理器 / macOS 访达 / Linux xdg-open）。"""
    import subprocess as _sp
    if os.name == "nt":
        _sp.Popen(["explorer", folder])
    elif sys.platform == "darwin":
        _sp.Popen(["open", folder])
    else:
        _sp.Popen(["xdg-open", folder])
