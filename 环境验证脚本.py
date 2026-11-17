#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本机开发环境 · 三层验证脚本
================================================================
对应《电脑开发环境信息.md》第 21 节「各软件功能验证方法（三层验证法）」。

对每个软件按递进三层做检查：
  ① 功能有没有   —— 软件/命令/库是否安装存在
  ② 环境是否存在 —— 依赖的前置条件（环境变量、PATH、服务、端口、目录、GPU 等）
  ③ 功能是否正常 —— 实际跑一个最小任务（冒烟测试）

用法：
  python 环境验证脚本.py                 # 检查全部（详细）
  python 环境验证脚本.py --summary       # 只看结果矩阵
  python 环境验证脚本.py --only java     # 只检查名称含 java 的软件（忽略大小写）
  python 环境验证脚本.py --layer 1       # 只跑第 1 层
  python 环境验证脚本.py --network       # 额外跑需要联网的 ③ 层检查
  python 环境验证脚本.py --json          # 以 JSON 输出（便于程序处理）

状态：OK 正常 / WARN 警告 / FAIL 失败或未安装 / SKIP 跳过
说明：本脚本只读或写临时文件，不安装软件、不改系统配置。联网检查需显式 --network。
================================================================
"""

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile

# Windows 控制台 UTF-8 输出
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ----------------------------- 状态 -----------------------------
OK, WARN, FAIL, SKIP = "OK", "WARN", "FAIL", "SKIP"
ICON = {OK: "[OK]", WARN: "[!!]", FAIL: "[XX]", SKIP: "[--]"}

HOME = os.path.expanduser("~")  # C:\Users\marco

# 本机关键路径（与文档保持一致；换机后在此集中修改）
P = {
    "java_home": r"D:\wofkIns\jdk-17.0.0.1",
    "maven_home": r"D:\wofkIns\apache-maven-3.9.9",
    "gradle_cache": os.path.join(HOME, ".gradle"),
    "node_root": r"C:\Users\marco\.workbuddy\binaries\node\versions\22.22.2-6",
    "dotnet": r"C:\Program Files\dotnet",
    "python314": r"D:\wofkIns\Python\Python314",
    "conda": r"D:\wofkIns\anaconda3",
    "conda_ai": r"G:\workIns\conda",
    "ai_python": r"G:\workIns\conda\envs\pytorch\python.exe",   # 已装 torch/transformers 的 AI 环境
    "hf_home": r"G:\study\AI\cache\huggingface",
    "vscode": r"D:\softIns\Microsoft VS Code",
    "idea": r"D:\wofkIns\ideaIU-2025.1.win",
    "mysql_root": r"D:\wofkIns\mysql",
    "dbeaver": r"D:\wofkIns\dbeaver-ce-25.1.3-win32.win32.x86_64",
    "postman": r"C:\Users\marco\AppData\Local\Postman",
    "git": r"D:\wofkIns\Git\cmd\git.exe",
    "sunshine": r"D:\softIns\Sunshine",
    "tailscale": r"F:\Game\tailscale",
    "kuli": r"D:\Program Files (x86)\KuliCloud",
    "uu": r"D:\Program Files\Netease\GameViewer",
    "workbuddy": r"D:\softIns\LenovoSoftstore\Install\WorkBuddy",
}

NETWORK = False  # --network 打开


# ----------------------------- 工具函数 -----------------------------
def resolve_cmd(name):
    """解析命令的真实可执行文件：Windows 下 .cmd/.bat 需完整路径。
    返回可直接传给 subprocess 的路径；解析不到则返回原 name。"""
    if os.name != "nt" or os.path.splitext(name)[1]:
        return name
    try:
        r = subprocess.run(["where.exe", name], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            cands = [l.strip() for l in r.stdout.splitlines() if l.strip()]
            # 优先真正的可执行文件扩展名（.exe > .cmd > .bat > 无扩展）
            for ext in (".exe", ".cmd", ".bat"):
                for c in cands:
                    if c.lower().endswith(ext):
                        return c
            return cands[0]
    except Exception:
        pass
    return name


def run(cmd, timeout=25):
    """执行命令，返回 (returncode, stdout+stderr)。自动解析 .cmd/.bat 命令。"""
    if isinstance(cmd, list) and cmd:
        cmd = [resolve_cmd(cmd[0])] + list(cmd[1:])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 127, "command not found"
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except OSError as ex:
        return 126, str(ex)


def first_line(cmd_args, timeout=25):
    """执行命令，返回首行；失败返回空串。"""
    rc, out = run(cmd_args, timeout)
    return out.splitlines()[0].strip() if rc == 0 and out else ""


def which(name):
    """在 PATH 中查找命令（Windows where.exe）。"""
    rc, out = run(["where.exe", name])
    if rc == 0 and out:
        return out.splitlines()[0].strip()
    return ""


def exists(path):
    return os.path.exists(os.path.expandvars(path))


def py(code, timeout=60):
    """用当前 Python 解释器执行一段代码（-c）。"""
    return run([sys.executable, "-c", code], timeout)


def aipy(code, timeout=120):
    """用 G 盘 pytorch Conda 环境执行 AI 库检查（torch/transformers 装在此环境，
    不在 PATH 默认解释器里）。若该环境不存在，回退到当前解释器。"""
    exe = P["ai_python"] if os.path.isfile(P["ai_python"]) else sys.executable
    return run([exe, "-c", code], timeout)


def pymod(mod, *args, timeout=60):
    """用当前 Python 解释器执行模块（-m mod args），如 -m pip list。"""
    return run([sys.executable, "-m", mod, *args], timeout)


def port_open(port, host="127.0.0.1", timeout=0.5):
    """TCP 端口是否有服务监听。"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def service_state(name):
    """查询 Windows 服务状态（ctypes 调用 Windows 服务 API，无需外部命令/管理员）。"""
    try:
        import ctypes
        from ctypes import wintypes
        advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
        SC_MANAGER_CONNECT = 0x0001
        SERVICE_QUERY_STATUS = 0x0004
        # 64 位下必须显式声明，否则句柄被截断
        advapi32.OpenSCManagerW.restype = wintypes.SC_HANDLE
        advapi32.OpenSCManagerW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
        advapi32.OpenServiceW.restype = wintypes.SC_HANDLE
        advapi32.OpenServiceW.argtypes = [wintypes.SC_HANDLE, wintypes.LPCWSTR, wintypes.DWORD]
        advapi32.CloseServiceHandle.argtypes = [wintypes.SC_HANDLE]
        advapi32.QueryServiceStatus.argtypes = [wintypes.SC_HANDLE, ctypes.c_void_p]
        advapi32.QueryServiceStatus.restype = wintypes.BOOL
        scm = advapi32.OpenSCManagerW(None, None, SC_MANAGER_CONNECT)
        if not scm:
            return "UNKNOWN"
        try:
            svc = advapi32.OpenServiceW(scm, name, SERVICE_QUERY_STATUS)
            if not svc:
                return "NOT_FOUND"
            try:
                class SERVICE_STATUS(ctypes.Structure):
                    _fields_ = [
                        ("dwServiceType", wintypes.DWORD),
                        ("dwCurrentState", wintypes.DWORD),
                        ("dwControlsAccepted", wintypes.DWORD),
                        ("dwWin32ExitCode", wintypes.DWORD),
                        ("dwServiceSpecificExitCode", wintypes.DWORD),
                        ("dwCheckPoint", wintypes.DWORD),
                        ("dwWaitHint", wintypes.DWORD),
                    ]
                st = SERVICE_STATUS()
                ok = advapi32.QueryServiceStatus(svc, ctypes.byref(st))
                if not ok:
                    return "UNKNOWN"
                return {1: "STOPPED", 2: "START_PENDING", 3: "STOP_PENDING",
                        4: "RUNNING", 5: "CONTINUE_PENDING", 6: "PAUSE_PENDING",
                        7: "PAUSED"}.get(st.dwCurrentState, "UNKNOWN")
            finally:
                advapi32.CloseServiceHandle(svc)
        finally:
            advapi32.CloseServiceHandle(scm)
    except Exception:
        return "UNKNOWN"


def fmt(st, msg):
    return (st, msg)


def need_net():
    """联网检查开关：关闭时统一 SKIP。"""
    return fmt(SKIP, "需联网验证，加 --network 启用")


# ------------------------- 各软件的三层检查 -------------------------
# 每个函数返回 (status, message)

# ---- 3 Java ----
def java_l1():
    j, jc = which("java"), which("javac")
    if j and jc:
        return fmt(OK, "java + javac 均在 PATH")
    return fmt(FAIL, "java/javac 不在 PATH")
def java_l2():
    v = os.environ.get("JAVA_HOME", "")
    return fmt(OK, "JAVA_HOME=" + v) if v and exists(v) else fmt(FAIL, "JAVA_HOME 未设或路径无效")
def java_l3():
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "T.java")
        with open(src, "w", encoding="utf-8") as f:
            f.write('public class T{public static void main(String[] a){System.out.println("OK");}}')
        rc1, _ = run(["javac", "-encoding", "UTF-8", src])
        if rc1 != 0:
            return fmt(FAIL, "javac 编译失败")
        rc2, out = run(["java", "-cp", d, "T"])
        return fmt(OK, "编译+运行成功，输出 " + out) if rc2 == 0 and "OK" in out else fmt(FAIL, "运行失败")

# ---- 4 Maven ----
def maven_l1():
    return fmt(OK, "mvn 在 PATH") if which("mvn") else fmt(FAIL, "mvn 不在 PATH")
def maven_l2():
    # 2026-11-17 修正：本机全局 conf/settings.xml 已指定 localRepository 为 G 盘
    repo = r"G:\workIns\LocalWareHouse"
    return fmt(OK, "本地仓库存在(G:\\workIns\\LocalWareHouse)") if exists(repo) else fmt(WARN, "生效仓库不存在（检查 conf/settings.xml 的 localRepository）")
def maven_l3():
    rc, out = run(["mvn", "-version"])
    return fmt(OK, out.splitlines()[0]) if rc == 0 else fmt(FAIL, "mvn 无法启动")

# ---- 5 Gradle ----
def gradle_l1():
    return fmt(OK, "gradle 在 PATH") if which("gradle") else fmt(FAIL, "未安装（不在 PATH）")
def gradle_l2():
    return fmt(OK, "缓存目录存在，可用 wrapper") if exists(P["gradle_cache"]) else fmt(WARN, "无缓存目录")
def gradle_l3():
    return fmt(SKIP, "未安装；建议项目内 ./gradlew build")

# ---- 6 Node ----
def node_l1():
    return fmt(OK, first_line(["node", "-v"])) if which("node") else fmt(FAIL, "node 不在 PATH")
def node_l2():
    return fmt(OK, "NODE 根目录存在") if exists(P["node_root"]) else fmt(WARN, "记录路径不存在，请核对")
def node_l3():
    rc, out = run(["node", "-e", "console.log('OK',process.version)"])
    return fmt(OK, out) if rc == 0 and "OK" in out else fmt(FAIL, "node 执行失败")

# ---- npm ----
def npm_l1():
    return fmt(OK, first_line(["npm", "-v"])) if which("npm") else fmt(FAIL, "npm 不在 PATH")
def npm_l2():
    return fmt(OK, "registry=" + first_line(["npm", "config", "get", "registry"]))
def npm_l3():
    if not NETWORK:
        return need_net()
    rc, out = run(["npm", "view", "lodash", "version"], timeout=40)
    return fmt(OK, "联网取包版本=" + out) if rc == 0 else fmt(FAIL, "联网/仓库异常")

# ---- 19 .NET ----
def dotnet_l1():
    rc, out = run(["dotnet", "--version"])
    if rc == 0:
        return fmt(OK, "SDK " + out)
    if "SDK" in out and "No .NET SDKs" in out:
        return fmt(WARN, "有运行时但无 SDK（无法开发）")
    return fmt(FAIL, "dotnet 不可用")
def dotnet_l2():
    rc, out = run(["dotnet", "--list-runtimes"])
    return fmt(OK, "运行时 " + str(len([l for l in out.splitlines() if l.strip()])) + " 项") if rc == 0 and out else fmt(FAIL, "无运行时")
def dotnet_l3():
    rc, out = run(["dotnet", "--list-sdks"])
    if rc == 0 and not out.strip():
        return fmt(SKIP, "无 SDK，跳过编译验证；装 SDK 后可 dotnet new console && dotnet run")
    return fmt(OK, "SDK 可用") if rc == 0 else fmt(FAIL, "SDK 检查失败")

# ---- 7 Python ----
def python_l1():
    return fmt(OK, first_line(["python", "--version"])) if which("python") else fmt(FAIL, "python 不在 PATH")
def python_l2():
    rc, out = py("import sys;print(sys.executable)")
    return fmt(OK, out) if rc == 0 and out else fmt(FAIL, "无法获取解释器")
def python_l3():
    rc, out = py("import sys,json,math;print('OK',sys.version.split()[0])")
    return fmt(OK, out) if rc == 0 and "OK" in out else fmt(FAIL, "标准库导入失败")

# ---- pip ----
def pip_l1():
    rc, out = pymod("pip", "--version")
    return fmt(OK, out) if rc == 0 else fmt(FAIL, "pip 不可用")
def pip_l2():
    rc, out = run(["pip", "-V"])
    return fmt(WARN, out if rc == 0 else "无法确定 pip 归属")  # 提示：可能与当前 python 不一致
def pip_l3():
    rc, out = pymod("pip", "list", "--format=columns")
    return fmt(OK, "已安装包 " + str(max(0, len(out.splitlines()) - 2)) + " 个") if rc == 0 else fmt(FAIL, "pip list 失败")

# ---- 8 Conda ----
def conda_l1():
    return fmt(OK, first_line(["conda", "--version"])) if which("conda") else fmt(FAIL, "conda 不在 PATH")
def conda_l2():
    rc, out = run(["conda", "info"])
    base = next((l.strip() for l in out.splitlines() if "base environment" in l), "")
    return fmt(OK, base) if rc == 0 and base else fmt(WARN, "conda info 未返回 base 信息")
def conda_l3():
    rc, out = run(["conda", "env", "list"])
    n_path = len([l for l in out.splitlines() if l.strip() and not l.startswith('#')])
    ai_env = "pytorch" if os.path.isfile(P["ai_python"]) else "无"
    extra = " + G 盘另一套 conda（pytorch 环境：" + ai_env + "）" if os.path.isdir(P["conda_ai"]) else ""
    return fmt(OK, "PATH 中 conda 环境 " + str(n_path) + " 个" + extra) if rc == 0 else fmt(FAIL, "env list 失败")

# ---- 9 Ollama ----
def ollama_l1():
    return fmt(OK, first_line(["ollama", "--version"])) if which("ollama") else fmt(FAIL, "未安装（不在 PATH）")
def ollama_l2():
    return fmt(WARN, "端口 11434 未监听（服务未启动）") if not port_open(11434) else fmt(OK, "端口 11434 已监听")
def ollama_l3():
    return fmt(SKIP, "未安装；装后 ollama run <model>")

# ---- 10 HF / Transformers ----
def hf_l1():
    rc, out = aipy("import huggingface_hub,transformers;print(transformers.__version__)")
    return fmt(OK, "库已安装（transformers " + out.strip() + "，AI 环境）") if rc == 0 else fmt(FAIL, "huggingface_hub/transformers 未安装")
def hf_l2():
    h = os.environ.get("HF_HOME", "")
    e = os.environ.get("HF_ENDPOINT", "")
    return fmt(OK, "HF_HOME=" + h + "; HF_ENDPOINT=" + e) if h and e else fmt(WARN, "HF_HOME/HF_ENDPOINT 未完整设置")
def hf_l3():
    if not NETWORK:
        return need_net()
    rc, out = aipy("from huggingface_hub import HfApi;print(HfApi().list_models(limit=1))")
    return fmt(OK, "HF API 可访问") if rc == 0 else fmt(FAIL, "HF 访问失败")

# ---- 20 PyTorch ----
def torch_l1():
    rc, out = aipy("import torch;print(torch.__version__)")
    return fmt(OK, "torch " + out.strip() + "（AI 环境）") if rc == 0 else fmt(FAIL, "torch 未安装（AI 环境亦未检测到）")
def torch_l2():
    rc, out = run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
    return fmt(OK, "GPU " + out.replace("\n", "; ")) if rc == 0 and out else fmt(WARN, "未检测到 NVIDIA GPU / nvidia-smi")
def torch_l3():
    rc, out = aipy("import torch;print(torch.__version__);print('CUDA',torch.cuda.is_available());print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NA')")
    return fmt(OK, out.replace("\n", "; ")) if rc == 0 else fmt(SKIP, "torch 未安装，跳过 GPU 冒烟")

# ---- 11 Docker ----
def docker_l1():
    return fmt(OK, first_line(["docker", "--version"])) if which("docker") else fmt(FAIL, "未安装（不在 PATH）")
def docker_l2():
    return fmt(SKIP, "安装后检查 WSL2 后端")
def docker_l3():
    return fmt(SKIP, "未安装；装后 docker run --rm hello-world")

# ---- 12 VSCode ----
def vscode_l1():
    return fmt(OK, first_line(["code", "--version"])) if which("code") else fmt(FAIL, "code 不在 PATH")
def vscode_l2():
    return fmt(OK, "安装目录存在") if exists(P["vscode"]) else fmt(WARN, "记录路径不存在")
def vscode_l3():
    rc, out = run(["code", "--list-extensions"])
    return fmt(OK, "扩展 " + str(len(out.splitlines())) + " 个") if rc == 0 else fmt(WARN, "无法列出扩展")

# ---- 14 IDEA ----
def idea_l1():
    exe = os.path.join(P["idea"], "bin", "idea64.exe")
    return fmt(OK, "idea64.exe 存在") if exists(exe) else fmt(FAIL, "idea64.exe 未找到")
def idea_l2():
    return fmt(OK, "安装目录存在") if exists(P["idea"]) else fmt(WARN, "记录路径不存在")
def idea_l3():
    return fmt(SKIP, "GUI 程序需人工启动验证（新建 Maven 项目运行 main）")

# ---- 13 MySQL ----
def mysql_l1():
    found = []
    root = P["mysql_root"]
    if os.path.isdir(root):
        for d in os.listdir(root):
            exe = os.path.join(root, d, "bin", "mysql.exe")
            if exists(exe):
                found.append(d)
    return fmt(OK, "找到 " + str(len(found)) + " 套: " + ", ".join(found)) if found else fmt(FAIL, "未找到 mysql.exe")
def mysql_l2():
    states = "MySQL=" + service_state("MySQL") + ", mysql80=" + service_state("mysql80")
    listening = "3306" if port_open(3306) else ("3307" if port_open(3307) else "无")
    return fmt(WARN, states + "; 监听端口=" + listening)
def mysql_l3():
    if not (port_open(3306) or port_open(3307)):
        return fmt(SKIP, "服务未启动；启动后 SELECT VERSION() 验证")
    return fmt(SKIP, "服务已启动，请连库执行 SELECT VERSION()")

# ---- 17 DBeaver ----
def dbeaver_l1():
    exe = os.path.join(P["dbeaver"], "dbeaver", "dbeaver.exe")
    return fmt(OK, "dbeaver.exe 存在") if exists(exe) else fmt(FAIL, "dbeaver.exe 未找到")
def dbeaver_l2():
    data = os.path.join(HOME, "AppData", "Roaming", "DBeaverData")
    return fmt(OK, "DBeaverData 存在") if exists(data) else fmt(WARN, "数据目录不存在")
def dbeaver_l3():
    exe = os.path.join(P["dbeaver"], "dbeaver", "dbeaver-cli.exe")
    if not exists(exe):
        return fmt(SKIP, "无 dbeaver-cli")
    rc, out = run([exe, "--help"])
    return fmt(OK, "dbeaver-cli 可运行") if rc == 0 else fmt(WARN, "dbeaver-cli 启动异常")

# ---- Postman ----
def postman_l1():
    return fmt(OK, "Postman.exe 存在") if exists(os.path.join(P["postman"], "Postman.exe")) else fmt(FAIL, "Postman.exe 未找到")
def postman_l2():
    data = os.path.join(HOME, "AppData", "Roaming", "Postman")
    return fmt(OK, "配置目录存在") if exists(data) else fmt(WARN, "配置目录不存在")
def postman_l3():
    if not NETWORK:
        return need_net()
    rc, out = py("import urllib.request;print(urllib.request.urlopen('https://postman-echo.com/get',timeout=8).status)")
    return fmt(OK, "HTTP " + out) if rc == 0 else fmt(FAIL, "联网请求失败")

# ---- 16 Git ----
def git_l1():
    return fmt(OK, first_line(["git", "--version"])) if which("git") else fmt(FAIL, "git 不在 PATH")
def git_l2():
    u = first_line(["git", "config", "--global", "user.name"])
    return fmt(OK, "user.name=" + u) if u else fmt(WARN, "未配置 user.name")
def git_l3():
    with tempfile.TemporaryDirectory() as d:
        run(["git", "init", "-q", d])
        rc, out = run(["git", "-C", d, "status", "--short"])
        return fmt(OK, "git init/status 正常") if rc == 0 else fmt(FAIL, "git 操作失败")

# ---- 15 端口一览 ----
def port_l1():
    return fmt(OK, "端口检测能力可用")  # Python socket 可用即代表
def port_l2():
    checks = [(11434, "Ollama"), (3306, "MySQL"), (3307, "MySQL-8"),
              (8080, "Web"), (3000, "前端"), (47990, "Sunshine")]
    listening = [f"{p}({n})" for p, n in checks if port_open(p)]
    return fmt(OK, "监听中: " + ", ".join(listening)) if listening else fmt(WARN, "常见开发端口均未监听")
def port_l3():
    return fmt(SKIP, "端口连通性已在 ② 层用 socket 实测")

# ---- 18.2 Sunshine ----
def sunshine_l1():
    return fmt(OK, "sunshine.exe 存在") if exists(os.path.join(P["sunshine"], "sunshine.exe")) else fmt(FAIL, "未找到")
def sunshine_l2():
    st = service_state("SunshineService")
    port = "47990 已监听" if port_open(47990) else "47990 未监听"
    return fmt(OK, "服务=" + st + "; " + port)
def sunshine_l3():
    if not port_open(47990):
        return fmt(SKIP, "端口未监听")
    rc, out = py("import urllib.request,ssl;c=ssl._create_unverified_context();print(urllib.request.urlopen('https://127.0.0.1:47990',context=c,timeout=5).status)")
    return fmt(OK, "管理页 HTTP " + out) if rc == 0 else fmt(WARN, "端口在但 HTTP 探测失败")

# ---- 18.3 Tailscale ----
def tailscale_l1():
    return fmt(OK, "tailscale.exe 存在") if exists(os.path.join(P["tailscale"], "tailscale.exe")) else fmt(FAIL, "未找到")
def tailscale_l2():
    st = service_state("Tailscale")
    return fmt(OK, "服务=" + st) if st == "RUNNING" else fmt(WARN, "服务=" + st)
def tailscale_l3():
    exe = os.path.join(P["tailscale"], "tailscale.exe")
    rc, out = run([exe, "status"], timeout=20)
    return fmt(OK, "节点 " + str(len(out.splitlines())) + " 个") if rc == 0 and out else fmt(WARN, "status 读取失败")

# ---- 18.1 / 18.4 常驻软件（kuli云、UU远程、WorkBuddy、千问、豆包、TRAE）----
def make_desktop_checks(name, path_key, exe_rel=""):
    def l1():
        base = P[path_key]
        target = os.path.join(base, exe_rel) if exe_rel else base
        return fmt(OK, "程序路径存在") if exists(target) else fmt(WARN, "路径需核对")
    def l2():
        return fmt(OK, "安装目录存在") if exists(P[path_key]) else fmt(WARN, "目录不存在")
    def l3():
        return fmt(SKIP, name + " 为 GUI 程序，需人工登录/发起一次请求验证")
    return l1, l2, l3

kuli_l1, kuli_l2, kuli_l3 = make_desktop_checks("kuli云", "kuli", "KuliCloud.exe")
uu_l1, uu_l2, uu_l3 = make_desktop_checks("UU远程", "uu")
wb_l1, wb_l2, wb_l3 = make_desktop_checks("WorkBuddy", "workbuddy", "WorkBuddy.exe")


# ----------------------------- 检查清单 -----------------------------
# (类别, 名称, L1, L2, L3)
CHECKS = [
    ("编程语言与构建", "Java (JDK)", java_l1, java_l2, java_l3),
    ("编程语言与构建", "Maven", maven_l1, maven_l2, maven_l3),
    ("编程语言与构建", "Gradle", gradle_l1, gradle_l2, gradle_l3),
    ("编程语言与构建", "Node.js", node_l1, node_l2, node_l3),
    ("编程语言与构建", "npm", npm_l1, npm_l2, npm_l3),
    ("编程语言与构建", ".NET", dotnet_l1, dotnet_l2, dotnet_l3),
    ("Python 与 AI", "Python", python_l1, python_l2, python_l3),
    ("Python 与 AI", "pip", pip_l1, pip_l2, pip_l3),
    ("Python 与 AI", "Conda", conda_l1, conda_l2, conda_l3),
    ("Python 与 AI", "Ollama", ollama_l1, ollama_l2, ollama_l3),
    ("Python 与 AI", "HF/Transformers", hf_l1, hf_l2, hf_l3),
    ("Python 与 AI", "PyTorch", torch_l1, torch_l2, torch_l3),
    ("Python 与 AI", "Docker", docker_l1, docker_l2, docker_l3),
    ("IDE/数据库/接口", "VSCode", vscode_l1, vscode_l2, vscode_l3),
    ("IDE/数据库/接口", "IntelliJ IDEA", idea_l1, idea_l2, idea_l3),
    ("IDE/数据库/接口", "MySQL", mysql_l1, mysql_l2, mysql_l3),
    ("IDE/数据库/接口", "DBeaver", dbeaver_l1, dbeaver_l2, dbeaver_l3),
    ("IDE/数据库/接口", "Postman", postman_l1, postman_l2, postman_l3),
    ("IDE/数据库/接口", "Git", git_l1, git_l2, git_l3),
    ("端口/网络/常驻", "端口占用", port_l1, port_l2, port_l3),
    ("端口/网络/常驻", "Sunshine", sunshine_l1, sunshine_l2, sunshine_l3),
    ("端口/网络/常驻", "Tailscale", tailscale_l1, tailscale_l2, tailscale_l3),
    ("端口/网络/常驻", "kuli云", kuli_l1, kuli_l2, kuli_l3),
    ("端口/网络/常驻", "UU远程", uu_l1, uu_l2, uu_l3),
    ("端口/网络/常驻", "WorkBuddy", wb_l1, wb_l2, wb_l3),
]

LAYER_NAME = {1: "功能有没有", 2: "环境是否存在", 3: "功能是否正常"}


def do_checks(only=None, layer=None):
    results = []
    for cat, name, l1, l2, l3 in CHECKS:
        if only and only.lower() not in (cat + " " + name).lower():
            continue
        layers = []
        for idx, fn in enumerate((l1, l2, l3), start=1):
            if layer and idx != layer:
                layers.append((SKIP, "未选中该层"))
            else:
                try:
                    layers.append(fn())
                except Exception as ex:  # 单个检查异常不影响整体
                    layers.append((FAIL, "检查异常: " + str(ex)))
        results.append((cat, name, layers))
    return results


def print_detail(results):
    cur = None
    for cat, name, layers in results:
        if cat != cur:
            print("\n" + "=" * 64)
            print("【" + cat + "】")
            print("=" * 64)
            cur = cat
        print("▶ " + name)
        for i, (st, msg) in enumerate(layers, start=1):
            print("   " + ICON[st] + " " + str(i) + "层(" + LAYER_NAME[i] + "): " + msg)
    print_summary(results)


def print_summary(results):
    print("\n" + "=" * 64)
    print("结果矩阵（①功能 ②环境 ③正常）")
    print("=" * 64)
    print("%-18s %-6s %-6s %-6s" % ("软件", "①", "②", "③"))
    print("-" * 64)
    counts = {OK: 0, WARN: 0, FAIL: 0, SKIP: 0}
    for _, name, layers in results:
        print("%-18s %-6s %-6s %-6s" % (name, *[ICON[s] for s, _ in layers]))
        for s, _ in layers:
            counts[s] += 1
    print("-" * 64)
    print("统计: OK=%d  WARN=%d  FAIL=%d  SKIP=%d" %
          (counts[OK], counts[WARN], counts[FAIL], counts[SKIP]))
    print("说明: FAIL 多为未安装或需人工/联网验证；详见详细输出与各章节。")


def to_json(results):
    out = []
    for cat, name, layers in results:
        out.append({
            "category": cat, "name": name,
            "layers": [
                {"layer": i, "name": LAYER_NAME[i], "status": st, "message": msg}
                for i, (st, msg) in enumerate(layers, start=1)
            ],
        })
    return json.dumps(out, ensure_ascii=False, indent=2)


def main():
    global NETWORK
    ap = argparse.ArgumentParser(description="本机开发环境三层验证脚本")
    ap.add_argument("--summary", action="store_true", help="只输出结果矩阵")
    ap.add_argument("--only", metavar="KEY", help="只检查名称/类别含 KEY 的软件")
    ap.add_argument("--layer", type=int, choices=[1, 2, 3], help="只运行指定层")
    ap.add_argument("--network", action="store_true", help="启用需要联网的 ③ 层检查")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = ap.parse_args()
    NETWORK = args.network

    results = do_checks(args.only, args.layer)
    if not results:
        print("没有匹配的软件。可用名称见文档第 21 节或用 --only 换关键词。")
        return
    if args.json:
        print(to_json(results))
    elif args.summary:
        print_summary(results)
    else:
        print_detail(results)


if __name__ == "__main__":
    main()
