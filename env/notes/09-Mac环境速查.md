# 09-Mac环境速查（Apple M2 MacBook）

> 数据来源：`mac/mac_profile.json`（2026-11-17 由 `mac/collect_mac.py` 采集）。
> 软件升级/路径变更后：先重跑 `python3 mac/collect_mac.py`，再更新 `config.py` 的 `PROFILE_MAC`。

## 1. 本机身份

| 项 | 值 |
| --- | --- |
| 机型 | MacBook (Mac14,2) |
| 芯片 | Apple M2（arm64），8 核 |
| 统一内存 | 24 GB |
| 系统 | macOS 26.6.2 (25G83) |
| 磁盘 | 单卷 APFS 460GB，可用 ~165GB，充足 |
| GPU 加速 | 无 CUDA；PyTorch 走 **MPS** 后端（`torch.backends.mps.is_available()` = True） |

## 2. Python 环境（4 套并存）

| 解释器 | 版本 | 说明 |
| --- | --- | --- |
| `~/.workbuddy/binaries/python/.../python3` | 3.13.12 | PATH 首个（WorkBuddy 内置），无 AI 库 |
| `~/miniconda3/bin/python3` | 3.13.13 | conda base，有 requests |
| `/opt/homebrew/bin/python3` | 3.14.6 | Homebrew，无三方库 |
| `/usr/bin/python3` | 3.9.6 | 系统自带 |

**AI 环境只有一套**：`~/miniconda3/envs/pytorch`（torch 2.11.0 / transformers 5.8.0 / flask 3.1.3 / psutil 7.2.2），不在 PATH。
conda 环境：`base` / `llm` / `pytorch`，另有一个项目级环境 `transformers-finetune-lab/.conda`（torch 2.12）。

铁律：**装包一律 `python -m pip`**；AI 任务先 `conda activate pytorch` 或写全路径。

## 3. 开发工具（Homebrew 前缀 /opt/homebrew）

| 工具 | 版本 | 位置 |
| --- | --- | --- |
| JDK | 17.0.17 | `/opt/homebrew/opt/openjdk@17`（JAVA_HOME 已设） |
| Maven | 3.9.12 | `/opt/homebrew/bin/mvn` |
| Git | 2.51.2 | `/opt/homebrew/bin/git`（另有系统 /usr/bin/git） |
| Node.js / npm | 22.22.2 / 10.9.7 | WorkBuddy 内置（PATH 首个）；brew 也装了一套 |
| Go | 1.26.4 | `/opt/homebrew/bin/go` |
| ffmpeg | 8.1.2 | `/opt/homebrew/bin/ffmpeg` |
| Ollama | 0.40.16 | `/usr/local/bin/ollama`，常驻运行 |
| Deno | 2.8.3 | `/opt/homebrew/bin/deno` |
| Xcode CLT | 26.6 | `/Library/Developer/CommandLineTools` |
| Tailscale | 1.104.7 | app + `/usr/local/bin/tailscale`，**已装未运行** |
| Homebrew | 5.0.8 | 72 个 formula、2 个 cask（mark-text、mos） |

未安装：Docker、Gradle（建议用项目 gradlew）、wget（用 curl 代替）。

桌面 GUI 应用（启动即用，无常用 CLI）：IntelliJ IDEA 2026.1.2、Postman 11.81.4、KuliCloud 3.2.2（代理，端口 7892）、UU远程 GameViewer 4.46.0、VSCode、千问办公 QwenWorkCN 1.3.2（技能库 `~/.qwen/skills`）、千问 Qianwen 5.2.0.298——均在 /Applications，软件状态面板可见。

## 4. 服务与端口（2026-11-17 实测）

常驻服务 7 项（Web「服务与端口」面板可实时探测/一键启停）：Ollama（Running）、UU远程（Running）、KuliCloud 代理（Running）、WorkBuddy 桌面端（Running）、Tailscale（默认 Stopped）、控制台 Web 8010（按需）、Homebrew 托管服务（无）。

| 端口 | 用途 | 说明 |
| --- | --- | --- |
| 11434 | Ollama 本地大模型 | 常驻；`ollama list` 看模型 |
| 11435 | 本地 Python API | 临时进程，已停止 |
| 5000 / 7000 | macOS ControlCenter | **AirPlay 系统占用，避开** |
| 7892 | KuliCloud 代理工具 | HTTP(S)_PROXY 指向它，端口会变 |
| 56352 / 56353 | UU远程 GameViewer | ⚠️ 只绑具体网卡/IPv6，`connect 127.0.0.1` 探测会误报不通，用 `lsof -iTCP:56352 -sTCP:LISTEN` 判断 |
| 54365 / 54367 / 16799 | 千问办公 QwenWorkCN | 运行时随机分配，随启随灭，不列入快照 |
| 8010 | 本控制台 Web | 按需；被占自动顺延 |

无 brew services 托管服务；用户 LaunchAgents 自启动项 7 个（jetbrains、google keystone 等）。高随机临时端口（18488/39099/5 万段等）为编辑器/沙箱会话，随启随灭，不列入快照。

## 5. 代理

`HTTP_PROXY` / `HTTPS_PROXY` 指向本机代理工具（实测 127.0.0.1:51510，端口随代理客户端变化）。
pip / git / curl 走代理异常时先查代理是否在跑；`NO_PROXY=127.0.0.1,localhost,::1`。

## 6. 与 Windows 侧（PROFILE_WIN）的差异速记

| 项 | Windows 11 台式机 | 本机 Mac |
| --- | --- | --- |
| AI 解释器 | `G:\workIns\conda\envs\pytorch\python.exe` | `~/miniconda3/envs/pytorch/bin/python` |
| GPU | RTX 3070 + CUDA 12.6 | Apple M2 + MPS |
| 服务管理 | `net start/stop`（管理员） | `open -a` / `launchctl` / `brew services` |
| 端口排查 | `netstat -ano` | `lsof -nP -iTCP -sTCP:LISTEN` |
| 打开文件夹 | `explorer <路径>` | `open <路径>` |
| 启动脚本 | `env.bat` / `env-web.bat` | `./env.sh` / `./env-web.sh` |
| HF 缓存 | `G:\study\AI\cache\huggingface`（HF_HOME 已设） | 默认 `~/.cache/huggingface`（HF_HOME 未设） |
| pip 缓存 | `C:\Users\marco\AppData\Local\pip\Cache` | `~/Library/Caches/pip`（清理 `pip cache purge`） |
| npm 缓存 | `C:\Users\marco\AppData\Local\npm-cache` | `~/.npm`（清理 `npm cache clean --force`） |
| Go 模块缓存 | （Windows 未装 Go） | `~/go/pkg/mod`（清理 `go clean -modcache`） |
| Ollama 模型 | （Windows 未装） | `~/.ollama` |
| AI 桌面应用 | WorkBuddy / ChatGPT（Windows 侧按实际补充） | WorkBuddy / ChatGPT / Qoder / Trae / 千问办公 / 千问 共 6 款（详见 11） |
| 版本探测 | config 绝对路径 + `cmd /c` 调 .cmd | config 绝对路径直调可执行文件 |

两套档案都在 `config.py`（`PROFILE_WIN` / `PROFILE_MAC`），按 `sys.platform` 自动选择；
引擎（engine/）完全共用，跨平台逻辑已内置。

## 7. 常用命令速记

```bash
./env.sh status        # 状态总览（版本/GPU/端口）
./env.sh doctor        # 一键体检
./env.sh services      # 服务/端口快照
./env.sh cache         # 缓存占用（只读）
./env-web.sh           # 启动 Web 控制台（自动开浏览器；「环境体检」面板 = 18 项自动检查）

python3 mac/collect_mac.py   # 重新采集环境事实
lsof -nP -iTCP:8010          # 查端口占用
conda activate pytorch       # 进 AI 环境
ollama list && ollama ps     # 本地大模型
```

软件变更后的三件套（全绿即自洽，详见 00「维护约定」）：

```bash
python3 _check_links.py       # 文档链接
python3 _check_software.py    # 软件覆盖（可带 mac/win/all）
python3 _check_web_sync.py    # 18 项体检：Web 显示与实机一致性
```

## 8. 开发者注意（本机特有的坑与事实）

- **`/usr/libexec/java_home` 陷阱**：系统 JVM 注册表里只有 **Temurin 8（x86_64）**，
  `/usr/libexec/java_home` 默认会返回 Java 8；日常用的 JDK 17 来自 Homebrew
  （`JAVA_HOME=/opt/homebrew/opt/openjdk@17/...`，已正确设置）。
  构建工具若用 `/usr/libexec/java_home` 找 JDK，会意外拿到 8——显式用 `JAVA_HOME`。
- **Tailscale 已装但默认不随开机启动**（Windows 侧是常驻 Running）：需要组网先
  `open -a Tailscale`；CLI 在 `/usr/local/bin/tailscale`（Intel 位置，经 Rosetta）。
- **`code` 命令不在 PATH**：想启用可把
  `/Applications/Visual Studio Code.app/Contents/Resources/app/bin` 加进 PATH，
  或在 VSCode 里执行 `Shell Command: Install 'code' command in PATH`；
  当前用 `open -a 'Visual Studio Code' .` 即可（本机装了 48 个扩展）。
- **git 身份与 SSH**：`user.name=marco_masc` / `user.email=marco_masc@outlook.com`；
  `~/.ssh/` 下有 `id_ed25519` 与 `id_rsa` 两对密钥。
- **计算机名**：`masc的MacBook Air`（局域网/AirDrop/远程连接显示用这个名字）。
- **系统更新**：macOS 26.6.2（2026-09 安装）；Xcode CLT 26.6（2026-07 安装）。
  升级系统后记得复核 `PROFILE_MAC` 的路径事实。
- **macOS 禁止读取第三方进程线程表**（系统级保护，终端里也被拒）：
  `psutil.Process.threads()` 对其它进程一律 `AccessDenied`——实时端口面板的线程数
  靠 `/bin/ps -M -p <pid>` 回退才拿到，**TID 列表只有进程读自己时可用**；
  沙箱（WorkBuddy 内）连 `ps/top` 都被禁，只能看端口/PID/进程名。
- **千问办公 ≠ 千问**：本机装了两个独立应用——QwenWorkCN（AI 办公套件，技能库
  `~/.qwen/skills` 是它的）与 Qianwen（通义千问桌面端，数据 2.5GB）。别把
  `~/.qwen` 当成千问桌面端的数据目录。
