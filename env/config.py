# -*- coding: utf-8 -*-
import sys as _sys
r"""
=============================================================================
主题配置 PROFILE —— 「本机开发环境」一条龙控制台（Windows / macOS 双平台）
=============================================================================
基于脚手架生成，引擎在 engine/（本副本按本机主题做了克定制制，脚手架模板未改）。
所有主题信息集中在本文件；版本探测用绝对路径调用各工具，稳定复现。

本文件同时保存两套事实数据（保证 Windows 和 Mac 都能用）：
    PROFILE_WIN —— Windows 11 台式机（事实源 M:\AI\WorkBuddy\docs\电脑开发环境信息.md，2026-11-16 采集）
    PROFILE_MAC —— MacBook (Apple M2)（2026-11-17 用 mac/collect_mac.py 实测采集）
文件末尾按 sys.platform 自动选择：win32 → PROFILE_WIN，其余 → PROFILE_MAC。
把整个 env/ 目录拷到另一台机器后，只需更新对应平台的 PROFILE_* 即可，引擎不用改。

Windows 实测复核：2026-11-17。差异处以实测为准（如 git 2.55.0.windows.2）。
"""

PROFILE_WIN = {
    # ── 1. 身份 ───────────────────────────────────────────────────
    "name": "本机开发环境",
    "short": "env",
    "desc": "Windows 11 本机环境 · 版本 / 路径 / 服务 / 端口 一条龙速查",
    "docs_title": "本机开发环境速查",

    # ── 2. 路径 ───────────────────────────────────────────────────
    "paths": {
        "project": ".",
        "artifacts": "",           # 无模型产物
        "data": "",                # 无数据集
        "notes": "notes",          # 速查文档目录
        "web": "web",
        "cache": "",               # 缓存由 cache.items 单独列
    },

    # ── 3. 环境 / 版本探测 ────────────────────────────────────────
    # 每条 probe 用绝对路径调用外部命令，吞掉异常并 print 单行版本。
    # 引擎把全部 probe 拼进一个子进程按序执行（单进程 + 缓存，首次后秒回）。
    "env": {
        "python_exe": r"G:\workIns\conda\envs\pytorch\python.exe",
        "disk_drive": "C:\\",       # 体检关注系统盘剩余
        "mirror_host": "",          # 无镜像主机 → 跳过连通性检查
        "mirror_url": "",
        "versions": [
            {"label": "Python", "expect_major": "3",
             "probe": "import sys; print(sys.version.split()[0])"},

            {"label": "JDK", "expect_major": "17",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run([r"D:\\wofkIns\\jdk-17.0.0.1\\bin\\java.exe","-version"],capture_output=True,text=True,timeout=25)
    _m=_re.search(r'"([0-9][^"]*)"',(_r.stdout or "")+(_r.stderr or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "Maven", "expect_major": "3",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["cmd","/c",r"D:\\wofkIns\\apache-maven-3.9.9\\bin\\mvn.cmd","-version"],capture_output=True,text=True,timeout=30)
    _m=_re.search(r"Apache Maven ([0-9][^ ]*)",(_r.stdout or "")+(_r.stderr or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "Node.js", "expect_major": "22",
             "probe": '''import subprocess as _sp
try:
    _r=_sp.run([r"C:\\Users\\marco\\.workbuddy\\binaries\\node\\versions\\22.22.2-6\\node.exe","-v"],capture_output=True,text=True,timeout=20)
    print((_r.stdout or "").strip().lstrip("v") or "-")
except Exception:
    print("-")'''},

            {"label": "npm", "expect_major": "10",
             "probe": '''import subprocess as _sp
try:
    _r=_sp.run(["cmd","/c",r"C:\\Users\\marco\\.workbuddy\\binaries\\node\\versions\\22.22.2-6\\npm.cmd","-v"],capture_output=True,text=True,timeout=20)
    print((_r.stdout or "").strip().splitlines()[0] or "-")
except Exception:
    print("-")'''},

            {"label": "Git", "expect_major": "2",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run([r"D:\\wofkIns\\Git\\cmd\\git.exe","--version"],capture_output=True,text=True,timeout=20)
    _m=_re.search(r"git version ([0-9][^ ]*)",(_r.stdout or "")+(_r.stderr or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "Conda", "expect_major": "26",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run([r"D:\\wofkIns\\anaconda3\\Scripts\\conda.exe","--version"],capture_output=True,text=True,timeout=25)
    _m=_re.search(r"conda\\s+([0-9][^\\s]*)",(_r.stdout or "")+(_r.stderr or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "torch", "expect_major": "2",
             "probe": "import torch; print(torch.__version__)"},
            {"label": "transformers", "expect_major": "5",
             "probe": "import transformers; print(transformers.__version__)"},
            {"label": "Flask", "expect_major": "3",
             "probe": "import flask; print(flask.__version__)"},
        ],
        # GPU 属本机环境的一部分，保留探测
        "gpu": {
            "probe": "import torch; print('TRUE' if torch.cuda.is_available() else 'FALSE')",
            "name_probe": "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else '-')",
        },
    },

    # ── 4. 服务：本主题无推理脚本服务 ─────────────────────────────
    "serve": {"enabled": False},
    "web_port": 8010,               # 避开 HF 控制台 8000

    # ── 5. 数据 / 产物 / 曲线：本主题均不适用（留空）──────────────
    "data": {"files": [], "sample_file": "", "sample_col": "",
             "label_source": "", "label_note": "本机开发环境主题无数据集；服务/端口见「服务与端口」面板。"},
    "artifacts": {
        "meanings": {}, "must_exist": [], "metrics_files": [],
        "history_file": "", "history_key": "", "curve_metrics": [], "x_key": "step",
    },

    # ── 6. 缓存占用（只读，全部 safe=False，不提供删除系统缓存）──
    # 2026-11-17 实测大小；引擎按 path 实时计算，note 里的数字仅供快速参考
    "cache": {"items": [
        {"name": "Conda packages (G 盘)", "path": r"G:\workIns\conda\pkgs", "safe": False,
         "note": "AI 环境(pytorch)的包缓存，实测 11.3 GB；删除前确认环境不再需要"},
        {"name": "Conda pkgs (D 盘旧套)", "path": r"D:\wofkIns\anaconda3\pkgs", "safe": False,
         "note": "D 盘 anaconda3(base)的包缓存，实测 6.6 GB；与 G 盘互不相干"},
        {"name": "AI 模型/数据集缓存 (G 盘)", "path": r"G:\study\AI\cache", "safe": False,
         "note": "实测 16.5 GB：huggingface 2.8 + imdb_m2_optimized 10.3 + bert-base-cased 3.4 GB，删除后需重新下载"},
        {"name": "pip 缓存", "path": r"C:\Users\marco\AppData\Local\pip\Cache", "safe": False,
         "note": "实测 6.7 GB，本机最大缓存之一（各 Python 共用）；清理：pip cache purge"},
        {"name": "npm 缓存", "path": r"C:\Users\marco\AppData\Local\npm-cache", "safe": False,
         "note": "实测仅 0.02 GB（npm config get cache 确认的位置）"},
        {"name": "Maven 本地仓库", "path": r"G:\workIns\LocalWareHouse", "safe": False,
         "note": "实测 11.65 GB（真正生效的仓库）；全局 conf/settings.xml 指定，清理勿直接删"},
        {"name": "Maven 旧仓库(遗留)", "path": r"D:\wofkIns\repository", "safe": False,
         "note": "实测 10.4 GB；Maven 已改用 G 盘 LocalWareHouse，此目录不再使用，可评估迁移或清理"},
        {"name": "Codex 运行时缓存", "path": r"C:\Users\marco\.cache", "safe": False,
         "note": "codex-runtimes 1.4 GB；删除后 Codex CLI 会重新下载运行时"},
        {"name": "系统临时文件 Temp", "path": r"C:\Users\marco\AppData\Local\Temp", "safe": False,
         "note": "实测约 2 GB，可用系统「存储感知」或磁盘清理处理，勿手动全删"},
    ]},

    # ── 7. recap 核心速记 ─────────────────────────────────────────
    "recap": {
        "core": "唯一事实源：M:\\AI\\WorkBuddy\\docs\\电脑开发环境信息.md（23 节）\n"
                "AI 解释器只有 G:\\workIns\\conda\\envs\\pytorch\\python.exe（torch 2.11+cu126 / transformers 5.8），不在 PATH\n"
                "PATH 里的 python 有 3 套（3.13.14 / 3.14 / 3.13.9）但都没有 AI 库；装包一律 python -m pip\n"
                "两套 Conda：D 盘 wofkIns（PATH 中，仅 base）/ G 盘 workIns（AI 环境所在）",
        "rules": [
            "AI 任务固定用 G 盘 pytorch 环境解释器，PATH 里的 python 没有 torch",
            "远程/串流端口常驻：Sunshine 47984/47989/47990/48010、Tailscale UDP 41641；调试端口先排查它们",
            "MySQL 三套、服务均未启动且两套同配 3306；用前先定哪套并错开端口（推荐 8.0 用 3307）",
            ".NET 只有运行时无 SDK；dotnet --version 报错属正常；Ollama/Docker/Gradle 未装",
            "C 盘余 ~38 GB、D 盘余 ~12 GB 偏紧，新软件/模型放 E/F/M 盘",
            "验证软件是否就绪用三层法：①有没有 → ②环境齐不齐 → ③跑个最小任务",
        ],
        "commands_note": "忘记先看 env status / env recap；检验记忆用 env quiz；环境异常用 env doctor；服务端口看 Web「服务与端口」。",
    },

    "extra_checks": [],             # 引擎的 extra_checks 仅支持 json_key，本主题不用
    "question_module": "question_bank.py",

    # ── 8. 主题定制字段（引擎副本读取；脚手架模板不认识，不影响）──
    "ui": {
        # Web 面板显示顺序（面向"查询 + 操作"，移除记忆抽测 quiz）
        # pathtruth=PATH真相 / envvars=环境变量 / ports_live=实时端口 / processes=关键进程 / cmdlib=命令库
        "sections": ["status", "info", "pathtruth", "envvars", "software", "aitools", "servicesvc",
                     "ports_live", "processes", "test", "doctor", "cmdlib", "cache", "docs"],
    },
    "facts": {
        "ai_tools": [
            # 依据 Windows 事实源（01-B3/B4，2026-11-16 采集）预填；
            # ⚠️ 子目录/数据路径需在 Windows 实机复核后补全（复核前不写猜测路径）
            {
                "name": "WorkBuddy（腾讯）", "version": "5.11.3",
                "app": "", "home": "", "size": "",
                "items": [
                    {"name": "安装目录", "path": r"D:\softIns", "note": "事实源 B4：WorkBuddy 安装于 D:\\softIns 下（具体子目录待实机复核）"},
                ],
                "note": "内置 node/python（PATH 首个来自它）；Windows 侧数据目录待实机采集",
            },
            {
                "name": "千问 Qianwen（阿里）", "version": "5.2.0",
                "app": "", "home": "", "size": "",
                "items": [
                    {"name": "安装目录", "path": r"D:\softIns", "note": "事实源 B4：安装于 D:\\softIns 下（具体子目录待实机复核）"},
                ],
                "note": "Windows 侧是否另有千问办公未记录，待实机确认",
            },
            {
                "name": "豆包（字节）", "version": "2.32.6",
                "app": "", "home": "", "size": "",
                "items": [
                    {"name": "安装目录", "path": r"D:\softIns", "note": "事实源 B4：安装于 D:\\softIns 下（具体子目录待实机复核）"},
                ],
                "note": "Mac 侧未安装（仅 Windows 有）",
            },
            {
                "name": "Trae CN（字节）", "version": "3.4.20",
                "app": r"D:\Program Files (x86)\Trae CN", "home": "", "size": "",
                "items": [
                    {"name": "安装目录", "path": r"D:\Program Files (x86)\Trae CN", "note": "事实源 B3 实测路径"},
                ],
                "note": "与 Mac 侧 Trae CN 3.4.20 同版本；用户数据目录待实机采集",
            },
        ],
        # 关键路径（status 面板展示存在性）
        "paths": [
            {"name": "环境手册（事实源）", "path": r"M:\AI\WorkBuddy\docs\电脑开发环境信息.md"},
            {"name": "AI 环境解释器", "path": r"G:\workIns\conda\envs\pytorch\python.exe"},
            {"name": "HF 缓存", "path": r"G:\study\AI\cache\huggingface"},
            {"name": "JDK", "path": r"D:\wofkIns\jdk-17.0.0.1"},
            {"name": "Maven", "path": r"D:\wofkIns\apache-maven-3.9.9"},
            {"name": "Git", "path": r"D:\wofkIns\Git\cmd\git.exe"},
            {"name": "Tailscale", "path": r"F:\Game\tailscale"},
            {"name": "VSCode", "path": r"D:\softIns\Microsoft VS Code"},
            {"name": "IDEA Ultimate", "path": r"D:\wofkIns\ideaIU-2025.1.win"},
            {"name": "DBeaver", "path": r"D:\wofkIns\dbeaver-ce-25.1.3-win32.win32.x86_64"},
            {"name": "Postman", "path": r"C:\Users\marco\AppData\Local\Postman"},
        ],
        # Windows 服务：查询用 Get-Service，启动命令供复制
        "services": [
            {"name": "Sunshine 串流", "svc": "SunshineService", "expect": "Running",
             "start": "net start SunshineService  (管理员)", "note": "TCP 47984/47989/47990/48010"},
            {"name": "Tailscale 组网", "svc": "Tailscale", "expect": "Running",
             "start": "net start Tailscale  (管理员)", "note": "UDP 41641；本机 IP 100.75.245.81"},
            {"name": "UU远程 GameViewer", "svc": "GameViewerService", "expect": "Running",
             "start": "net start GameViewerService  (管理员)", "note": "远程游戏服务"},
            {"name": "MySQL 5.7", "svc": "MySQL", "expect": "Stopped",
             "start": "net start MySQL  (管理员)", "note": "端口 3306；手动启动类型"},
            {"name": "MySQL 8.0", "svc": "mysql80", "expect": "Stopped",
             "start": "net start mysql80  (管理员)", "note": "端口 3307，推荐用这套"},
        ],
        # 常驻端口快照（来自环境手册 + 实测）
        "ports": [
            {"port": "47984 / 47989 / 47990 / 48010", "proto": "TCP", "use": "Sunshine 串流", "state": "监听中"},
            {"port": "41641", "proto": "UDP", "use": "Tailscale 组网", "state": "监听中"},
            {"port": "3306 / 3307", "proto": "TCP", "use": "MySQL（服务未启动）", "state": "未监听"},
            {"port": "11434", "proto": "TCP", "use": "Ollama（未安装）", "state": "未监听"},
            {"port": "8000 / 8010", "proto": "TCP", "use": "控制台 Web（HF / 本机环境）", "state": "按需"},
        ],
        # 磁盘快照（环境手册 2026-11-16 采集）
        "disks": [
            {"drive": "C:", "free_gb": 37.9, "note": "系统盘，偏紧"},
            {"drive": "D:", "free_gb": 12.4, "note": "很紧张"},
            {"drive": "E:", "free_gb": 391.9, "note": "充足"},
            {"drive": "F:", "free_gb": 318.2, "note": "充足"},
            {"drive": "G:", "free_gb": 82.4, "note": "AI 环境所在"},
            {"drive": "M:", "free_gb": 201.5, "note": "工作区所在"},
        ],

        # ── 基础信息：配置文件路径（2026-11-17 实测存在性）────────
        "config_files": [
            {"name": "环境手册（唯一事实源）", "path": r"M:\AI\WorkBuddy\docs\电脑开发环境信息.md",
             "note": "23 节，软件升级/路径变更后先改这里"},
            {"name": "本控制台配置", "path": r"M:\AI\WorkBuddy\env\config.py",
             "note": "改版本探测/路径/面板都在这里"},
            {"name": "控制台题库（当前未启用）", "path": r"M:\AI\WorkBuddy\env\question_bank.py",
             "note": "已移除记忆抽测，文件保留备用"},
            {"name": "Git 全局配置", "path": r"C:\Users\marco\.gitconfig", "note": "user.name/email 等"},
            {"name": "Maven 全局 settings.xml", "path": r"D:\wofkIns\apache-maven-3.9.9\conf\settings.xml",
             "note": "已自定义 localRepository → G:\\workIns\\LocalWareHouse（用户级 ~/.m2/settings.xml 不存在）"},
            {"name": "WorkBuddy MCP 配置", "path": r"C:\Users\marco\.workbuddy\mcp.json", "note": "自定义 MCP 服务"},
            {"name": "WorkBuddy 设置", "path": r"C:\Users\marco\.workbuddy\settings.json", "note": "全局设置"},
            {"name": "VSCode 用户设置", "path": r"C:\Users\marco\AppData\Roaming\Code\User\settings.json", "note": ""},
            {"name": "hosts 文件", "path": r"C:\Windows\System32\drivers\etc\hosts", "note": "需管理员修改"},
        ],
        # 常见于"配置文件"但本机不存在（如 ~/.npmrc、~/.m2/settings.xml、~/.ssh/config）——
        # 未列入上方，避免误报；需要时手动创建即可。

        # ── 基础信息：产物 / 工作目录路径 ──────────────────────────
        "products": [
            {"name": "AI 环境解释器", "path": r"G:\workIns\conda\envs\pytorch\python.exe",
             "note": "torch 2.11+cu126 / transformers 5.8，唯一带 AI 库的 Python"},
            {"name": "Python site-packages", "path": r"G:\workIns\conda\envs\pytorch\Lib\site-packages",
             "note": "AI 环境的第三方包装在这里"},
            {"name": "Conda envs（G 盘）", "path": r"G:\workIns\conda\envs", "note": "AI 环境所在"},
            {"name": "Conda envs（D 盘）", "path": r"D:\wofkIns\anaconda3\envs", "note": "仅 base，PATH 中的 Conda"},
            {"name": "HF 缓存（模型/数据集）", "path": r"G:\study\AI\cache\huggingface", "note": "HF_HOME，删除后需重下"},
            {"name": "Maven 本地仓库", "path": r"G:\workIns\LocalWareHouse",
             "note": "实测 11.65 GB；全局 conf/settings.xml 指定（默认 ~/.m2/repository 仅 0.07 GB 残留）"},
            {"name": "pip 缓存", "path": r"C:\Users\marco\AppData\Local\pip\Cache", "note": "下载过的 wheel"},
            {"name": "npm 缓存", "path": r"C:\Users\marco\AppData\Local\npm-cache", "note": "Node 包缓存"},
            {"name": "控制台速查文档", "path": r"M:\AI\WorkBuddy\env\notes", "note": "6 份复习/查询文档"},
        ],

        # ── 软件状态：开发工具 + 运行时（版本实时探测，路径/操作来自此表）──
        # probe_label 对应 env.versions 的 label；引擎据此合并实时版本
        "software": [
            {"name": "JDK 17", "probe_label": "JDK", "path": r"D:\wofkIns\jdk-17.0.0.1",
             "category": "开发", "start": "", "note": "java -version；版本输出到 stderr"},
            {"name": "Maven 3.9", "probe_label": "Maven", "path": r"D:\wofkIns\apache-maven-3.9.9",
             "category": "开发", "start": "mvn -v", "note": "需 cmd /c 调用 .cmd"},
            {"name": "Node.js 22", "probe_label": "Node.js", "path": r"C:\Users\marco\.workbuddy\binaries\node\versions\22.22.2-6",
             "category": "开发", "start": "node -v", "note": "WorkBuddy 内置 node"},
            {"name": "npm 10", "probe_label": "npm", "path": r"C:\Users\marco\.workbuddy\binaries\node\versions\22.22.2-6\npm.cmd",
             "category": "开发", "start": "npm -v", "note": "需 cmd /c 调用 .cmd"},
            {"name": "Git", "probe_label": "Git", "path": r"D:\wofkIns\Git\cmd\git.exe",
             "category": "开发", "start": "git --version", "note": "实测 2.55.0.windows.2"},
            {"name": "Conda (D 盘)", "probe_label": "Conda", "path": r"D:\wofkIns\anaconda3\Scripts\conda.exe",
             "category": "环境", "start": "conda --version", "note": "PATH 中的 Conda，仅 base"},
            {"name": "Python (AI 环境)", "probe_label": "Python", "path": r"G:\workIns\conda\envs\pytorch\python.exe",
             "category": "环境", "start": "python -V", "note": "AI 任务固定用它，不在 PATH"},
            {"name": "PyTorch", "probe_label": "torch", "path": r"G:\workIns\conda\envs\pytorch\Lib\site-packages\torch",
             "category": "AI", "start": "python -c \"import torch;print(torch.__version__)\"", "note": "GPU 版 cu126"},
            {"name": "Transformers", "probe_label": "transformers", "path": "",
             "category": "AI", "start": "python -c \"import transformers;print(transformers.__version__)\"", "note": "v5.8.0"},
            {"name": "Flask", "probe_label": "Flask", "path": "",
             "category": "AI", "start": "python -c \"import flask;print(flask.__version__)\"", "note": "Web 控制台依赖"},
            {"name": "DBeaver 25.1", "probe_label": "", "path": r"D:\wofkIns\dbeaver-ce-25.1.3-win32.win32.x86_64",
             "category": "工具", "start": "dbeaver.exe", "note": "数据库客户端 CE 版"},
            {"name": "Postman 12", "probe_label": "", "path": r"C:\Users\marco\AppData\Local\Postman",
             "category": "工具", "start": "Postman.exe", "note": "接口调试"},
            {"name": "VSCode", "probe_label": "", "path": r"D:\softIns\Microsoft VS Code",
             "category": "工具", "start": "code", "note": "代码编辑器"},
            {"name": "IDEA Ultimate", "probe_label": "", "path": r"D:\wofkIns\ideaIU-2025.1.win",
             "category": "工具", "start": "idea64.exe", "note": "Java IDE"},
            {"name": "Docker", "probe_label": "", "path": r"C:\Program Files\Docker\Docker",
             "category": "未安装", "start": "", "note": "尚未安装，需要时再装"},
            {"name": "Ollama", "probe_label": "", "path": r"C:\Users\marco\AppData\Local\Programs\Ollama",
             "category": "未安装", "start": "", "note": "尚未安装；端口 11434"},
            {"name": "WorkBuddy", "probe_label": "", "path": "",
             "category": "AI", "start": "", "note": "5.11.3，安装于 D:\\softIns\\（子目录待实机复核）"},
            {"name": "千问 Qianwen", "probe_label": "", "path": "",
             "category": "AI", "start": "", "note": "5.2.0，安装于 D:\\softIns\\（子目录待实机复核）"},
            {"name": "豆包", "probe_label": "", "path": "",
             "category": "AI", "start": "", "note": "2.32.6，安装于 D:\\softIns\\（Mac 侧未装）"},
            {"name": "Trae CN", "probe_label": "", "path": r"D:\Program Files (x86)\Trae CN",
             "category": "AI", "start": "", "note": "3.4.20，与 Mac 同版本"},
        ],

        # ── PATH 真相：命令实际解析（where 动态探测；expect 为期望路径片段）──
        # 判定：0 个=未找到；1 个=正常；多个=预警（第一个才是实际生效的）
        # expect 不在结果里=预警并给出说明（如 python 的 AI 解释器故意不在 PATH）
        "path_commands": [
            {"cmd": "python", "expect": r"G:\workIns\conda\envs\pytorch",
             "note": "PATH 里 4 个 python（首个是 WorkBuddy 3.13.12），AI 解释器不在 PATH——AI 任务必须用完整路径"},
            {"cmd": "pip", "expect": r"G:\workIns\conda\envs\pytorch",
             "note": "PATH 的 pip 属于 base/3.14；给 AI 环境装包用 python -m pip"},
            {"cmd": "git", "expect": r"D:\wofkIns\Git\cmd",
             "note": "PATH 首个是 WorkBuddy 内置 PortableGit；手动 Git 在 D:\\wofkIns\\Git"},
            {"cmd": "conda", "expect": r"D:\wofkIns\anaconda3\Scripts",
             "note": "PATH 里的 Conda 是 D 盘 base（仅 base 环境；AI 环境在 G 盘）"},
            {"cmd": "mvn", "expect": r"D:\wofkIns\apache-maven-3.9.9",
             "note": "mvn 与 mvn.cmd 同时存在属正常"},
            {"cmd": "node", "expect": r"C:\Users\marco\.workbuddy\binaries\node",
             "note": "PATH 首个是 WorkBuddy 内置 node 22；D 盘另有一套"},
            {"cmd": "npm", "expect": r"C:\Users\marco\.workbuddy\binaries\node",
             "note": "npm 与 npm.cmd 同时存在属正常"},
            {"cmd": "java", "expect": r"D:\wofkIns\jdk-17.0.0.1", "note": "唯一 JDK 17"},
        ],

        # ── 环境变量：只读展示 + 与预期比对（值来自 os.environ）──────────
        "env_vars": [
            {"name": "HF_HOME", "expect": r"G:\study\AI\cache\huggingface", "note": "模型/数据集缓存位置"},
            {"name": "HF_ENDPOINT", "expect": "https://hf-mirror.com", "note": "HF 镜像源，加速下载"},
            {"name": "JAVA_HOME", "expect": r"D:\wofkIns\jdk-17.0.0.1", "note": "Java 开发工具路径"},
            {"name": "MAVEN_HOME", "expect": r"D:\wofkIns\apache-maven-3.9.9", "note": ""},
            {"name": "PATH", "expect": "", "note": "太长不全文展示；PATH 中命令解析见「PATH 真相」面板"},
        ],

        # ── 常用命令库（一键复制；仅文本，不自动执行）────────────────────
        # 来源：本机环境手册（事实源）+ 各工具官方文档常用命令。
        # 约定：note 里标注「需管理员」「未安装」「PATH 外」等，避免误用。
        "command_lib": [
            {"group": "① 服务启停（CMD / 需管理员）", "items": [
                {"cmd": "net start SunshineService", "note": "启动串流服务"},
                {"cmd": "net stop SunshineService", "note": "停止串流服务"},
                {"cmd": "net start Tailscale", "note": "启动 Tailscale 组网"},
                {"cmd": "net stop Tailscale", "note": "停止 Tailscale"},
                {"cmd": "net start MySQL", "note": "启动 MySQL 5.7（3306）"},
                {"cmd": "net start mysql80", "note": "启动 MySQL 8.0（3307，推荐）"},
                {"cmd": "net stop mysql80", "note": "停止 MySQL 8.0"},
                {"cmd": "services.msc", "note": "打开服务图形界面（无需管理员即可查看）"},
            ]},
            {"group": "② 服务启停（PowerShell 替代）", "items": [
                {"cmd": "Start-Service mysql80", "note": "启动服务（可换 MySQL/Tailscale）"},
                {"cmd": "Stop-Service mysql80", "note": "停止服务"},
                {"cmd": "Get-Service MySQL, mysql80", "note": "查看 MySQL 两服务状态"},
                {"cmd": "Restart-Service mysql80", "note": "重启服务"},
            ]},
            {"group": "③ MySQL（客户端不在 PATH，写全路径）", "items": [
                {"cmd": r'"D:\wofkIns\mysql\mysql-8.0.29-ini\bin\mysql.exe" -u root -p -P 3307', "note": "连 8.0（3307，推荐）"},
                {"cmd": r'"D:\wofkIns\mysql\mysql-5.7.19-ini\bin\mysql.exe" -u root -p -P 3306', "note": "连 5.7（3306）"},
                {"cmd": "SELECT VERSION();", "note": "登录后：看版本"},
                {"cmd": "SHOW DATABASES;", "note": "登录后：看数据库"},
                {"cmd": "CREATE DATABASE demo DEFAULT CHARACTER SET utf8mb4;", "note": "登录后：建库（用 utf8mb4 支持 emoji）"},
            ]},
            {"group": "④ Java / JDK（17.0.0.1，PATH 外）", "items": [
                {"cmd": r'"D:\wofkIns\jdk-17.0.0.1\bin\java.exe" -version', "note": "看版本（输出在 stderr）"},
                {"cmd": r'"D:\wofkIns\jdk-17.0.0.1\bin\javac.exe" -version', "note": "看编译器版本"},
                {"cmd": "echo %JAVA_HOME%", "note": "CMD 查看 JAVA_HOME（Git Bash 用 echo $JAVA_HOME）"},
                {"cmd": "javac -encoding UTF-8 Main.java", "note": "显式 UTF-8 编译，避免 GBK 乱码"},
            ]},
            {"group": "⑤ Maven（3.9.9，PATH 外）", "items": [
                {"cmd": r'"D:\wofkIns\apache-maven-3.9.9\bin\mvn.cmd" -version', "note": "看版本"},
                {"cmd": "mvn clean package", "note": "清理并打包"},
                {"cmd": "mvn -DskipTests package", "note": "跳过测试打包"},
                {"cmd": "mvn dependency:tree", "note": "查看依赖树"},
                {"cmd": "mvn help:evaluate -Dexpression=settings.localRepository -q -DforceStdout", "note": "看本地仓库实际路径"},
            ]},
            {"group": "⑥ Node.js / npm（v22.22.2，PATH 中）", "items": [
                {"cmd": "node -v && npm -v && npx -v", "note": "一次看三个版本"},
                {"cmd": "npm config get registry", "note": "看当前镜像源"},
                {"cmd": "npm config set registry https://registry.npmmirror.com/", "note": "切淘宝镜像（改回用 npmjs.org）"},
                {"cmd": "npm ls -g --depth=0", "note": "列出全局包"},
                {"cmd": "npm init -y && npm install", "note": "初始化并安装依赖"},
                {"cmd": "corepack enable", "note": "启用 yarn/pnpm 支持"},
            ]},
            {"group": "⑦ Python（多版本，注意 PATH 优先级）", "items": [
                {"cmd": "where python", "note": "看 PATH 里所有 python（首个生效）"},
                {"cmd": "python -c \"import sys;print(sys.executable)\"", "note": "看当前 python 到底是哪个"},
                {"cmd": "py -0p", "note": "列出所有 py launcher 注册的 Python"},
                {"cmd": "python -m pip -V", "note": "确认 pip 属于哪个解释器"},
                {"cmd": "python -m pip install <包名>", "note": "推荐：确保装到当前解释器"},
                {"cmd": "python -m venv .venv", "note": "建虚拟环境隔离"},
            ]},
            {"group": "⑧ Conda（两套：D 盘 PATH 中 / G 盘 AI 用）", "items": [
                {"cmd": "conda env list", "note": "列出 Conda 环境"},
                {"cmd": "conda info", "note": "看 Conda 配置信息"},
                {"cmd": r'"D:\wofkIns\anaconda3\Scripts\conda.exe" env list', "note": "指定 D 盘 Conda（PATH 中那套）"},
                {"cmd": r"conda activate G:\workIns\conda\envs\pytorch", "note": "激活 G 盘 AI 环境（已实测可行）"},
                {"cmd": "conda create -n myenv python=3.11 -y", "note": "新建环境"},
                {"cmd": "conda deactivate", "note": "退出当前环境"},
            ]},
            {"group": "⑨ AI / PyTorch / HuggingFace（G 盘 pytorch 环境）", "items": [
                {"cmd": "nvidia-smi", "note": "看 GPU / 显存占用"},
                {"cmd": r'G:\workIns\conda\envs\pytorch\python.exe -c "import torch;print(torch.__version__,torch.cuda.is_available())"', "note": "验证 torch 与 CUDA"},
                {"cmd": r'G:\workIns\conda\envs\pytorch\python.exe -c "import transformers;print(transformers.__version__)"', "note": "验证 transformers"},
                {"cmd": r'G:\workIns\conda\envs\pytorch\python.exe -m pip list', "note": "查 AI 环境已装包"},
                {"cmd": "echo %HF_HOME%", "note": "看 HF 缓存目录（应为 G:\\study\\AI\\cache\\huggingface）"},
                {"cmd": "echo %HF_ENDPOINT%", "note": "看 HF 镜像源（应为 hf-mirror.com）"},
            ]},
            {"group": "⑩ Git（官方 cheat sheet 常用）", "items": [
                {"cmd": r'"D:\wofkIns\Git\cmd\git.exe" status', "note": "指定手动 Git（非 WorkBuddy 内置）"},
                {"cmd": "git add . && git commit -m \"msg\"", "note": "暂存并提交"},
                {"cmd": "git log --oneline -10", "note": "最近 10 条提交"},
                {"cmd": "git switch -c feature-x", "note": "新建并切换分支"},
                {"cmd": "git fetch && git pull", "note": "拉取远程更新"},
                {"cmd": "git push origin main", "note": "推送到远程"},
                {"cmd": "git stash", "note": "暂存当前改动"},
                {"cmd": "git config --global user.name", "note": "查看全局用户名"},
            ]},
            {"group": "⑪ IDE（VSCode / IDEA）", "items": [
                {"cmd": "code .", "note": "用 VSCode 打开当前目录"},
                {"cmd": "code --list-extensions", "note": "列出已装扩展"},
                {"cmd": "code --install-extension <ext>", "note": "安装扩展"},
                {"cmd": "idea64.exe", "note": "启动 IntelliJ IDEA Ultimate"},
            ]},
            {"group": "⑫ Tailscale 组网（PATH 外，写全路径）", "items": [
                {"cmd": r'"F:\Game\tailscale\tailscale.exe" status', "note": "查看组网节点"},
                {"cmd": r'"F:\Game\tailscale\tailscale.exe" ip', "note": "看本机组网 IP（100.75.245.81）"},
                {"cmd": r'"F:\Game\tailscale\tailscale.exe" up', "note": "上线"},
                {"cmd": r'"F:\Game\tailscale\tailscale.exe" down', "note": "下线"},
            ]},
            {"group": "⑬ .NET（仅运行时，无 SDK）", "items": [
                {"cmd": "dotnet --info", "note": "看 SDK / 运行时总览"},
                {"cmd": "dotnet --list-runtimes", "note": "列出运行时（当前 7.0.20 / 9.0.22）"},
                {"cmd": "dotnet --list-sdks", "note": "列出 SDK（当前为空，需装 SDK 才能开发）"},
            ]},
            {"group": "⑭ 端口 / 网络排查", "items": [
                {"cmd": "netstat -ano | findstr LISTENING", "note": "CMD：所有监听端口与 PID"},
                {"cmd": "netstat -ano | findstr :8080", "note": "CMD：查某端口被谁占用"},
                {"cmd": "Get-NetTCPConnection -LocalPort 3306", "note": "PowerShell：查端口占用"},
                {"cmd": "ipconfig /all", "note": "看全部网络配置"},
                {"cmd": "ping 100.75.245.81", "note": "测试本机 Tailscale IP 连通"},
            ]},
            {"group": "⑮ 系统 / 进程排查", "items": [
                {"cmd": "tasklist", "note": "列出所有进程"},
                {"cmd": "tasklist | findstr python", "note": "找残留的 python 进程"},
                {"cmd": "wmic process where \"name='python.exe'\" get ProcessId,CommandLine", "note": "看 python 进程命令行（找重复 Web）"},
                {"cmd": "systeminfo", "note": "看系统完整信息"},
            ]},
            {"group": "⑯ 未安装软件（备查，运行会报错）", "items": [
                {"cmd": "docker --version", "note": "Docker 未安装"},
                {"cmd": "gradle -version", "note": "Gradle 未装（建议用项目 gradlew）"},
                {"cmd": "ollama --version", "note": "Ollama 未安装（默认端口 11434）"},
                {"cmd": "dotnet new console", "note": ".NET 无 SDK，当前会失败"},
            ]},
            {"group": "⑰ AI 工具目录（子路径待实机复核）", "items": [
                {"cmd": "dir D:\\softIns", "note": "WorkBuddy/千问/豆包 安装目录一览（事实源 B4）"},
                {"cmd": "dir \"D:\\Program Files (x86)\\Trae CN\"", "note": "Trae CN 安装目录（B3 实测）"},
                {"cmd": "dir C:\\Users\\marco\\.workbuddy", "note": "WorkBuddy 数据目录（内置 node/python 在 binaries）"},
            ]},
            {"group": "⑱ 解压缩（Win10+ 自带 tar / PowerShell）", "items": [
                {"cmd": "tar -czf a.tgz 目录", "note": "打包（Win10+ 自带 tar）"},
                {"cmd": "tar -xzf a.tgz -C 目标目录", "note": "解压到指定目录"},
                {"cmd": "tar -tf a.tgz", "note": "只看内容不解压"},
                {"cmd": "Compress-Archive 目录 a.zip", "note": "PowerShell 打 zip"},
                {"cmd": "Expand-Archive a.zip -DestinationPath 目标", "note": "PowerShell 解 zip"},
            ]},
        ],

        # ── 关键进程检测：扫描这些关键字的进程（避免重复启动 Web）────────
        "watch_processes": ["web.py", "webctl.py", "serve_api.py"],
    },
}

# =============================================================================
# macOS 档案（Apple M2 MacBook Air）—— 2026-11-17 用 mac/collect_mac.py 实测采集
# 采集原始数据：mac/mac_profile.json；重采：python3 mac/collect_mac.py
# =============================================================================
PROFILE_MAC = {
    # ── 1. 身份 ───────────────────────────────────────────────────
    "name": "本机开发环境（Mac）",
    "short": "env",
    "desc": "macOS 本机环境 · 版本 / 路径 / 服务 / 端口 一条龙速查",
    "docs_title": "本机开发环境速查（Mac）",

    # ── 2. 路径 ───────────────────────────────────────────────────
    "paths": {
        "project": ".",
        "artifacts": "",
        "data": "",
        "notes": "notes",
        "web": "web",
        "cache": "",
    },

    # ── 3. 环境 / 版本探测 ────────────────────────────────────────
    "env": {
        "python_exe": "/Users/masc/miniconda3/envs/pytorch/bin/python",
        "disk_drive": "/",          # 体检关注根卷剩余
        "mirror_host": "",
        "mirror_url": "",
        "versions": [
            {"label": "Python", "expect_major": "3",
             "probe": "import sys; print(sys.version.split()[0])"},

            {"label": "JDK", "expect_major": "17",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home/bin/java","-version"],capture_output=True,text=True,timeout=25)
    _m=_re.search(r'"([0-9][^"]*)"',(_r.stdout or "")+(_r.stderr or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "Maven", "expect_major": "3",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["/opt/homebrew/bin/mvn","-version"],capture_output=True,text=True,timeout=30)
    _m=_re.search(r"Apache Maven ([0-9][^ ]*)",(_r.stdout or "")+(_r.stderr or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "Node.js", "expect_major": "22",
             "probe": '''import subprocess as _sp
try:
    _r=_sp.run(["/Users/masc/.workbuddy/binaries/node/versions/22.22.2-6/bin/node","-v"],capture_output=True,text=True,timeout=20)
    print((_r.stdout or "").strip().lstrip("v") or "-")
except Exception:
    print("-")'''},

            {"label": "npm", "expect_major": "10",
             "probe": '''import subprocess as _sp
try:
    _r=_sp.run(["/Users/masc/.workbuddy/binaries/node/versions/22.22.2-6/bin/npm","-v"],capture_output=True,text=True,timeout=20)
    print((_r.stdout or "").strip().splitlines()[0] or "-")
except Exception:
    print("-")'''},

            {"label": "Git", "expect_major": "2",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["/opt/homebrew/bin/git","--version"],capture_output=True,text=True,timeout=20)
    _m=_re.search(r"git version ([0-9][^ ]*)",(_r.stdout or "")+(_r.stderr or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "Conda", "expect_major": "26",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["/Users/masc/miniconda3/bin/conda","--version"],capture_output=True,text=True,timeout=25)
    _m=_re.search(r"conda\\s+([0-9][^\\s]*)",(_r.stdout or "")+(_r.stderr or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "torch", "expect_major": "2",
             "probe": "import torch; print(torch.__version__)"},
            {"label": "transformers", "expect_major": "5",
             "probe": "import transformers; print(transformers.__version__)"},
            {"label": "Flask", "expect_major": "3",
             "probe": "import flask; print(flask.__version__)"},

            {"label": "Go", "expect_major": "1",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["/opt/homebrew/bin/go","version"],capture_output=True,text=True,timeout=25)
    _m=_re.search(r"go([0-9][^ ]*)",(_r.stdout or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "Deno", "expect_major": "2",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["/opt/homebrew/bin/deno","--version"],capture_output=True,text=True,timeout=20)
    _m=_re.search(r"deno ([0-9][^ ]*)",(_r.stdout or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "ffmpeg", "expect_major": "8",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["/opt/homebrew/bin/ffmpeg","-version"],capture_output=True,text=True,timeout=25)
    _m=_re.search(r"version ([0-9][^ ]*)",(_r.stdout or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "Ollama", "expect_major": "0",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["/usr/local/bin/ollama","--version"],capture_output=True,text=True,timeout=20)
    _m=_re.search(r"version is ([0-9][^ ]*)",(_r.stdout or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "Homebrew", "expect_major": "5",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["/opt/homebrew/bin/brew","--version"],capture_output=True,text=True,timeout=25)
    _m=_re.search(r"Homebrew ([0-9][^ ]*)",(_r.stdout or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},

            {"label": "clang (Xcode CLT)", "expect_major": "2",
             "probe": '''import subprocess as _sp, re as _re
try:
    _r=_sp.run(["/usr/bin/clang","--version"],capture_output=True,text=True,timeout=20)
    _m=_re.search(r"clang version ([0-9][^ ]*)",(_r.stdout or ""))
    print(_m.group(1) if _m else "-")
except Exception:
    print("-")'''},
        ],
        # Mac 无 NVIDIA CUDA；M 系列 MPS 后端等价物，探测它
        "gpu": {
            "probe": "import torch; print('TRUE' if getattr(torch.backends, 'mps', None) and torch.backends.mps.is_available() else 'FALSE')",
            "name_probe": "import torch; print('Apple MPS' if torch.backends.mps.is_available() else '-')",
        },
    },

    # ── 4. 服务：本主题无推理脚本服务 ─────────────────────────────
    "serve": {"enabled": False},
    "web_port": 8010,               # 与 Windows 侧保持一致

    # ── 5. 数据 / 产物 / 曲线：本主题均不适用（留空）──────────────
    "data": {"files": [], "sample_file": "", "sample_col": "",
             "label_source": "", "label_note": "本机开发环境主题无数据集；服务/端口见「服务与端口」面板。"},
    "artifacts": {
        "meanings": {}, "must_exist": [], "metrics_files": [],
        "history_file": "", "history_key": "", "curve_metrics": [], "x_key": "step",
    },

    # ── 6. 缓存占用（只读，全部 safe=False，不提供删除系统缓存）──
    # 2026-11-17 依据 mac_profile.json 核对：HF_HOME 未设置→默认 ~/.cache/huggingface、
    # 无 .npmrc→npm 缓存默认 ~/.npm，均正确；补 Homebrew/Go/Deno 三处遗漏
    "cache": {"items": [
        {"name": "Conda pkgs 包缓存", "path": "/Users/masc/miniconda3/pkgs", "safe": False,
         "note": "conda 安装包的缓存；确认环境不再需要后再清（conda clean -p）"},
        {"name": "HF 模型缓存", "path": "/Users/masc/.cache/huggingface", "safe": False,
         "note": "模型/数据集缓存（HF_HOME 未设置，走此默认位置），删除后需重新下载"},
        {"name": "Ollama 模型", "path": "/Users/masc/.ollama", "safe": False,
         "note": "本地大模型文件（ollama rm <模型> 删除单个）"},
        {"name": "Homebrew 下载缓存", "path": "/Users/masc/Library/Caches/Homebrew", "safe": False,
         "note": "72 个 formula + 2 个 cask 的下载缓存，可 brew cleanup 清理"},
        {"name": "Go 模块缓存", "path": "/Users/masc/go/pkg/mod", "safe": False,
         "note": "go get 下载的依赖；清理：go clean -modcache"},
        {"name": "Deno 缓存", "path": "/Users/masc/Library/Caches/deno", "safe": False,
         "note": "deno 2.8.3 的依赖/编译缓存；清理：deno cache --reload 或删目录"},
        {"name": "npm 缓存", "path": "/Users/masc/.npm", "safe": False,
         "note": "Node 包下载缓存；清理：npm cache clean --force"},
        {"name": "pip 缓存", "path": "/Users/masc/Library/Caches/pip", "safe": False,
         "note": "Python 包下载缓存；清理：pip cache purge"},
    ]},

    # ── 7. recap 核心速记 ─────────────────────────────────────────
    "recap": {
        "core": "本机事实：mac/mac_profile.json（2026-11-17 采集）+ notes/09-Mac环境速查.md\n"
                "AI 解释器只有 /Users/masc/miniconda3/envs/pytorch/bin/python（torch 2.11 / transformers 5.8 / MPS 可用）\n"
                "PATH 里 python3 有 4 套（WorkBuddy 3.13.12 / miniconda3 3.13.13 / Homebrew 3.14.6 / 系统 3.9.6）\n"
                "装包一律 python -m pip；AI 任务先 conda activate pytorch 或写全路径",
        "rules": [
            "AI 任务固定用 miniconda3 的 pytorch 环境（MPS 加速）；PATH 里的 python3 都没有 torch",
            "Ollama 常驻运行占 11434；另有本地 python API 占 11435——调试端口先排查它们",
            "5000/7000 被 macOS ControlCenter（AirPlay）占用，起服务避开",
            "HTTP(S)_PROXY 指向本机代理工具，端口随代理客户端变化；pip/git 走代理异常先查它",
            "Homebrew 装的软件在 /opt/homebrew（arm64 标准位置），JDK17/Maven/Go/ffmpeg 都来自 brew",
            "/usr/libexec/java_home 默认返回 Temurin 8（x86_64，唯一注册的 JVM）；日常 JDK 17 来自 Homebrew，JAVA_HOME 已指向 17",
            "Tailscale 已安装但默认不随开机启动；需要组网先 open -a Tailscale（Windows 侧则是常驻 Running）",
            "验证软件是否就绪用三层法：①有没有 → ②环境齐不齐 → ③跑个最小任务",
        ],
        "commands_note": "忘记先看 env status / env recap；服务端口看 Web「服务与端口」；重采环境：python3 mac/collect_mac.py。",
    },

    "extra_checks": [],
    "question_module": "question_bank.py",

    # ── 8. 主题定制字段 ──────────────────────────────────────────
    "ui": {
        "sections": ["status", "info", "pathtruth", "envvars", "software", "aitools", "servicesvc",
                     "ports_live", "processes", "test", "doctor", "cmdlib", "cache", "docs"],
    },
    "facts": {
        "ai_tools": [
            {
                "name": "WorkBuddy（腾讯）", "version": "5.11.3",
                "app": "/Applications/WorkBuddy.app",
                "home": "~/.workbuddy", "size": "995 MB",
                "items": [
                    {"name": "云档案/人格记忆", "path": "~/.workbuddy/user-b616c829-499f-47e2-a2da-1c885f809084-personal/", "note": "IDENTITY/USER/SOUL.md，服务端管理"},
                    {"name": "本地长期记忆", "path": "~/.workbuddy/memory/", "note": "<user-id>_memory.md"},
                    {"name": "工作区记忆", "path": "~/study/AI/WorkBuddy/env/.workbuddy/memory/", "note": "随项目走（本项目日志/笔记）"},
                    {"name": "MCP 配置", "path": "~/.workbuddy/mcp.json"},
                    {"name": "技能 skills", "path": "~/.workbuddy/skills/"},
                    {"name": "连接器 connectors", "path": "~/.workbuddy/connectors/"},
                    {"name": "内置运行时 binaries", "path": "~/.workbuddy/binaries/", "note": "456MB（node 等）"},
                ],
                "note": "本控制台项目本身就是 WorkBuddy 工作项目（~/study/AI/WorkBuddy）",
            },
            {
                "name": "ChatGPT / Codex（OpenAI）", "version": "26.915.31945",
                "app": "/Applications/ChatGPT.app",
                "home": "~/.codex", "size": "1.1 GB",
                "items": [
                    {"name": "Codex CLI 配置", "path": "~/.codex/config.toml", "note": "模型 gpt-5.6-terra、sandbox=workspace-write、reasoning=low"},
                    {"name": "全局指令 AGENTS.md", "path": "~/.codex/AGENTS.md"},
                    {"name": "会话记录", "path": "~/.codex/sessions/", "note": "233MB，36 个会话（按年/月归档）"},
                    {"name": "记忆体", "path": "~/.codex/memories/", "note": "当前 0B（config.toml features.memories=false 未启用）"},
                    {"name": "桌面端数据", "path": "~/Library/Application Support/com.openai.chat/", "note": "仅 208KB，会话主体在云端"},
                ],
                "note": "MCP 在 config.toml 的 [mcp_servers]（node_repl，随 app 内置 node）",
            },
            {
                "name": "Qoder（阿里）", "version": "QoderWork CN 0.6.7",
                "app": "/Applications/QoderWork CN.app",
                "home": "~/.qoder", "size": "115 MB",
                "items": [
                    {"name": "设置", "path": "~/.qoder/settings.json", "note": "enabledPlugins / security"},
                    {"name": "记忆体", "path": "~/.qoder/memories/019e5bba/", "note": "global + projects 两级"},
                    {"name": "项目登记", "path": "~/.qoder/projects/-Users-masc-Code-Java-project-projectUnit", "note": "Java 项目 projectUnit"},
                    {"name": "技能/插件/扩展", "path": "~/.qoder/skills/"},
                ],
                "note": "VSCode 系目录结构",
            },
            {
                "name": "Trae（字节）", "version": "Trae CN 3.4.20",
                "app": "/Applications/Trae CN.app",
                "home": "~/Library/Application Support/Trae CN", "size": "392 MB",
                "items": [
                    {"name": "IDE 设置", "path": "~/Library/Application Support/Trae CN/User/settings.json"},
                    {"name": "MCP 配置", "path": "~/Library/Application Support/Trae CN/User/mcp.json", "note": "apple shortcuts、Time 等（带画廊 ID）"},
                    {"name": "工作区存储", "path": "~/Library/Application Support/Trae CN/User/workspaceStorage/"},
                    {"name": "SOLO 模式数据", "path": "~/Library/Application Support/TRAE SOLO CN/", "note": "⚠️ 4.2GB（ModularData 3.3G + Partitions 537M）"},
                ],
                "note": "SOLO 数据是本机 AI 工具里最大磁盘占用，清理优先看这里",
            },
            {
                "name": "千问办公 QwenWork（阿里）", "version": "1.3.2",
                "app": "/Applications/QwenWorkCN.app",
                "home": "~/Library/Application Support/QwenWorkCN", "size": "29 MB（应用本体 1.3GB）",
                "items": [
                    {"name": "应用数据", "path": "~/Library/Application Support/QwenWorkCN/", "note": "Chromium 系：Local Storage/Preferences/Partitions"},
                    {"name": "智能体技能 skills", "path": "~/.qwen/skills/", "note": "29 个 lark-*（飞书审批/多维表格/日历/通讯录等集成）"},
                    {"name": "运行标识", "path": "~/.qwen/installation_id"},
                    {"name": "输出语言偏好", "path": "~/.qwen/output-language.md"},
                    {"name": "缓存", "path": "~/Library/Caches/cn.qwenwork.desktop.mac", "note": "约 80K"},
                    {"name": "本地服务端口", "note": "运行时监听 127.0.0.1:54365/54367/16799（随机分配，随启随灭，实时端口面板可见）"},
                ],
                "note": "阿里 AI 办公套件桌面端；运行时监听 3 个本地端口（实时端口面板可见）",
            },
            {
                "name": "千问 Qianwen（阿里）", "version": "5.2.0.298",
                "app": "/Applications/Qianwen.app",
                "home": "~/Library/Application Support/Qianwen", "size": "2.5GB（应用本体 1.3GB，缓存 648MB）",
                "items": [
                    {"name": "应用数据", "path": "~/Library/Application Support/Qianwen/", "note": "Chromium 系，2.5GB 是本机第二大 AI 工具磁盘占用"},
                    {"name": "缓存", "path": "~/Library/Caches/Qianwen/", "note": "648MB，清理优先看这里"},
                ],
                "note": "通义千问桌面客户端；与千问办公是两个独立应用（本机装了两个）",
            },
        ],
        # 关键路径（status 面板展示存在性）
        "paths": [
            {"name": "AI 环境解释器", "path": "/Users/masc/miniconda3/envs/pytorch/bin/python"},
            {"name": "Conda", "path": "/Users/masc/miniconda3/bin/conda"},
            {"name": "Homebrew", "path": "/opt/homebrew/bin/brew"},
            {"name": "JDK 17", "path": "/opt/homebrew/opt/openjdk@17"},
            {"name": "Maven", "path": "/opt/homebrew/bin/mvn"},
            {"name": "Git", "path": "/opt/homebrew/bin/git"},
            {"name": "Ollama", "path": "/usr/local/bin/ollama"},
            {"name": "Tailscale", "path": "/Applications/Tailscale.app"},
            {"name": "Xcode CLT", "path": "/Library/Developer/CommandLineTools"},
            {"name": "VSCode", "path": "/Applications/Visual Studio Code.app"},
            {"name": "Node.js（WorkBuddy 内置）", "path": "/Users/masc/.workbuddy/binaries/node/versions/22.22.2-6"},
            {"name": "Go", "path": "/opt/homebrew/bin/go"},
            {"name": "Deno", "path": "/opt/homebrew/bin/deno"},
            {"name": "ffmpeg", "path": "/opt/homebrew/bin/ffmpeg"},
            {"name": "控制台项目", "path": "/Users/masc/study/AI/WorkBuddy/env"},
        ],
        # 服务/常驻进程状态：macOS 无 net 服务，用 probe 命令实测（只读）
        "services": [
            {"name": "Ollama 本地大模型", "svc": "ollama", "expect": "Running",
             "probe": 'pgrep -f "Ollama serve" >/dev/null 2>&1 || pgrep -x ollama >/dev/null 2>&1 && echo Running || echo Stopped',
             "start": "open -a Ollama", "stop": "osascript -e 'quit app \"Ollama\"'",
             "note": "端口 11434；模型文件在 ~/.ollama"},
            {"name": "UU远程 GameViewer", "svc": "UURemote", "expect": "Running",
             "probe": "pgrep -f UURemote >/dev/null 2>&1 && echo Running || echo Stopped",
             "start": "open -a UURemote", "stop": "osascript -e 'quit app \"UURemote\"'",
             "note": "远程控制，端口 56352/56353"},
            {"name": "Tailscale 组网", "svc": "tailscale", "expect": "Stopped",
             "probe": "/usr/local/bin/tailscale status >/dev/null 2>&1 && echo Running || echo Stopped",
             "start": "open -a Tailscale", "stop": "osascript -e 'quit app \"Tailscale\"'",
             "note": "已安装但默认未运行（Windows 侧常驻）；CLI 在 /usr/local/bin/tailscale，组网 UDP 41641"},
            {"name": "KuliCloud 代理", "svc": "KuliCloud", "expect": "Running",
             "probe": "pgrep -x KuliCloud >/dev/null 2>&1 && echo Running || echo Stopped",
             "start": "open -a KuliCloud", "stop": "osascript -e 'quit app \"KuliCloud\"'",
             "note": "代理工具，本地混合端口 7892（HTTP(S)_PROXY 指向它，端口会变）"},
            {"name": "WorkBuddy 桌面端", "svc": "WorkBuddy", "expect": "Running",
             "probe": "pgrep -f 'WorkBuddy.app' >/dev/null 2>&1 && echo Running || echo Stopped",
             "start": "open -a WorkBuddy", "stop": "osascript -e 'quit app \"WorkBuddy\"'",
             "note": "AI 助手宿主（本控制台常由它拉起）；⚠️ 停止会结束依赖它的 AI 会话"},
            {"name": "控制台 Web（8010）", "svc": "envweb", "expect": "按需",
             "probe": "lsof -nP -iTCP:8010 -sTCP:LISTEN >/dev/null 2>&1 && echo Running || echo Stopped",
             "start": "双击 启动Web控制台.command（或 cd 项目根 && python engine/web.py）",
             "stop": "kill $(lsof -ti:8010)",
             "note": "本环境控制台；⚠️ 停止即关闭当前打开的控制台页面"},
            {"name": "Homebrew 托管服务", "svc": "brew", "expect": "无",
             "probe": "c=$(brew services list 2>/dev/null | tail -n +2 | grep -c started); [ \"$c\" = \"0\" ] && echo 无 || echo \"共${c}个在跑\"",
             "start": "brew services start <名>", "stop": "brew services stop <名>",
             "note": "当前无 brew services 托管的服务"},
        ],
        # 常驻端口快照（mac_profile.json 2026-11-17 实测）
        "ports": [
            {"port": "11434", "proto": "TCP", "use": "Ollama 本地大模型", "state": "监听中"},
            {"port": "11435", "proto": "TCP", "use": "本地 Python API（临时）", "state": "临时，已停止"},
            {"port": "5000 / 7000", "proto": "TCP", "use": "macOS ControlCenter（AirPlay）", "state": "系统占用"},
            {"port": "7892", "proto": "TCP", "use": "KuliCloud 代理工具", "state": "监听中"},
            {"port": "56352 / 56353", "proto": "TCP", "use": "UU远程 GameViewer", "state": "监听中"},
            {"port": "41641", "proto": "UDP", "use": "Tailscale 组网（未运行）", "state": "未监听"},
            {"port": "8010", "proto": "TCP", "use": "控制台 Web", "state": "按需（控制台运行时监听）"},
            # 说明：18488/39099/5 万段等高随机端口是编辑器/沙箱/系统临时会话，随启随灭，不列入快照
        ],
        # 磁盘快照（2026-11-17 实测，全机单卷 APFS）
        "disks": [
            {"drive": "/（Macintosh HD）", "free_gb": 164.0, "note": "总 460GB，空间充足"},
        ],

        # ── 基础信息：配置文件路径（2026-11-17 实测存在性）────────
        "config_files": [
            {"name": "控制台配置", "path": "/Users/masc/study/AI/WorkBuddy/env/config.py",
             "note": "两平台档案都在这里；Mac 事实在 PROFILE_MAC"},
            {"name": "Git 全局配置", "path": "/Users/masc/.gitconfig", "note": "user.name/email 等"},
            {"name": "zsh 配置", "path": "/Users/masc/.zshrc", "note": "别名/PATH 导出"},
            {"name": "zprofile", "path": "/Users/masc/.zprofile", "note": "登录 shell 环境（conda init 在这）"},
            {"name": "SSH 配置", "path": "/Users/masc/.ssh/config", "note": "主机别名/密钥"},
            {"name": "SSH 密钥", "path": "/Users/masc/.ssh/id_ed25519", "note": "已存在（另有 id_rsa）；git 身份 marco_masc <marco_masc@outlook.com>"},
            {"name": "VSCode 扩展目录", "path": "/Users/masc/.vscode/extensions", "note": "48 个扩展"},
            {"name": "Maven settings.xml", "path": "/Users/masc/.m2/settings.xml", "note": "存在（镜像/仓库配置）"},
            {"name": "WorkBuddy MCP 配置", "path": "/Users/masc/.workbuddy/mcp.json", "note": "自定义 MCP 服务"},
            {"name": "VSCode 用户设置", "path": "/Users/masc/Library/Application Support/Code/User/settings.json", "note": ""},
            {"name": "hosts 文件", "path": "/etc/hosts", "note": "修改需 sudo"},
        ],

        # ── 基础信息：产物 / 工作目录路径 ──────────────────────────
        "products": [
            {"name": "AI 环境解释器", "path": "/Users/masc/miniconda3/envs/pytorch/bin/python",
             "note": "torch 2.11 / transformers 5.8，唯一带 AI 库的 Python（MPS 加速）"},
            {"name": "AI 环境 site-packages", "path": "/Users/masc/miniconda3/envs/pytorch/lib/python3.13/site-packages",
             "note": "AI 环境的第三方包装在这里"},
            {"name": "Conda envs", "path": "/Users/masc/miniconda3/envs",
             "note": "base / llm / pytorch 三个环境"},
            {"name": "HF 模型缓存", "path": "/Users/masc/.cache/huggingface", "note": "删除后需重下"},
            {"name": "Ollama 模型", "path": "/Users/masc/.ollama", "note": "本地大模型文件"},
            {"name": "Maven 本地仓库", "path": "/Users/masc/.m2/repository", "note": "Java 依赖产物"},
            {"name": "pip 缓存", "path": "/Users/masc/Library/Caches/pip", "note": "Python 包下载缓存（清理：pip cache purge）"},
            {"name": "npm 缓存", "path": "/Users/masc/.npm", "note": "Node 包下载缓存（清理：npm cache clean --force）"},
            {"name": "Go 模块缓存", "path": "/Users/masc/go/pkg/mod", "note": "go get 下载的依赖（清理：go clean -modcache）"},
            {"name": "控制台速查文档", "path": "notes", "note": "跨平台复习/查询文档"},
        ],

        # ── 软件状态：开发工具 + 运行时（版本实时探测）────────────
        "software": [
            {"name": "JDK 17", "probe_label": "JDK", "path": "/opt/homebrew/opt/openjdk@17",
             "category": "开发", "start": "java -version", "note": "Homebrew openjdk@17（17.0.17）"},
            {"name": "Maven 3.9", "probe_label": "Maven", "path": "/opt/homebrew/bin/mvn",
             "category": "开发", "start": "mvn -v", "note": "Homebrew maven 3.9.12"},
            {"name": "Node.js 22", "probe_label": "Node.js", "path": "/Users/masc/.workbuddy/binaries/node/versions/22.22.2-6",
             "category": "开发", "start": "node -v", "note": "WorkBuddy 内置 node；brew 也装了 node"},
            {"name": "npm 10", "probe_label": "npm", "path": "/Users/masc/.workbuddy/binaries/node/versions/22.22.2-6/bin/npm",
             "category": "开发", "start": "npm -v", "note": ""},
            {"name": "Git", "probe_label": "Git", "path": "/opt/homebrew/bin/git",
             "category": "开发", "start": "git --version", "note": "Homebrew git 2.51.2"},
            {"name": "Go", "probe_label": "", "path": "/opt/homebrew/bin/go",
             "category": "开发", "start": "go version", "note": "Homebrew go 1.26.4"},
            {"name": "Conda", "probe_label": "Conda", "path": "/Users/masc/miniconda3",
             "category": "环境", "start": "conda --version", "note": "miniconda3 26.3.2，envs: base/llm/pytorch"},
            {"name": "Python (AI 环境)", "probe_label": "Python", "path": "/Users/masc/miniconda3/envs/pytorch/bin/python",
             "category": "环境", "start": "conda activate pytorch", "note": "AI 任务固定用它，不在 PATH"},
            {"name": "PyTorch", "probe_label": "torch", "path": "/Users/masc/miniconda3/envs/pytorch/lib/python3.13/site-packages/torch",
             "category": "AI", "start": "python -c \"import torch;print(torch.__version__)\"", "note": "2.11.0；无 CUDA，用 MPS 后端"},
            {"name": "Transformers", "probe_label": "transformers", "path": "",
             "category": "AI", "start": "python -c \"import transformers;print(transformers.__version__)\"", "note": "5.8.0"},
            {"name": "Flask", "probe_label": "Flask", "path": "",
             "category": "AI", "start": "python -c \"import flask;print(flask.__version__)\"", "note": "Web 控制台依赖（3.1.3）"},
            {"name": "Ollama", "probe_label": "", "path": "/usr/local/bin/ollama",
             "category": "AI", "start": "open -a Ollama", "note": "0.40.16 常驻运行，端口 11434"},
            {"name": "Homebrew", "probe_label": "", "path": "/opt/homebrew/bin/brew",
             "category": "工具", "start": "brew --version", "note": "5.0.8，72 个 formula"},
            {"name": "ffmpeg", "probe_label": "", "path": "/opt/homebrew/bin/ffmpeg",
             "category": "工具", "start": "ffmpeg -version", "note": "Homebrew 8.1.2"},
            {"name": "VSCode", "probe_label": "", "path": "/Applications/Visual Studio Code.app",
             "category": "工具", "start": "open -a 'Visual Studio Code'", "note": "code 命令不在 PATH，用 open -a"},
            {"name": "Tailscale", "probe_label": "", "path": "/Applications/Tailscale.app",
             "category": "工具", "start": "open -a Tailscale", "note": "1.104.7 已装未运行；CLI /usr/local/bin/tailscale"},
            {"name": "Deno", "probe_label": "", "path": "/opt/homebrew/bin/deno",
             "category": "开发", "start": "deno --version", "note": "Homebrew 2.8.3"},
            {"name": "Xcode CLT", "probe_label": "", "path": "/Library/Developer/CommandLineTools",
             "category": "开发", "start": "xcode-select -p", "note": "26.6，clang/系统 git 头文件"},
            {"name": "IntelliJ IDEA", "probe_label": "", "path": "/Applications/IntelliJ IDEA.app",
             "category": "开发", "start": "open -a 'IntelliJ IDEA'", "note": "2026.1.2，Java IDE"},
            {"name": "Postman", "probe_label": "", "path": "/Applications/Postman.app",
             "category": "工具", "start": "open -a Postman", "note": "11.81.4，接口调试"},
            {"name": "KuliCloud", "probe_label": "", "path": "/Applications/KuliCloud.app",
             "category": "工具", "start": "open -a KuliCloud", "note": "3.2.2，代理工具，本地混合端口 7892"},
            {"name": "UU远程 GameViewer", "probe_label": "", "path": "/Applications/UURemote.app",
             "category": "工具", "start": "open -a UURemote", "note": "4.46.0，远程控制；启停见「服务」面板，端口 56352/56353"},
            {"name": "千问办公 QwenWork", "probe_label": "", "path": "/Applications/QwenWorkCN.app",
             "category": "AI", "start": "open -a QwenWorkCN", "note": "1.3.2，阿里 AI 办公套件；技能库 ~/.qwen/skills；详情见「AI 工具」面板"},
            {"name": "千问 Qianwen", "probe_label": "", "path": "/Applications/Qianwen.app",
             "category": "AI", "start": "open -a Qianwen", "note": "5.2.0.298，通义千问桌面端；数据 2.5GB+缓存 648MB"},
            {"name": "Docker", "probe_label": "", "path": "/Applications/Docker.app",
             "category": "未安装", "start": "", "note": "尚未安装"},
            {"name": "Gradle", "probe_label": "", "path": "",
             "category": "未安装", "start": "", "note": "未装（建议用项目 gradlew）"},
            {"name": "wget", "probe_label": "", "path": "",
             "category": "未安装", "start": "", "note": "未装（用 curl 或 brew install wget）"},
        ],

        # ── PATH 真相：命令实际解析（which -a 实测）────────────────
        "path_commands": [
            {"cmd": "python3", "expect": ".workbuddy/binaries/python",
             "note": "PATH 里 4 套 python3；首个是 WorkBuddy 3.13.12，AI 解释器不在 PATH——AI 任务用 conda activate pytorch 或全路径"},
            {"cmd": "python", "expect": ".workbuddy/binaries/python",
             "note": "python 与 python3 同指向 WorkBuddy 内置版"},
            {"cmd": "git", "expect": "/opt/homebrew",
             "note": "Homebrew git；/usr/bin/git 是系统自带（Apple git）"},
            {"cmd": "conda", "expect": "/Users/masc/miniconda3/bin",
             "note": "miniconda3，由 zprofile 的 conda init 注入 PATH"},
            {"cmd": "java", "expect": "/opt/homebrew/opt/openjdk@17",
             "note": "Homebrew openjdk@17；JAVA_HOME 已指向这里"},
            {"cmd": "mvn", "expect": "/opt/homebrew/bin/mvn",
             "note": "Homebrew maven 3.9.12"},
            {"cmd": "node", "expect": ".workbuddy/binaries/node",
             "note": "PATH 首个是 WorkBuddy 内置 node 22；brew 另有一套"},
            {"cmd": "npm", "expect": ".workbuddy/binaries/node",
             "note": "与 node 同版本"},
            {"cmd": "brew", "expect": "/opt/homebrew/bin/brew",
             "note": "arm64 Homebrew 标准前缀"},
        ],

        # ── 环境变量：只读展示 + 与预期比对 ───────────────────────
        "env_vars": [
            {"name": "JAVA_HOME", "expect": "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home", "note": "Java 开发工具路径"},
            {"name": "CONDA_PREFIX", "expect": "/Users/masc/miniconda3", "note": "当前激活的 conda 环境（base）"},
            {"name": "HTTP_PROXY", "expect": "", "note": "本机代理工具动态设置，端口随代理客户端变化"},
            {"name": "HTTPS_PROXY", "expect": "", "note": "同上"},
            {"name": "HF_HOME", "expect": "", "note": "未设置——HF 缓存用默认 ~/.cache/huggingface"},
            {"name": "PATH", "expect": "", "note": "太长不全文展示；PATH 中命令解析见「PATH 真相」面板"},
        ],

        # ── 常用命令库（一键复制；仅文本，不自动执行）────────────────
        "command_lib": [
            {"group": "① Homebrew（/opt/homebrew）", "items": [
                {"cmd": "brew list --formula", "note": "列出已装命令行软件"},
                {"cmd": "brew search <关键词>", "note": "搜索可安装的软件"},
                {"cmd": "brew info <名>", "note": "看版本/依赖/占用说明（装前确认）"},
                {"cmd": "brew uninstall <名>", "note": "卸载（加 --zap 连配置一起清）"},
                {"cmd": "brew update && brew upgrade", "note": "更新 Homebrew 与全部软件"},
                {"cmd": "brew services list", "note": "查看 brew 托管的后台服务"},
                {"cmd": "brew cleanup", "note": "清理旧版本缓存"},
            ]},
            {"group": "② 服务 / 进程管理（macOS）", "items": [
                {"cmd": "launchctl list | head -30", "note": "用户域服务/代理列表"},
                {"cmd": "launchctl print gui/$(id -u) | head -40", "note": "当前用户会话详情（免 sudo）"},
                {"cmd": "pgrep -lf ollama", "note": "按名字找进程"},
                {"cmd": "open -a Ollama", "note": "启动 Ollama 应用"},
                {"cmd": "osascript -e 'quit app \"Ollama\"'", "note": "优雅退出 Ollama"},
                {"cmd": "ls ~/Library/LaunchAgents", "note": "用户自启动项"},
            ]},
            {"group": "③ 端口 / 网络排查", "items": [
                {"cmd": "lsof -nP -iTCP -sTCP:LISTEN", "note": "所有监听端口与进程"},
                {"cmd": "lsof -nP -iTCP:8010", "note": "看某端口被谁占用"},
                {"cmd": "lsof -t -iTCP:8010 -sTCP:LISTEN", "note": "按端口只列出 PID（进程号）"},
                {"cmd": "lsof -nP -iTCP:8010 -sTCP:LISTEN | awk 'NR>1{print $1, $2}'", "note": "端口 → 进程名 + PID 对照"},
                {"cmd": "ps -M <PID>", "note": "看某进程的线程列表（每线程一行；⚠️ 控制台沙箱内 ps 受限，请在终端执行）"},
                {"cmd": "netstat -an | grep LISTEN", "note": "按状态过滤连接"},
                {"cmd": "ifconfig | grep 'inet '", "note": "看本机 IP"},
                {"cmd": "curl -I https://hf-mirror.com", "note": "测外网连通（经代理）"},
            ]},
            {"group": "④ Java / JDK 17（Homebrew）", "items": [
                {"cmd": "java -version", "note": "看版本（输出在 stderr）"},
                {"cmd": "javac -version", "note": "看编译器版本"},
                {"cmd": "echo $JAVA_HOME", "note": "确认 JAVA_HOME（zsh）"},
                {"cmd": "/usr/libexec/java_home -V", "note": "macOS 官方：列出所有已装 JDK"},
            ]},
            {"group": "⑤ Maven（3.9.12，Homebrew）", "items": [
                {"cmd": "mvn -version", "note": "看版本与 Java 运行时"},
                {"cmd": "mvn clean package", "note": "清理并打包"},
                {"cmd": "mvn -DskipTests package", "note": "跳过测试打包"},
                {"cmd": "mvn dependency:tree", "note": "查看依赖树"},
            ]},
            {"group": "⑥ Node.js / npm（v22.22.2）", "items": [
                {"cmd": "node -v && npm -v", "note": "一次看两个版本"},
                {"cmd": "npm config get registry", "note": "看当前镜像源"},
                {"cmd": "npm config set registry https://registry.npmmirror.com/", "note": "切淘宝镜像（改回用 npmjs.org）"},
                {"cmd": "npm ls -g --depth=0", "note": "列出全局包"},
            ]},
            {"group": "⑦ Python / Conda（4 套 python3 并存）", "items": [
                {"cmd": "which -a python3", "note": "看 PATH 里所有 python3（首个生效）"},
                {"cmd": "python3 -c \"import sys;print(sys.executable)\"", "note": "看当前 python 到底是哪个"},
                {"cmd": "conda env list", "note": "列出 conda 环境（base/llm/pytorch）"},
                {"cmd": "conda activate pytorch", "note": "激活 AI 环境"},
                {"cmd": "python -m pip install <包名>", "note": "推荐：确保装到当前解释器"},
                {"cmd": "conda deactivate", "note": "退出当前环境"},
            ]},
            {"group": "⑧ AI / PyTorch（pytorch 环境，MPS 加速）", "items": [
                {"cmd": "conda activate pytorch && python -c \"import torch;print(torch.__version__, torch.backends.mps.is_available())\"",
                 "note": "验证 torch 与 MPS（True=可用）"},
                {"cmd": "python -c \"import transformers;print(transformers.__version__)\"", "note": "验证 transformers"},
                {"cmd": "python -m pip list", "note": "查 AI 环境已装包"},
                {"cmd": "python -c \"import importlib.metadata as m;print(m.version('flask'))\"", "note": "验证 Flask 版本（本机 3.1.3；⚠️ flask.__version__ 3.2 起移除，勿用）"},
                {"cmd": "cd <项目根> && python engine/web.py", "note": "启动本环境控制台（或双击 启动Web控制台.command）"},
                {"cmd": "lsof -nP -iTCP:8010 -sTCP:LISTEN", "note": "确认控制台端口已监听"},
                {"cmd": "system_profiler SPHardwareDataType | grep -E 'Chip|Memory'", "note": "看芯片与统一内存"},
            ]},
            {"group": "⑨ Ollama（0.40.16，端口 11434）", "items": [
                {"cmd": "ollama list", "note": "已下载的本地模型"},
                {"cmd": "ollama ps", "note": "正在运行的模型与显存占用"},
                {"cmd": "ollama run <模型名>", "note": "交互运行模型"},
                {"cmd": "curl http://127.0.0.1:11434/api/tags", "note": "API 方式看模型列表"},
            ]},
            {"group": "⑩ Git 常用", "items": [
                {"cmd": "git status", "note": "工作区状态"},
                {"cmd": "git add . && git commit -m \"msg\"", "note": "暂存并提交"},
                {"cmd": "git log --oneline -10", "note": "最近 10 条提交"},
                {"cmd": "git switch -c feature-x", "note": "新建并切换分支"},
                {"cmd": "git pull && git push", "note": "拉取远端并推送本地提交"},
                {"cmd": "git diff --stat", "note": "未提交改动的文件级概览"},
                {"cmd": "git config --global user.name", "note": "查看全局用户名"},
            ]},
            {"group": "⑪ Go（1.26.4，Homebrew）", "items": [
                {"cmd": "go version", "note": "查看 Go 版本（本机 1.26.4）"},
                {"cmd": "go env GOPATH GOROOT", "note": "工作区/安装根（GOPATH=~/go）"},
                {"cmd": "go mod init <模块名>", "note": "初始化新模块"},
                {"cmd": "go get <包路径>", "note": "添加依赖"},
                {"cmd": "go mod tidy", "note": "整理依赖（更新 go.mod/go.sum）"},
                {"cmd": "go build ./...", "note": "编译当前模块全部包"},
                {"cmd": "go run main.go", "note": "直接运行"},
                {"cmd": "go test ./...", "note": "跑全部测试"},
                {"cmd": "gofmt -w .", "note": "格式化代码"},
                {"cmd": "go vet ./...", "note": "静态检查"},
                {"cmd": "GOOS=windows GOARCH=amd64 go build", "note": "交叉编译 Windows 可执行文件"},
                {"cmd": "go env -w GOPROXY=https://goproxy.cn,direct", "note": "国内模块代理（本机未设，走系统代理）"},
            ]},
            {"group": "⑫ Deno / ffmpeg（brew 工具链）", "items": [
                {"cmd": "deno --version", "note": "Deno 版本（本机 2.8.3）"},
                {"cmd": "deno eval 'console.log(1)'", "note": "最小运行"},
                {"cmd": "deno run --allow-net <脚本>", "note": "跑脚本（按需授权）"},
                {"cmd": "deno info", "note": "缓存与配置路径"},
                {"cmd": "ffmpeg -version", "note": "ffmpeg 版本（本机 8.1.2）"},
                {"cmd": "ffmpeg -formats | head", "note": "查看支持的封装格式"},
                {"cmd": "ffmpeg -i in.mp4 out.gif", "note": "简单转码示例"},
            ]},
            {"group": "⑬ IDE / 系统", "items": [
                {"cmd": "open -a 'Visual Studio Code' .", "note": "用 VSCode 打开当前目录（code 不在 PATH）"},
                {"cmd": "sw_vers", "note": "macOS 版本"},
                {"cmd": "sysctl -n machdep.cpu.brand_string hw.memsize", "note": "芯片与内存"},
                {"cmd": "df -h /", "note": "根卷剩余空间"},
                {"cmd": "top -l 1 -n 10 -o cpu", "note": "CPU 占用前 10 进程（采样一次）"},
            ]},
            {"group": "⑭ 未安装软件（备查，运行会报错）", "items": [
                {"cmd": "docker --version", "note": "Docker 未安装"},
                {"cmd": "gradle -version", "note": "Gradle 未装（建议用项目 gradlew）"},
                {"cmd": "wget --version", "note": "wget 未装（用 curl 或 brew install wget）"},
            ]},
            {"group": "⑮ Tailscale 组网（CLI 已在 /usr/local/bin）", "items": [
                {"cmd": "tailscale status", "note": "查看组网节点与在线状态（App Store 版自动在 /usr/local/bin 装了包装脚本，直接可用）"},
                {"cmd": "tailscale ip -4", "note": "本机 Tailscale IPv4（本机 100.115.85.1）"},
                {"cmd": "tailscale ping <节点>", "note": "测节点连通与路径（direct/relay）"},
                {"cmd": "open -a Tailscale", "note": "启动菜单栏应用（CLI 不启动后台，仅查询）"},
                {"cmd": "tailscale version", "note": "看 CLI 版本（本机 1.104.7）"},
            ]},
            {"group": "⑯ Xcode CLT / 编译工具链（clang 21.0.0）", "items": [
                {"cmd": "xcode-select -p", "note": "查看 CLT 安装位置（/Library/Developer/CommandLineTools）"},
                {"cmd": "clang --version", "note": "编译器版本（本机 21.0.0，Apple clang）"},
                {"cmd": "pkgutil --pkg-info=com.apple.pkg.CLTools_Executables", "note": "查看 CLT 安装版本与时间"},
                {"cmd": "xcode-select --install", "note": "重装/修复 CLT（弹窗安装）"},
                {"cmd": "xcrun --find git && git --version", "note": "确认 git 来自 CLT 而非 brew"},
                {"cmd": "clang -o hello hello.c && ./hello", "note": "最小编译验证"},
            ]},
            {"group": "⑰ AI 工具目录与记忆体（WorkBuddy / Codex / Qoder / Trae）", "items": [
                {"cmd": "du -sh ~/.workbuddy ~/.codex ~/.qoder 2>/dev/null | sort -h", "note": "三家 AI 工具主目录体积（995MB / 1.1GB / 115MB）"},
                {"cmd": "du -sh \"$HOME/Library/Application Support/Trae CN\" \"$HOME/Library/Application Support/TRAE SOLO CN\"", "note": "Trae IDE 与 SOLO 数据体积（实测合计约 4.6GB）"},
                {"cmd": "ls ~/.qwen/skills | wc -l && ls ~/.qwen/skills | head -8", "note": "千问办公智能体技能清单（lark-* 飞书集成）"},
                {"cmd": "du -sh \"$HOME/Library/Application Support/QwenWorkCN\" \"$HOME/Library/Application Support/Qianwen\" ~/Library/Caches/Qianwen", "note": "千问办公/千问数据与缓存体积（千问缓存 648MB 可清理）"},
                {"cmd": "open -a QwenWorkCN && open -a Qianwen", "note": "启动千问办公 / 千问桌面端"},
                {"cmd": "cat ~/.codex/config.toml", "note": "ChatGPT/Codex CLI 配置"},
                {"cmd": "cat ~/.codex/AGENTS.md", "note": "Codex 全局指令（记忆体一部分）"},
                {"cmd": "ls ~/.codex/memories ~/.qoder/memories", "note": "Codex / Qoder 记忆体目录"},
                {"cmd": "cat ~/.workbuddy/mcp.json", "note": "WorkBuddy MCP 服务器配置"},
                {"cmd": "ls ~/.workbuddy/skills ~/.workbuddy/connectors", "note": "WorkBuddy 技能与连接器"},
                {"cmd": "open -a WorkBuddy && open -a 'Trae CN'", "note": "启动 WorkBuddy / Trae"},
            ]},
            {"group": "⑱ 解压缩（tar / gzip / zip）", "items": [
                {"cmd": "tar -czvf x.tar.gz <目录>", "note": "打包并 gzip 压缩（c=create z=gzip v=显示 f=文件）"},
                {"cmd": "tar -xzvf x.tar.gz", "note": "解压 .tar.gz（自动识别 gz/bz2/xz）"},
                {"cmd": "tar -tzvf x.tar.gz", "note": "只看包内容，不解压"},
                {"cmd": "tar -xzvf x.tar.gz -C <目标目录>", "note": "解压到指定目录（目录需已存在）"},
                {"cmd": "gzip <文件> / gunzip <文件>.gz", "note": "单文件压缩/解压（不打包，原文件消失）"},
                {"cmd": "zip -r x.zip <目录> / unzip x.zip -d <目标目录>", "note": "zip 格式；unzip 未装时用 ditto -x -k x.zip <目录>"},
                {"cmd": "ditto -c -k --sequesterRsrc --keepParent <目录> x.zip", "note": "macOS 原生打 zip（保留 Finder 元数据，与右键压缩一致）"},
                {"cmd": "tar -xzvf x.tar.gz（Win10+ cmd 自带 tar）；PowerShell Expand-Archive x.zip", "note": "Windows 侧对应命令（🟦 对照）"},
            ]},
        ],

        # ── 关键进程检测：扫描这些关键字的进程（避免重复启动 Web）──
        "watch_processes": ["web.py"],
    },
}

# ── 双平台自动选择：win32 → Windows 档案，其余（darwin/linux）→ Mac 档案 ──
PROFILE = PROFILE_WIN if _sys.platform == "win32" else PROFILE_MAC
