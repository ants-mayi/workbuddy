# Shell 与系统常用命令（文件操作 / 日志查看 / 运维）

> 一份独立的"系统命令"手册，与本目录 [06-跨平台命令速查与差异](06-跨平台命令速查与差异.md) 互补：
> 那份按**软件**组织（Java/Conda/Git…），这份按**系统操作**组织——文件、文本、日志、压缩、远程。
>
> **本机 = macOS（Apple M2，默认 shell zsh）**，所以 **Bash 列（🟡）就是日常直接用的**；**CMD / PowerShell 列（🟦）**是 Windows 台式机对照（同一项目 Windows 侧、写跨平台脚本时用）。
> **图例**：⚠️ = 有坑 / 易错 / 已弃用；🟡 = 本机（macOS）直接可用；🟦 = Windows 台式机（对照）。
> 命令基于 Windows 10/11 与主流 Linux 发行版核对（2026-11-17），具体参数以 `man command` / `command /?` / `Get-Help` 为准。

---

## 目录

- [1. 文件与目录操作](#1-文件与目录操作)
- [2. 文件内容查看与搜索](#2-文件内容查看与搜索)
- [3. 文本编辑与替换（不开编辑器）](#3-文本编辑与替换不开编辑器)
- [4. 日志查看与分析（重点）](#4-日志查看与分析重点)
- [5. 解压缩](#5-解压缩)
- [6. 远程连接、传输与断开](#6-远程连接传输与断开)
- [7. 进程 / 服务 / 系统信息](#7-进程--服务--系统信息)
- [8. 网络诊断](#8-网络诊断)
- [9. 帮助系统与实用建议](#9-帮助系统与实用建议)
- [10. 关键差异与注意事项](#10-关键差异与注意事项)

---

## 1. 文件与目录操作

| 功能 | Bash (Linux/macOS) 🟡 | Windows CMD 🟦 | PowerShell 🟦 |
| --- | --- | --- | --- |
| 当前路径 | `pwd` | `cd`（无参数） | `Get-Location` / `pwd` |
| 切换目录 | `cd /path` / `cd ~` / `cd -`（上个目录） | `cd /d D:\path`（⚠️ 跨盘要 `/d`） | `Set-Location D:\path`（跨盘不用 `/d`） |
| 列目录 | `ls -la` / `ls -lh`（人类可读大小） | `dir` / `dir /a` | `Get-ChildItem` / `ls` / `gci` |
| 列子目录树 | `find . -type d` / `tree` | `tree /f` | `tree` / `Get-ChildItem -Recurse` |
| 新建目录 | `mkdir -p a/b/c`（父目录不存在也建） | `mkdir a\b\c`（⚠️ 依赖命令扩展，默认启用支持多层；老系统/扩展禁用需先建父目录） | `New-Item -ItemType Directory -Force a\b\c` 或 `mkdir -Force a\b\c`（实测均支持多层与 -Force） |
| 新建空文件 | `touch f.txt` | `type nul > f.txt` | `New-Item f.txt` / `ni f.txt` |
| 复制文件 | `cp src dst` | `copy src dst` | `Copy-Item src dst` |
| 复制目录 | `cp -r srcdir dstdir` | `xcopy /e /i srcdir dstdir` | `Copy-Item srcdir dstdir -Recurse` |
| 大规模复制/备份 | `rsync -av --delete src/ dst/`（Linux/macOS 自带） | `robocopy src dst /e /mt:16`（多线程） | `robocopy src dst /e /mt:16`（⚠️ `/mir` 会镜像删除，慎用） |
| 移动 | `mv src dst` | `move src dst` | `Move-Item src dst` |
| 重命名 | `mv old new` | `ren old new` | `Rename-Item old new` |
| 删除文件 | `rm f` / `rm -f`（不确认） | `del f` | `Remove-Item f` |
| 删除目录 | `rm -r dir` / `rm -rf` | `rmdir /s /q dir` | `Remove-Item dir -Recurse -Force` |
| 查看大小 | `du -sh dir` / `du -h --max-depth=1` | 无原生（见下） | `"{0:N2} GB" -f ((Get-ChildItem dir -Recurse \| Measure-Object Length -Sum).Sum/1GB)` |
| 磁盘空间 | `df -h` | `wmic logicaldisk get name,freespace`（⚠️ wmic 已弃用） | `Get-PSDrive -PSProvider FileSystem` / `Get-Volume` |
| 找文件 | `find . -name "*.conf"` / `locate`（需索引） | `dir /s /b *.conf` | `Get-ChildItem -Recurse -Filter *.conf` |
| 软链接 | `ln -s target link` | `mklink link target`（CMD）/ `mklink /d`（目录） | `New-Item -ItemType SymbolicLink`（需管理员或开发者模式） |
| 比较文件 | `diff a b` | `fc a b` | `Compare-Object (Get-Content a) (Get-Content b)` |
| 统计行数 | `wc -l f` | `find /c /v ""` | `(Get-Content f).Count` |

> ⚠️ **删除高危命令**：`rm -rf` / `Remove-Item -Recurse -Force` 不可恢复，删除前先 `ls` 确认路径；本控制台的缓存清理功能都做了只读预览，同理。
> 🟦 **Windows 台式机**：Git Bash（`D:\wofkIns\Git\bin\bash.exe`）自带 `ls/cp/mv/rm/grep/tar/ssh` 等全套 Unix 工具，在 Windows 上想用 Bash 语法不用装 WSL。
> 🟡 **本机（macOS）**：zsh + BSD 工具链。注意 BSD 版命令与 GNU 有差异（如 `sed -i ''` 要空参数、`date` 不支持 `-d`、`ls` 无 `--color=auto` 写法用 `ls -G`）。

---

## 2. 文件内容查看与搜索

| 功能 | Bash 🟡 | Windows CMD 🟦 | PowerShell 🟦 |
| --- | --- | --- | --- |
| 看全文 | `cat f` | `type f` | `Get-Content f` / `gc f` |
| 看前/后 N 行 | `head -20 f` / `tail -20 f` | `more`（翻页，无 head/tail） | `Get-Content f -TotalCount 20` / `Get-Content f -Tail 20` |
| 分页看 | `less f`（推荐）/ `more f` | `more f` | `Get-Content f \| Out-Host -Paging` |
| 搜内容 | `grep "kw" f` | `findstr "kw" f` | `Select-String -Path f -Pattern "kw"` |
| 递归搜目录 | `grep -rn "kw" dir` | `findstr /s /n /i "kw" *.*` | `Get-ChildItem -Recurse \| Select-String "kw"` |
| 忽略大小写 | `grep -i` | `findstr /i` | `Select-String -CaseSensitive:$false`（默认就不区分） |
| 反向匹配 | `grep -v "kw"` | `findstr /v "kw"` | `... \| Where-Object {$_ -notmatch 'kw'}` |
| 正则搜索 | `grep -E "a|b"` | `findstr /r "a b"`（空格=OR，语法特殊） | `Select-String -Pattern 'a\|b'`（.NET 正则） |
| 显示行号 | `grep -n` / `cat -n` | `findstr /n` | `Select-String`（自带行号 `LineNum`） |
| 多关键词 AND | `grep a \| grep b` | `findstr /c:"a" /c:"b"`（是 OR） | `Select-String a \| Select-String b` |

> ⚠️ **CMD `findstr` 的正则是简化版**，且 `/c:"multi word"` 才表示整体匹配；复杂正则请用 PowerShell `Select-String`（.NET 语法）。

---

## 3. 文本编辑与替换（不开编辑器）

### Bash：sed 流式替换

```bash
# 全局替换（⚠️ sed -i 直接改原文件、不可逆）
sed -i 's/old/new/g' file.txt

# 生产环境安全姿势：自动备份 + diff 验证
sed -i.bak 's/MaxConnections=100/MaxConnections=500/' app.ini
diff app.ini.bak app.ini

# 只看第 5 行；删除注释行和空行
sed -n '5p' file.txt
sed -e '/^#/d' -e '/^$/d' file.txt
```

### PowerShell：-replace + 显式编码

```powershell
# ✅ 安全替换模式（显式指定编码 + 仅在内容变化时写入）
$content = Get-Content -LiteralPath .\app.ini -Raw -Encoding UTF8
$newContent = $content -replace 'MaxConnections=\d+', 'MaxConnections=500'
if ($newContent -ne $content) {
    Set-Content -LiteralPath .\app.ini -Value $newContent -Encoding UTF8 -NoNewline
}

# ⚠️ Windows PowerShell 5.x 默认编码陷阱
# Get-Content 省略 -Encoding 时用系统 ANSI 代码页，不是 UTF-8
# Set-Content 默认也是 ANSI → 必须始终显式指定 -Encoding UTF8
# PowerShell 7+（pwsh）默认 UTF-8，无此问题
```

### CMD

> ⚠️ CMD **没有原生流式替换能力**，复杂文本处理请用 PowerShell 或 Git Bash 里的 `sed`。

### Vim 最小集（交互式编辑）

打开 `vim file` 后：`i` 进入插入模式 → 编辑 → `Esc` 退出插入 → `:wq` 保存退出（`:q!` 不保存强制退出）；`/kw` 搜索、`n` 下一个、`dd` 删行、`u` 撤销。

---

## 4. 日志查看与分析（重点）

### 4.1 实时跟踪新日志

| Bash | PowerShell | 说明 |
| --- | --- | --- |
| `tail -f app.log` | `Get-Content app.log -Wait` | 新内容出现即刷新 |
| `tail -F app.log` | — | ⚠️ 日志轮转（文件被重建）后继续跟踪，`-f` 做不到 |
| `tail -f a.log b.log` | 多文件各自开窗口 | 多文件同时跟踪 |
| `tail -n 100 -f app.log` | `Get-Content app.log -Tail 100 -Wait` | 先看最后 100 行再跟踪 |

> ⚠️ Windows 台式机的 CMD/PowerShell 原生没有 `tail`，Git Bash / WSL 里才有；本机（macOS）自带 `tail -f`。

### 4.2 分页浏览大文件

`less` 是最常用的日志浏览器——**按需加载，打开 GB 级日志几乎瞬间完成**，远优于 `cat` 一次性灌进终端：

| 按键 | 作用 |
| --- | --- |
| `空格` / `b` | 下翻一页 / 上翻一页 |
| `g` / `G` | 跳到文件头 / 尾 |
| `/kw` 然后 `n` | 向下搜索，下一个匹配 |
| `?kw` 然后 `n` | 向上搜索 |
| `-i` 回车 | 开启忽略大小写搜索 |
| `F` | 实时跟踪模式（等价 `tail -f`，Ctrl+C 退出跟踪回到浏览） |
| `q` | 退出 |

### 4.3 grep 过滤进阶

```bash
# 排除噪音：错误日志但去掉健康检查
grep "ERROR" app.log | grep -v "/health"

# 统计匹配行数；取匹配部分（-o 只输出命中片段）
grep -c "ERROR" app.log
grep -o "req_id=[0-9a-f]*" app.log

# 上下文：命中行前后各 3 行（排查日志时极常用）
grep -B3 -A3 "NullPointerException" app.log

# 多模式任一命中
grep -E "ERROR|FATAL|Exception" app.log
```

PowerShell 等价：`Select-String -Path app.log -Pattern "ERROR" -Context 3,3`（前 3 后 3）。

### 4.4 awk 列提取与统计

`awk` 擅长**按列提取和统计**，是日志量化分析的核心工具（默认按空白分列，`$1` 是第 1 列）：

```bash
# 提取 Nginx 访问日志中状态码为 500 的请求 IP（$9=状态码，$1=IP）
awk '$9 == 500 {print $1}' /var/log/nginx/access.log

# 统计各状态码出现次数并按次数倒序取前 10
awk '{print $9}' access.log | sort | uniq -c | sort -rn | head -10

# 按时间范围过滤（两个正则之间为一个范围）
awk '/2026-11-17 10:/,/2026-11-17 11:/' app.log

# 提取配置文件中特定键的值
awk '$1 == "MaxConnections" {print $2}' /etc/myapp/config.conf
```

PowerShell 等价（管道传的是**对象**，思想相同）：

```powershell
# 统计错误级别出现次数
Get-Content app.log | ForEach-Object { ($_ -split '\s+')[2] } |
  Group-Object | Sort-Object Count -Descending | Select-Object -First 10
```

### 4.5 journalctl（Linux systemd 服务日志）

```bash
journalctl -u nginx                 # 某个服务的全部日志
journalctl -u nginx -f              # 实时跟踪
journalctl -u nginx --since today   # 今天的
journalctl -u nginx --since "2026-11-17 10:00" --until "2026-11-17 11:00"
journalctl -p err -e                # 只看错误级及以上的，并跳到最新
journalctl --disk-usage             # 日志占用空间；清理：journalctl --vacuum-size=200M
```

> 老系统/无 systemd：直接看 `/var/log/syslog`（Debian 系）或 `/var/log/messages`（RHEL 系）。

### 4.6 Windows 事件日志 / IIS

```powershell
# 最近 20 条应用程序日志（文本格式）
wevtutil qe Application /c:20 /f:text /rd:true

# 只看错误级
Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2} -MaxEvents 20 |
  Format-Table TimeCreated, Message -Wrap

# 扫描 IIS 日志中 401 请求的来源 IP 并去重统计
Select-String -Path C:\inetpub\logs\*\*.log -Pattern " 401 " |
  ForEach-Object { ($_ -split '\s+')[-3] } |
  Group-Object | Sort-Object Count -Descending | Select-Object -First 10
```

🟡 **本机（macOS）日志位置**：统一日志用 `log show --last 1h --predicate 'process == "xxx"'`；应用日志多在 `~/Library/Logs/<应用>/`；Ollama 在 `~/.ollama/logs/server.log`。控制台无固定日志文件（输出在启动它的终端，可 `./env-web.sh > web.log 2>&1` 落盘）。
🟦 **Windows 台式机**：MySQL 8.0 错误日志在其 data 目录；Sunshine 配置/日志在 `C:\Program Files\Sunshine\config`；Tailscale 状态 `tailscale status`。

### 4.7 组合使用范例

```bash
# Linux：找出最近错误最多的 Top 5 接口，排除健康检查
grep "ERROR" app.log | grep -v "/health" | \
  awk '{print $7}' | sort | uniq -c | sort -rn | head -5

# Linux：批量检查所有 conf 文件中是否包含过时参数
find /etc/myapp -name "*.conf" -exec grep -l "DeprecatedOption" {} +
```

---

## 5. 解压缩

| 功能 | Bash 🟡 | Windows CMD 🟦 | PowerShell 🟦 |
| --- | --- | --- | --- |
| 解压 tar.gz | `tar -xzf f.tar.gz` / `-C 目标目录` | `tar -xzf f.tar.gz` | `tar -xzf f.tar.gz` |
| 解压 zip | `unzip f.zip -d dir` | `tar -xf f.zip` | `Expand-Archive f.zip -DestinationPath dir` |
| 压缩 tar.gz | `tar -czf f.tar.gz dir` | `tar -czf f.tar.gz dir` | 同 CMD |
| 压缩 zip | `zip -r f.zip dir`（需装 zip） | `tar -a -cf f.zip dir` | `Compress-Archive dir f.zip` |
| 查看（不解压） | `tar -tvf f.tar.gz` / `unzip -l f.zip` | 同左 | `tar -tvf f.tar.gz` |

> **版本/实现差异**：
> - Windows 10 1803+ 自带 `tar`，基于 **libarchive (bsdtar)**，支持 `-a` 按扩展名自动选格式，与 Linux GNU tar 行为略有差异。
> - `tar -C /path/to/dir` 解压到指定目录时**目录必须已存在**。
> - ⚠️ `Compress-Archive` / `Expand-Archive` 的 **2GB 单文件限制**仅针对 Windows PowerShell 5.1；PowerShell 7+（.NET 5+）已放宽（支持 Zip64）。无论哪个版本，超大包仍建议直接用 `tar`。

---

## 6. 远程连接、传输与断开

```bash
# 连接（Windows 10/11 也内置 OpenSSH 客户端，三平台命令一致）
ssh user@host            # 默认 22 端口
ssh user@host -p 2222    # 指定端口
ssh -i ~/.ssh/id_ed25519 user@host    # 指定密钥

# 传文件（两边都要有 ssh/scp）
scp local.tar.gz user@host:/tmp/          # 本地 → 远程
scp user@host:/var/log/app.log ./         # 远程 → 本地
scp -r dir user@host:/tmp/                # 递归传目录
```

**断开连接**：正常输 `exit` 或按 `Ctrl+D`。

> ⚠️ **SSH 卡死时不要反复按 `Ctrl+C`**，通常无效。正确做法是 SSH 内置转义序列 **`~.`**（波浪号+点，新起一行输入），由本地客户端拦截，不依赖远端响应。

### tmux：远程长任务断线不丢（mac/Linux/WSL/Git Bash）

> 本职是"会话与终端解耦"：SSH 断线、关窗都不会杀掉里面跑的任务，重连即恢复现场。配合上面 `ssh` 的标准姿势：登服务器先 `tmux new -s work` 再跑长任务，断线后重连 `tmux attach -t work`。

| 操作 | 命令 / 按键 |
| --- | --- |
| 新建会话 | `tmux new -s work` |
| 列出会话 | `tmux ls` |
| 恢复会话 | `tmux attach -t work` |
| 分离（任务继续跑） | `Ctrl+b` 再按 `d` |
| 删除会话 | `tmux kill-session -t work` |
| 新建窗口 / 切窗口 | `Ctrl+b c` / `Ctrl+b 0~9` |
| 左右 / 上下分屏 | `Ctrl+b %` / `Ctrl+b "` |
| 缩放当前窗格 | `Ctrl+b z` |

> Windows 上 Git Bash / WSL 均可装 tmux；原生 PowerShell/CMD 无对应物——Windows Terminal 的分屏只解决显示问题，不解决断线保活。

---

## 7. 进程 / 服务 / 系统信息

服务的启动/停止/状态/刷新已按软件整理在 [06 §2 服务管理](06-跨平台命令速查与差异.md#2-服务管理启动停止状态刷新)，这里只列进程与系统信息：

| 功能 | Bash 🟡 | Windows CMD 🟦 | PowerShell 🟦 |
| --- | --- | --- | --- |
| 列进程 | `ps aux` | `tasklist` | `Get-Process` |
| 按名找进程 | `ps aux \| grep python` | `tasklist \| findstr python` | `Get-Process python` |
| 进程命令行 | `ps -ef \| grep python` | `wmic process where "name='python.exe'" get ProcessId,CommandLine`（⚠️ wmic 弃用） | `Get-CimInstance Win32_Process -Filter "name='python.exe'"` |
| 杀进程 | `kill <pid>` / `kill -9` | `taskkill /PID <pid> /F` | `Stop-Process -Id <pid> -Force` |
| CPU/内存排行 | `top` / `htop` | `tasklist /v`（弱） | `Get-Process \| Sort-Object CPU -Descending \| Select -First 10` |
| 系统信息 | `uname -a` / `lsb_release -a` | `systeminfo` | `Get-ComputerInfo`（慢）/ `systeminfo` |
| 环境变量 | `env` / `echo $VAR` | `set` / `echo %VAR%` | `Get-ChildItem Env:` / `$env:VAR` |

> ⚠️ **PowerShell 里的 `curl` 不是真 curl**：Win10/11 自带 `curl.exe`（真正的 curl），但 PowerShell 中 `curl` 默认是 `Invoke-WebRequest` 的别名，行为完全不同。在 PS 中用原生 curl 请显式写 **`curl.exe`**（CMD 里写 `curl` 即可）。

### 系统维护与磁盘（本机 macOS 🟡）

| 功能 | 命令 | 说明 |
| --- | --- | --- |
| 磁盘检查修复 | `diskutil verifyVolume /`（修复加 `repairVolume`） | APFS 卷检查；重大问题进恢复模式用急救 |
| DNS 缓存清理 | `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder` | 改 hosts / DNS 排障后必做 |
| 磁盘空间 | `df -h /`；图形化：关于本机 > 储存空间 | 清理建议看系统储存管理 |
| 定期维护脚本 | `sudo periodic daily weekly monthly` | 系统日常维护任务手动触发 |
| 系统日志 | `log show --last 1h`（量大，加 `--predicate` 过滤） | 统一日志系统（替代旧 syslog） |
| 权限修复 | 不再需要（10.11+ 无需 repair permissions） | 旧教程的 repair Disk Permissions 已废弃 |

### 系统维护与磁盘（Windows 🟦，⚠️ 需管理员）

| 功能 | 命令 | 说明 |
| --- | --- | --- |
| 系统文件检查修复 | `sfc /scannow`（只检不修：`/verifyonly`） | 修复系统文件损坏 |
| 系统映像修复三步 | `DISM /Online /Cleanup-Image /CheckHealth` → `/ScanHealth` → `/RestoreHealth` | sfc 修不好时，先跑 DISM 再跑 sfc |
| 清理 WinSxS 旧组件 | `DISM /Online /Cleanup-Image /StartComponentCleanup` | C 盘减肥，不删正在用的组件 |
| 磁盘清理 | `cleanmgr` / 设置 > 系统 > 存储 > 存储感知 | 日常清理用存储感知即可 |
| 检查修复磁盘 | `chkdsk D: /f` | 系统盘（C:）会提示重启时安排检查 |
| 清 DNS 缓存 | `ipconfig /flushdns` | 改 hosts / DNS 排障后必做 |

---

## 8. 网络诊断

| 功能 | Bash 🟡 | Windows CMD 🟦 | PowerShell 🟦 |
| --- | --- | --- | --- |
| 连通测试 | `ping -c 4 host`（⚠️ Linux 要 `-c` 限次数，否则一直 ping） | `ping host`（默认 4 次） | `Test-Connection host` / `ping` |
| 端口连通 | `nc -zv host 3306` | 无原生（用 PS） | `Test-NetConnection host -Port 3306` |
| 本机 IP | `ip addr` / `ifconfig`(旧) | `ipconfig` / `ipconfig /all` | `Get-NetIPConfiguration` |
| DNS 查询 | `dig domain` / `nslookup` | `nslookup domain` | `Resolve-DnsName domain` |
| 路由追踪 | `traceroute host` | `tracert host` | `Test-NetConnection -TraceRoute` |
| 监听端口 | `ss -tlnp`（推荐）/ `lsof -i -P -n` | `netstat -ano \| findstr LISTENING` | `Get-NetTCPConnection -State Listen` |
| 下载 | `wget url` / `curl -O url` | `curl -O url`（Win10 1803+ 自带） | `curl.exe -O url` / `Invoke-WebRequest` |

> 端口/进程排查的完整对比与两机端口速查见 [06 §11](06-跨平台命令速查与差异.md#11-端口--进程--网络排查) 和 Web「实时端口」面板。本机（macOS）日常用 `lsof -nP -iTCP:端口 -sTCP:LISTEN`。

---

## 9. 帮助系统与实用建议

**帮助系统**：

- Bash：`man command` / `command --help`
- CMD：`command /?`
- PowerShell：`Get-Help command -Detailed` / `Get-Command -Name *tar*`

**实用建议**：

- **Windows 用户优先学 PowerShell**：CMD 已进入维护模式，微软新功能仅面向 PS。WSL 用户则直接使用 Bash/Zsh。
- **跨平台脚本**：如需同时兼容，考虑 Python、Node.js 或 PowerShell Core（`pwsh`，跨平台，默认 UTF-8）。
- **远程操作审计**：生产环境建议用 `script` 命令（Linux）或 `Start-Transcript`（PowerShell）记录整个会话操作日志，便于事后追溯。
- **PowerShell 编码陷阱**：Windows PowerShell 5.x 默认输出编码为 UTF-16，处理 Linux 生成的 UTF-8 文件时易出问题。建议在 `$PROFILE` 中添加 `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`，或直接用 PowerShell 7+。
- **跨平台一致性**：频繁在 Linux/Windows 间切换的话，优先掌握 `ssh`、`scp`、`tar` 这三个**两端都原生可用**的命令，记忆负担最小。

---

## 10. 关键差异与注意事项

1. **路径分隔符**：Linux 用 `/`；Windows CMD 用 `\`；PowerShell 两者兼容但推荐 `\`。写跨平台脚本时用语言自带的路径拼接（如 Python `pathlib`）。
2. **通配符**：Bash 由 shell 展开通配符（globbing）；CMD 由命令自身解析；PowerShell 由提供程序（Provider）处理——行为细节不同。
3. **管道对象 vs 文本**：Bash/CMD 管道传纯文本流；PowerShell 管道传 **.NET 对象**，可直接访问属性（如 `Get-Process | Where-Object {$_.CPU -gt 100}`），这是 PS 的核心优势。
4. **大小写敏感**：Linux 文件名和参数严格区分大小写；Windows 文件系统不区分，PowerShell 命令本身也不区分。
5. **转义字符**：Bash 用 `\`；CMD 用 `^`；PowerShell 用反引号 `` ` ``。
6. **管理员权限**：Linux 用 `sudo` 提权；Windows 需"以管理员身份运行"终端，或 PS 里 `Start-Process -Verb RunAs`。

---

> **维护提示**：本文件与 [06-跨平台命令速查与差异](06-跨平台命令速查与差异.md)、`config.py` 的 `command_lib`、`G:\AI\WorkBuddy\docs\电脑开发环境信息.md` 是四处维护，升级系统/软件后记得同步。
