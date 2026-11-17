# Mac 侧执行指引（环境采集 → 本机控制台）

> 目标：在 Mac 上采集环境事实（`mac_profile.json`），并让「本机开发环境控制台」
> 在 Mac 上原生运行。脚本只读、不安装任何东西、不修改系统设置。
>
> **当前状态（2026-11-17）：两阶段均已完成** ——
> - 第一阶段：`collect_mac.py` 已在本机跑过，产出 `mac_profile.json` / `mac_profile.txt`；
> - 第二阶段：采集结果已固化进 `config.py` 的 `PROFILE_MAC`，引擎已跨平台化，
>   本机可直接运行控制台（见「〇、本机日常使用」）。

## 〇、本机日常使用（Mac 已就绪）

```bash
cd ~/study/AI/WorkBuddy/env
./env.sh status        # 状态总览：版本 / GPU(MPS) / 端口
./env.sh doctor        # 一键体检
./env.sh recap         # 核心速记
./env-web.sh           # 启动 Web 控制台（自动开浏览器，Ctrl+C 退出）
# 或在 Finder 双击：启动Web控制台.command
```

Windows 与 Mac 用同一套引擎和 config：`config.py` 内 `PROFILE_WIN` / `PROFILE_MAC`
两套档案按 `sys.platform` 自动选择；题库 `question_bank.py` 同理。

## 一、需要拷到 Mac 的文件

只需要 **1 个文件**：

```
M:\AI\WorkBuddy\env\mac\collect_mac.py
```

放到 Mac 上任意目录即可，例如 `~/env-mac/`：
（终端执行：`mkdir -p ~/env-mac && cp <来源路径>/collect_mac.py ~/env-mac/`）

## 二、在 Mac 上执行

### 方式 A：让 Mac 的 WorkBuddy 执行（推荐）

把下面这段话直接发给 Mac 上的 WorkBuddy：

```
请帮我执行环境采集脚本：当前目录下有一个 collect_mac.py（如果没有，
告诉我它应该在哪里）。请用 python3 运行它：python3 collect_mac.py
运行完成后：
1. 告诉我产出的 mac_profile.json 和 mac_profile.txt 的完整路径；
2. 把 mac_profile.txt 的内容完整展示给我看。
如果 python3 不存在或报错，请给出你检测到的可用 Python 解释器路径和错误详情。
```

### 方式 B：自己在终端执行

```bash
cd ~/env-mac        # 你放脚本的目录
python3 collect_mac.py
```

耗时约 10~30 秒，结束后同目录生成两个文件：
- `mac_profile.json` — **完整原始数据，这个要带回 Windows**
- `mac_profile.txt` — 人类可读摘要，可直接浏览核对

## 三、采集结果的去向

1. **本机即目标机**（当前形态）：`PROFILE_MAC` 已写在 `env/config.py` 里，
   控制台直接读本机数据，无需搬运；
2. 若将来换新 Mac：把整个 `env/` 拷过去 → 跑 `python3 mac/collect_mac.py`
   → 按新 `mac_profile.json` 更新 `config.py` 的 `PROFILE_MAC`（主要是
   `python_exe`、各工具绝对路径、`facts.*` 快照）→ 完成。

## 四、采集内容说明（都会采什么）

| 采集项 | 方式 | 用途 |
| --- | --- | --- |
| macOS 版本/架构/芯片/内存 | sw_vers / sysctl | PROFILE_MAC.system |
| 30+ 开发工具的存在性、路径、版本 | which -a + 各自 --version | PROFILE_MAC.software |
| 全部 Python 解释器 + flask/psutil 是否可用 | 逐个 import 测试 | 选定控制台解释器 |
| conda 环境列表 | conda env list | PROFILE_MAC.python |
| Homebrew 装了什么、哪些服务在跑 | brew list / brew services | 软件状态面板 |
| launchctl 用户域服务 + 自启动项 | launchctl list（免 sudo） | 服务面板 |
| 监听端口 | psutil（有则用）/ lsof 兜底 | 端口面板 |
| 磁盘 | df -h | 磁盘面板 |
| 关键配置文件存在性（git/zshrc/npmrc 等） | os.path.exists | 配置文件面板 |
| 环境变量（JAVA_HOME/HF_HOME 等 20 项） | os.environ | 环境变量面板 |

## 五、常见问题

- **"operation not permitted"**：macOS 的 TCC 保护，脚本不需要任何特殊权限，
  如果终端 App 首次运行弹权限询问，点"允许"即可；不需要 sudo。
- **`brew services list` 卡住**：Homebrew 首次运行可能要更新索引，等它跑完即可
  （脚本对每条命令都设了超时，最坏情况只是该项数据缺失）。
- **psutil 未安装**：没关系，端口信息自动降级用 lsof 采集，结果一样可用。
