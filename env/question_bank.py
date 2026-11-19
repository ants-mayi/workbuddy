# -*- coding: utf-8 -*-
"""
「本机开发环境」记忆抽测题库（Windows / macOS 双平台）
每题：t 主题 / q 问题 / k 判分关键词（任一命中算对）/ a 参考答案 / d 详解
答案里写 <short> 会自动替换成命令前缀 env。
文件末尾按 sys.platform 自动选择 Windows 或 Mac 题组。
"""

import sys as _sys

_WINDOWS_BANK = [
    # ── 命令 ────────────────────────────────────────────────────
    {"t": "命令", "q": "忘记本机环境情况时，第一条命令敲什么？", "k": ["status", "状态"],
     "a": "<short> status", "d": "一条看清所有工具版本、GPU、关键路径存在性。速记看 <short> recap。"},
    {"t": "命令", "q": "一键体检本机环境的命令？", "k": ["doctor", "体检"],
     "a": "<short> doctor", "d": "检查版本是否符合基线、解释器/缓存/磁盘是否正常，异常给修复建议。"},
    {"t": "命令", "q": "想查 Windows 服务状态、端口、启动命令去哪看？", "k": ["服务", "端口", "service", "web"],
     "a": "Web 控制台「服务与端口」面板", "d": "双击 env-web.bat，左侧「服务与端口」；命令行也可用 <short> services。"},
    {"t": "命令", "q": "检验自己是否记住本机关键信息，用哪条？", "k": ["quiz", "抽测", "记忆"],
     "a": "<short> quiz", "d": "主动回忆抽测，先答再看详解；<short> quiz -t 解释器 可专项练。"},
    {"t": "命令", "q": "查看各缓存目录占用（npm/Conda/HF 等）的命令？", "k": ["cache", "缓存"],
     "a": "<short> cache", "d": "只读报告占用；本主题不提供自动清理系统缓存，避免误删。"},

    # ── 解释器 / AI 环境 ────────────────────────────────────────
    {"t": "解释器", "q": "跑 AI 任务（torch/transformers）必须用哪个解释器？", "k": ["G:", "pytorch", "workIns"],
     "a": "G:\\workIns\\conda\\envs\\pytorch\\python.exe",
     "d": "这是本机唯一装了 torch/transformers 的环境，不在 PATH。PATH 里的 python 都没有 AI 库。"},
    {"t": "解释器", "q": "PATH 里有几套 python？分别多少版本？", "k": ["3.13", "3.14", "三"],
     "a": "3 套：3.13.14（WorkBuddy）/ 3.14（独立安装）/ 3.13.9（Anaconda base）",
     "d": "都没有 AI 库。装包一律 python -m pip，避免装到 A 用在 B。"},
    {"t": "解释器", "q": "本机有几套 Conda？装 PyTorch 的是哪套？", "k": ["两", "G", "workIns"],
     "a": "两套：D 盘 wofkIns（PATH 中，仅 base）/ G 盘 workIns（含 pytorch 环境）",
     "d": "目录名拼写不同：wofkIns vs workIns，别混淆。激活：conda activate G:\\workIns\\conda\\envs\\pytorch。"},
    {"t": "解释器", "q": "装 Python 包为什么要用 python -m pip 而不是裸 pip？", "k": ["解释", "指向", "一致", "版本"],
     "a": "确保包装到当前 python 对应的解释器，避免多版本下装在 A 用在 B",
     "d": "本机 pip 指向 3.14，而当前 bash 的 python 是 3.13，裸 pip 会装错地方。"},

    # ── GPU / AI 库 ────────────────────────────────────────────
    {"t": "AI/GPU", "q": "本机 GPU 型号和显存？torch 版本？", "k": ["3070", "8", "2.11"],
     "a": "RTX 3070 8GB；torch 2.11.0+cu126", "d": "CUDA 可用，驱动 621.14；8GB 适合微调小模型或推理量化模型。"},
    {"t": "AI/GPU", "q": "transformers 版本？v4→v5 哪几个参数改名了？", "k": ["5.8", "dtype", "processing_class", "eval_strategy"],
     "a": "transformers 5.8.0；torch_dtype→dtype、tokenizer→processing_class、evaluation_strategy→eval_strategy",
     "d": "v4 老写法在 v5 会报错，详见 HF 学习笔记的迁移表。"},
    {"t": "AI/GPU", "q": "HF 缓存和国内镜像环境变量分别指向哪？", "k": ["HF_HOME", "G:", "hf-mirror"],
     "a": "HF_HOME=G:\\study\\AI\\cache\\huggingface；HF_ENDPOINT=https://hf-mirror.com",
     "d": "都已设为系统环境变量且实测生效；缓存放 G 盘不占 C 盘。"},
    {"t": "AI/GPU", "q": "训练脚本里 pyarrow WinError 6714 的根因和修法？", "k": ["datasets", "torch", "顺序", "import"],
     "a": "torch 先于 datasets import 导致；把 from datasets import load_dataset 放到 import torch 之前",
     "d": "这是本机踩过的坑，详见脚手架 docs/03-踩坑与解法.md。"},

    # ── 服务 / 端口 ────────────────────────────────────────────
    {"t": "服务端口", "q": "本机常驻的串流 TCP 端口是哪几个？", "k": ["47984", "47989", "47990", "48010"],
     "a": "47984 / 47989 / 47990 / 48010（Sunshine 串流）", "d": "调试 Web 服务选端口时避开它们；47990 是 Sunshine 管理页。"},
    {"t": "服务端口", "q": "Tailscale 用哪个端口？本机组网 IP 多少？", "k": ["41641", "100.75.245.81", "UDP"],
     "a": "UDP 41641；本机 IP 100.75.245.81", "d": "远程访问优先走 Tailscale 组网，少做公网端口映射。"},
    {"t": "服务端口", "q": "本机 MySQL 有几套？推荐用哪套、什么端口？", "k": ["三", "8.0", "3307"],
     "a": "三套；推荐 8.0.29 用 3307", "d": "服务当前均未启动，两套同配 3306 会冲突；客户端 mysql.exe 未进 PATH。"},
    {"t": "服务端口", "q": "如何查看 Windows 服务状态 / 启动服务？", "k": ["Get-Service", "net start", "Start-Service"],
     "a": "Get-Service 查状态；net start <服务名> 或 Start-Service 启动（需管理员）",
     "d": "三个串流/组网服务 Running，MySQL 两套 Stopped。详见「服务与端口」面板。"},
    {"t": "服务端口", "q": ".NET 为什么 dotnet --version 会报错？", "k": ["SDK", "运行时", "正常"],
     "a": "只装了运行时没装 SDK，报错正常", "d": "运行时 7.0.20/9.0.22；要开发 C# 需装 .NET 8 LTS SDK。"},
    {"t": "服务端口", "q": "哪些工具未安装？", "k": ["Ollama", "Docker", "Gradle"],
     "a": "Ollama、Docker、Gradle（Gradle 可用 wrapper 免装）", "d": "torchaudio 也未装，可在 AI 环境补 cu126 匹配版。"},

    # ── 路径 / 磁盘 ────────────────────────────────────────────
    {"t": "路径", "q": "开发软件主要装在哪两个目录？", "k": ["wofkIns", "softIns"],
     "a": "D:\\wofkIns\\ 与 D:\\softIns\\", "d": "Node/Python 有 WorkBuddy 内置版在 .workbuddy\\binaries；Tailscale 在 F:\\Game。"},
    {"t": "路径", "q": "本机环境信息的唯一事实源文档在哪？", "k": ["电脑开发环境信息", "G:", "WorkBuddy"],
     "a": "G:\\AI\\WorkBuddy\\docs\\电脑开发环境信息.md", "d": "共 23 节；版本/路径/端口/命令以它为准，缺项先实测再补进去。"},
    {"t": "路径", "q": "哪个盘空间紧张，新软件/模型应放哪？", "k": ["C", "D", "E", "F", "M"],
     "a": "C 盘余 ~38GB、D 盘余 ~12GB 偏紧；新数据放 E/F/M 盘", "d": "E/F/M 各余 200GB 以上，充足。"},

    # ── 排障 ───────────────────────────────────────────────────
    {"t": "排障", "q": "验证软件是否就绪的「三层法」是哪三层？", "k": ["有没有", "环境", "正常", "功能"],
     "a": "①功能有没有 → ②相关环境是否存在 → ③功能是否正常（跑最小任务）",
     "d": "三层都过才算真可用。有环境验证脚本.py 可一键跑完。"},
    {"t": "排障", "q": "命令行 import torch 报 ModuleNotFoundError，最可能原因？", "k": ["python", "PATH", "解释器", "环境"],
     "a": "用错了解释器——PATH 里的 python 没有 torch",
     "d": "改用 G 盘 pytorch 环境的解释器，或先 conda activate 该环境。不是真的没装。"},
    {"t": "排障", "q": "bat 脚本中文注释导致 CMD 解析错乱，怎么避免？", "k": ["ASCII", "英文", "chcp", "编码"],
     "a": "bat 内容只用 ASCII，中文提示放 Python 端；配合 chcp 65001",
     "d": "CMD 默认 GBK，中文注释/标点会被错误解析。生成器产出的 bat 已是纯 ASCII。"},
]

# ============================================================
# Mac 题组（Apple M2 MacBook，2026-11-17 实测采集）
# ============================================================
_MAC_BANK = [
    # ── 命令 ────────────────────────────────────────────────────
    {"t": "命令", "q": "忘记本机环境情况时，第一条命令敲什么？", "k": ["status", "状态"],
     "a": "<short> status", "d": "一条看清所有工具版本、GPU、关键路径存在性。速记看 <short> recap。"},
    {"t": "命令", "q": "一键体检本机环境的命令？", "k": ["doctor", "体检"],
     "a": "<short> doctor", "d": "检查版本是否符合基线、解释器/缓存/磁盘是否正常，异常给修复建议。"},
    {"t": "命令", "q": "想查本机服务/常驻进程状态、端口、启动命令去哪看？", "k": ["服务", "端口", "service", "web"],
     "a": "Web 控制台「服务与端口」面板", "d": "运行 ./env-web.sh 打开网页控制台；命令行也可用 <short> services。"},
    {"t": "命令", "q": "查看各缓存目录占用（Conda/HF/npm 等）的命令？", "k": ["cache", "缓存"],
     "a": "<short> cache", "d": "只读报告占用；本主题不提供自动清理系统缓存，避免误删。"},
    {"t": "命令", "q": "重新采集本机 Mac 环境事实的命令？", "k": ["collect_mac", "采集"],
     "a": "python3 mac/collect_mac.py", "d": "生成 mac_profile.json（完整数据）和 mac_profile.txt（摘要），更新 PROFILE_MAC 时先跑它。"},

    # ── 解释器 / AI 环境 ────────────────────────────────────────
    {"t": "解释器", "q": "跑 AI 任务（torch/transformers）必须用哪个解释器？", "k": ["miniconda3", "pytorch", "envs"],
     "a": "/Users/masc/miniconda3/envs/pytorch/bin/python",
     "d": "唯一装了 torch/transformers 的环境。先 conda activate pytorch，或直接写全路径。"},
    {"t": "解释器", "q": "PATH 里有几套 python3？分别是多少？", "k": ["4", "四", "3.13", "3.14", "3.9"],
     "a": "4 套：WorkBuddy 3.13.12 / miniconda3 3.13.13 / Homebrew 3.14.6 / 系统 3.9.6",
     "d": "which -a python3 可验证。都没有 torch。装包一律 python -m pip。"},
    {"t": "解释器", "q": "本机 conda 有哪些环境？AI 环境叫什么？", "k": ["base", "llm", "pytorch"],
     "a": "base / llm / pytorch 三个环境；AI 任务用 pytorch",
     "d": "conda env list 查看。激活：conda activate pytorch。"},

    # ── GPU / AI 库 ────────────────────────────────────────────
    {"t": "AI/GPU", "q": "本机芯片是什么？torch 用什么后端加速？CUDA 可用吗？", "k": ["M2", "MPS", "mps", "cuda"],
     "a": "Apple M2（24GB 统一内存）；torch 用 MPS 后端，无 NVIDIA CUDA",
     "d": "验证：python -c \"import torch;print(torch.backends.mps.is_available())\"，应输出 True。"},
    {"t": "AI/GPU", "q": "torch 和 transformers 的版本？v4→v5 哪几个参数改名了？", "k": ["2.11", "5.8", "dtype", "processing_class", "eval_strategy"],
     "a": "torch 2.11.0；transformers 5.8.0；torch_dtype→dtype、tokenizer→processing_class、evaluation_strategy→eval_strategy",
     "d": "v4 老写法在 v5 会报错。Mac 与 Windows 侧 AI 环境版本一致，学习笔记通用。"},
    {"t": "AI/GPU", "q": "本机 HF 缓存指向哪？HF_HOME 设了吗？", "k": [".cache", "huggingface", "未设置", "默认"],
     "a": "未设置 HF_HOME，用默认 ~/.cache/huggingface",
     "d": "与 Windows 侧（G 盘自定义路径）不同。想改就 export HF_HOME=... 写进 ~/.zshrc。"},

    # ── 服务 / 端口 ────────────────────────────────────────────
    {"t": "服务端口", "q": "Ollama 在本机什么状态、占哪个端口？", "k": ["11434", "常驻", "运行"],
     "a": "常驻运行，端口 11434；模型文件在 ~/.ollama", "d": "ollama list 看模型，ollama ps 看运行中模型。"},
    {"t": "服务端口", "q": "5000 和 7000 端口被谁占了？起服务要注意什么？", "k": ["ControlCenter", "AirPlay", "系统"],
     "a": "macOS ControlCenter（AirPlay 接收器）占用；起服务避开这两个端口",
     "d": "系统占用关不掉也不该关；控制台 Web 用 8010，冲突时会自动顺延。"},
    {"t": "服务端口", "q": "本机代理环境变量是什么情况？", "k": ["HTTP_PROXY", "HTTPS_PROXY", "代理", "51510"],
     "a": "HTTP(S)_PROXY 指向本机代理工具（端口随代理客户端变化）",
     "d": "pip/git 走代理异常先查代理是否在跑；当前实测量 127.0.0.1:51510。"},

    # ── 路径 / 工具 ────────────────────────────────────────────
    {"t": "路径", "q": "Homebrew 装的软件都在哪？本机哪些开发工具来自 brew？", "k": ["/opt/homebrew", "brew"],
     "a": "/opt/homebrew（arm64 标准位置）；JDK17/Maven/Go/ffmpeg/git 都来自 brew",
     "d": "brew list --formula 查看。JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home。"},
    {"t": "路径", "q": "本机环境事实（PROFILE_MAC）的数据来源文件在哪？", "k": ["mac_profile", "collect_mac", "config.py"],
     "a": "mac/mac_profile.json（采集原始数据）；配置在 config.py 的 PROFILE_MAC",
     "d": "软件升级/路径变更后：先重跑 python3 mac/collect_mac.py，再更新 PROFILE_MAC。"},
    {"t": "路径", "q": "VSCode 怎么从命令行打开？code 命令在 PATH 里吗？", "k": ["open -a", "不在", "PATH"],
     "a": "code 不在 PATH；用 open -a 'Visual Studio Code' .",
     "d": "想用 code 命令可在 VSCode 里执行 Shell Command: Install 'code' command in PATH。"},

    # ── 排障 ───────────────────────────────────────────────────
    {"t": "排障", "q": "验证软件是否就绪的「三层法」是哪三层？", "k": ["有没有", "环境", "正常", "功能"],
     "a": "①功能有没有 → ②相关环境是否存在 → ③功能是否正常（跑最小任务）",
     "d": "三层都过才算真可用。"},
    {"t": "排障", "q": "命令行 import torch 报 ModuleNotFoundError，最可能原因？", "k": ["python", "PATH", "解释器", "环境", "conda"],
     "a": "用错了解释器——PATH 里的 python3 没有 torch",
     "d": "先 conda activate pytorch（或用全路径），不是真的没装。"},
    {"t": "排障", "q": "macOS 上查某个端口被谁占用用什么命令？", "k": ["lsof"],
     "a": "lsof -nP -iTCP:端口号（全部监听：lsof -nP -iTCP -sTCP:LISTEN）",
     "d": "Windows 对应 netstat -ano；Web 控制台「实时端口」面板可直接看。"},
]

# 按平台自动选择：Windows 用 Windows 题，Mac 用 Mac 题
QUESTION_BANK = _WINDOWS_BANK if _sys.platform == "win32" else _MAC_BANK
