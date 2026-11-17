#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect_mac.py — 环境控制台 Mac 端只读采集脚本
================================================
用途：在 macOS 上采集生成 PROFILE_MAC 所需的全部事实数据。
     只读操作，不修改任何系统设置，不安装任何东西。

运行方式（终端执行，或在 Mac 的 WorkBuddy 里让它执行）：
    python3 collect_mac.py

产出（脚本同目录下）：
    mac_profile.json   — 完整原始数据（带回给 Windows 侧用于生成配置）
    mac_profile.txt    — 人类可读摘要（可自行浏览核对）

依赖：仅 Python 标准库；若已 pip 安装 psutil 则端口/进程信息更完整（可选）。
耗时：约 10~30 秒。
"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime

OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mac_profile.json")
OUT_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mac_profile.txt")
R = {}  # 汇总结果


def run(cmd, timeout=15):
    """执行命令，返回 (stdout, stderr, returncode)。任何失败都不抛异常。"""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.stdout.strip(), p.stderr.strip(), p.returncode
    except Exception as e:
        return "", f"{type(e).__name__}: {e}", -1


def have(cmd):
    return shutil.which(cmd)


def which_all(cmd):
    """等价于 `which -a`：PATH 上该命令的所有候选。"""
    out, _, _ = run(["which", "-a", cmd])
    return [l for l in out.splitlines() if l.strip()] if out else []


def collect_system():
    d = {}
    out, _, _ = run(["sw_vers"])
    for line in out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    d["kernel"] = platform.release()
    d["arch"] = platform.machine()  # arm64 / x86_64
    out, _, _ = run(["uname", "-m"])
    d["uname_m"] = out
    out, _, _ = run(["scutil", "--get", "ComputerName"])
    d["computer_name"] = out  # 局域网/AirDrop 显示名，远程访问关心
    out, _, _ = run(["xcode-select", "-p"])
    d["xcode_clt"] = out or "未安装"  # 系统工具链（clang/git 头文件）
    # 芯片与内存
    out, _, _ = run(["sysctl", "-n", "machdep.cpu.brand_string"])
    d["cpu_brand"] = out or "(Apple Silicon 无此键，见 model)"
    out, _, _ = run(["sysctl", "-n", "hw.model"])
    d["hw_model"] = out
    out, _, _ = run(["sysctl", "-n", "hw.memsize"])
    try:
        d["memory_gb"] = round(int(out) / 1024**3, 1)
    except Exception:
        d["memory_gb"] = None
    out, _, _ = run(["sysctl", "-n", "hw.ncpu"])
    d["cpu_cores"] = out
    # 磁盘总览
    out, _, _ = run(["df", "-h", "/"])
    d["df_root"] = out
    R["system"] = d


DEV_CMDS = [
    "python3", "python", "pip3", "conda", "git", "node", "npm", "npx",
    "java", "javac", "mvn", "gradle", "docker", "docker-compose",
    "mysql", "redis-server", "nginx", "go", "rustc", "cargo",
    "code", "brew", "tail", "curl", "wget", "ssh", "ffmpeg", "ollama",
    "deno", "uv", "tailscale",
]


def collect_tools():
    tools = {}
    for c in DEV_CMDS:
        entry = {"path": have(c), "all_candidates": which_all(c) if have(c) else []}
        # 逐个取版本（命令各自的版本参数）
        if entry["path"]:
            vcmd = {
                "java": ["java", "-version"], "javac": ["javac", "-version"],
                "node": ["node", "-v"], "npm": ["npm", "-v"], "npx": ["npx", "-v"],
                "git": ["git", "--version"], "mvn": ["mvn", "-v"], "gradle": ["gradle", "-v"],
                "docker": ["docker", "--version"], "docker-compose": ["docker", "compose", "version"],
                "mysql": ["mysql", "--version"], "conda": ["conda", "--version"],
                "python3": ["python3", "--version"], "pip3": ["pip3", "--version"],
                "go": ["go", "version"], "rustc": ["rustc", "--version"],
                "code": ["code", "--version"], "brew": ["brew", "--version"],
                "ollama": ["ollama", "--version"], "ffmpeg": ["ffmpeg", "-version"],
                "deno": ["deno", "--version"], "uv": ["uv", "--version"],
                "tailscale": ["tailscale", "version"],
            }.get(c)
            if vcmd:
                out, err, _ = run(vcmd, timeout=30)
                first = (out or err).splitlines()[0] if (out or err) else ""
                # java/mvn/gradle 输出多行，保留前几行
                entry["version"] = "\n".join((out or err).splitlines()[:4]) or first
        tools[c] = entry
    R["tools"] = tools


def collect_python_envs():
    """找出所有 Python 解释器及其是否带 flask / psutil。"""
    candidates = which_all("python3") + which_all("python")
    # 常见安装位置补充
    for p in [
        "/usr/bin/python3", "/usr/local/bin/python3", "/opt/homebrew/bin/python3",
        os.path.expanduser("~/miniconda3/bin/python"), os.path.expanduser("~/anaconda3/bin/python"),
        os.path.expanduser("~/miniforge3/bin/python"), "/opt/homebrew/Caskroom/miniconda/base/bin/python",
    ]:
        if os.path.exists(p) and p not in candidates:
            candidates.append(p)
    envs = []
    for py in candidates:
        real = os.path.realpath(py)
        code = ("import sys;info=sys.version.split()[0];"
                "mods=[]\n"
                "for m in ('flask','psutil','requests'):\n"
                "    try:\n        __import__(m);mods.append(m)\n"
                "    except Exception:pass\n"
                "print(info+'|'+','.join(mods))")
        out, _, rc = run([py, "-c", code], timeout=20)
        ver, mods = ("", [])
        if rc == 0 and "|" in out:
            ver, mods = out.split("|")[0], out.split("|")[1].split(",") if out.split("|")[1] else []
        envs.append({"path": py, "realpath": real, "version": ver, "modules": mods})
    # conda 环境列表
    conda = have("conda")
    conda_envs = []
    if conda:
        out, _, _ = run(["conda", "env", "list"], timeout=30)
        for line in out.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                conda_envs.append(line)
    R["python_envs"] = {"candidates": envs, "conda_env_list": conda_envs}


def collect_homebrew():
    if not have("brew"):
        R["homebrew"] = {"installed": False}
        return
    prefix, _, _ = run(["brew", "--prefix"])
    formulas, _, _ = run(["brew", "list", "--formula"], timeout=60)
    casks, _, _ = run(["brew", "list", "--cask"], timeout=60)
    taps, _, _ = run(["brew", "tap"], timeout=30)
    # brew services 状态（用户级，免 sudo）
    svc, _, _ = run(["brew", "services", "list"], timeout=30)
    R["homebrew"] = {
        "installed": True, "prefix": prefix,
        "formulas": [f for f in formulas.splitlines() if f.strip()],
        "casks": [c for c in casks.splitlines() if c.strip()],
        "taps": [t for t in taps.splitlines() if t.strip()],
        "services_raw": svc,
    }


def collect_services():
    """launchctl 用户域服务（免 sudo）+ 系统域仅列名字。"""
    d = {}
    out, _, _ = run(["launchctl", "list"], timeout=20)
    d["user_services_raw"] = out[:4000]
    try:
        uid = os.getuid()
        out, _, _ = run(["launchctl", "print", f"gui/{uid}"], timeout=10)
        d["gui_domain_ok"] = out != "" and "not" not in out.lower()[:200]
    except AttributeError:
        d["gui_domain_ok"] = None  # 非 macOS 平台
    # 用户 LaunchAgents 目录（自启动项）
    la = os.path.expanduser("~/Library/LaunchAgents")
    d["user_launchagents"] = os.listdir(la) if os.path.isdir(la) else []
    R["launchd"] = d


def collect_ports():
    psutil_ok = False
    try:
        import psutil  # noqa
        psutil_ok = True
        conns = []
        for c in psutil.net_connections(kind="inet"):
            if c.status == psutil.CONN_LISTEN and c.laddr:
                pname = ""
                try:
                    pname = psutil.Process(c.pid).name() if c.pid else ""
                except Exception:
                    pass
                conns.append({"port": c.laddr.port, "pid": c.pid, "process": pname})
        seen, uniq = set(), []
        for c in sorted(conns, key=lambda x: x["port"]):
            k = (c["port"], c["pid"])
            if k not in seen:
                seen.add(k); uniq.append(c)
        R["ports"] = {"source": "psutil", "listening": uniq}
    except ImportError:
        out, _, _ = run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"], timeout=20)
        rows = []
        for line in out.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 9 and ":" in parts[8]:
                try:
                    port = int(parts[8].rsplit(":", 1)[1])
                    rows.append({"port": port, "process": parts[0], "pid": parts[1]})
                except ValueError:
                    pass
        R["ports"] = {"source": "lsof", "listening": rows, "psutil_installed": False}


def collect_paths_and_files():
    """常用开发目录 + 常见配置文件存在性。"""
    home = os.path.expanduser("~")
    d = {"home": home}
    for name, p in {
        "Desktop": "~/Desktop", "Documents": "~/Documents", "Downloads": "~/Downloads",
        "Projects(建议工作区)": "~/Projects", "Dev(常见)": "~/Dev", "dev(常见)": "~/dev",
        "Workspace(常见)": "~/Workspace",
    }.items():
        d[f"dir_{name}"] = os.path.isdir(os.path.expanduser(p))
    cfgs = {
        "git_global": "~/.gitconfig", "zshrc": "~/.zshrc", "zprofile": "~/.zprofile",
        "bash_profile": "~/.bash_profile", "ssh_config": "~/.ssh/config",
        "npmrc": "~/.npmrc", "condarc": "~/.condarc", "docker_daemon": "~/.docker/daemon.json",
        "maven_settings(常见位)": "~/.m2/settings.xml", "gradle(常见位)": "~/.gradle/gradle.properties",
    }
    d["config_files"] = {k: {"path": os.path.expanduser(v),
                             "exists": os.path.exists(os.path.expanduser(v))}
                         for k, v in cfgs.items()}
    # 开发人员关心的身份/密钥事实
    out, _, _ = run(["git", "config", "--global", "user.name"])
    d["git_user_name"] = out or "(未设置)"
    out, _, _ = run(["git", "config", "--global", "user.email"])
    d["git_user_email"] = out or "(未设置)"
    ssh = os.path.expanduser("~/.ssh")
    d["ssh_keys"] = [f for f in (os.listdir(ssh) if os.path.isdir(ssh) else [])
                     if f.startswith("id_") and not f.endswith(".pub")]
    R["paths"] = d


def collect_env_vars():
    keys = ["PATH", "HOME", "SHELL", "USER", "LANG", "JAVA_HOME", "MAVEN_HOME", "M2_HOME",
            "GRADLE_HOME", "CONDA_PREFIX", "NVM_DIR", "PYENV_ROOT", "HTTP_PROXY", "HTTPS_PROXY",
            "NO_PROXY", "PIP_INDEX_URL", "HF_HOME", "TRANSFORMERS_CACHE", "DOCKER_HOST"]
    R["env_vars"] = {k: os.environ.get(k, "(未设置)") for k in keys}


def collect_disks():
    out, _, _ = run(["df", "-h"], timeout=15)
    lines = [l for l in out.splitlines()
             if l.startswith("/dev/") or l.startswith("/System/Volumes/") or " / " in l[:40]]
    R["disks_raw"] = "\n".join(lines[:30])


def main():
    print("=" * 60)
    print("环境控制台 Mac 采集脚本（只读）")
    print("=" * 60)
    for fn in (collect_system, collect_tools, collect_python_envs,
               collect_homebrew, collect_services, collect_ports,
               collect_paths_and_files, collect_env_vars, collect_disks):
        name = fn.__name__.replace("collect_", "")
        print(f"· 采集 {name} ...", end=" ", flush=True)
        try:
            fn()
            print("完成")
        except Exception as e:
            R[f"_error_{name}"] = f"{type(e).__name__}: {e}"
            print(f"失败({type(e).__name__})")

    R["_meta"] = {
        "collected_at": datetime.now().isoformat(timespec="seconds"),
        "script_version": "1.0",
        "python_running": sys.version.split()[0],
        "python_path": sys.executable,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)

    # 生成人类可读摘要
    L = []
    L.append("=== 系统 ===")
    s = R.get("system", {})
    L.append(f"macOS {s.get('ProductVersion','?')}  架构 {s.get('arch')}  芯片 {s.get('cpu_brand')}")
    L.append(f"内存 {s.get('memory_gb')}GB  核心数 {s.get('cpu_cores')}  型号 {s.get('hw_model')}")
    L.append(f"根分区: {s.get('df_root','').splitlines()[-1] if s.get('df_root') else '?'}")
    L.append("\n=== 开发工具 ===")
    for k, v in R.get("tools", {}).items():
        if v.get("path"):
            ver = (v.get("version") or "").splitlines()[0] if v.get("version") else ""
            L.append(f"  {k:16s} {v['path']:45s} {ver[:60]}")
        else:
            L.append(f"  {k:16s} 未安装")
    L.append("\n=== Python 环境 ===")
    for e in R.get("python_envs", {}).get("candidates", []):
        mods = ",".join(e["modules"]) or "-"
        L.append(f"  {e['path']:50s} v{e['version'] or '?':8s} [{mods}]")
    ce = R.get("python_envs", {}).get("conda_env_list", [])
    if ce:
        L.append("  conda env list:")
        L += [f"    {x}" for x in ce]
    hb = R.get("homebrew", {})
    L.append("\n=== Homebrew ===")
    if hb.get("installed"):
        L.append(f"  prefix={hb.get('prefix')}  formula={len(hb.get('formulas',[]))}个  cask={len(hb.get('casks',[]))}个")
        L.append(f"  formulas: {', '.join(hb.get('formulas', []))}")
        if hb.get("casks"):
            L.append(f"  casks: {', '.join(hb.get('casks', []))}")
        if hb.get("services_raw"):
            L.append("  services:")
            L += [f"    {x}" for x in hb["services_raw"].splitlines()]
    else:
        L.append("  未安装 Homebrew")
    L.append("\n=== 用户 LaunchAgents(自启动) ===")
    L.append("  " + (", ".join(R.get("launchd", {}).get("user_launchagents", [])) or "(空)"))
    L.append("\n=== 监听端口 ===")
    p = R.get("ports", {})
    for x in p.get("listening", [])[:40]:
        L.append(f"  :{x['port']:6d} pid={x.get('pid','-')} {x.get('process','')}")
    L.append("\n=== 关键配置文件 ===")
    for k, v in R.get("paths", {}).get("config_files", {}).items():
        L.append(f"  [{'有' if v['exists'] else '无'}] {k}: {v['path']}")
    L.append("\n=== 环境变量 ===")
    for k, v in R.get("env_vars", {}).items():
        L.append(f"  {k} = {v[:120]}")
    txt = "\n".join(L)
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write(txt)

    print("\n" + "=" * 60)
    print("采集完成！产出：")
    print(f"  {OUT_JSON}   <- 请把这个文件带回给 Windows 侧")
    print(f"  {OUT_TXT}   <- 人类可读摘要")
    print("=" * 60)
    print(txt)


if __name__ == "__main__":
    main()
