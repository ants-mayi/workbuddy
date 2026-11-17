# Windows 与 macOS 快捷键速查

> 按"想干什么"查的键位手册，涵盖办公、浏览器、终端、IDE 调试、影音与冲突排查。
> **本机 = macOS（Apple M2）**，日常看「macOS」列；「Windows」列是台式机对照（同一项目 Windows 侧使用时查）。
> 修饰键对照：Windows 主用 `Ctrl`；macOS `⌘`Command、`⌥`Option、`⌃`Control、`⇧`Shift。
> **图例**：⚠️ = 有坑 / 易错 / 版本差异；ⓘ = 补充说明。
> 系统命令与终端操作另见 [06-跨平台命令速查与差异](06-跨平台命令速查与差异.md) 与 [07-Shell与Windows常用命令](07-Shell与Windows常用命令.md)。
> ⚠️ Mac 默认 F 键优先执行音量/亮度等系统功能，调试用的 F5/F10/F11/F12 会失效——先做 [9.2 标准功能键设置](#92-f1-f12-功能键冲突mac-重灾区)。
> 键位随系统/IDE 版本与插件而异，以命令面板反查为准（见 §11）。核对日期 2026-11-17。

---

## 目录

- [1. 通用基础操作](#1-通用基础操作)
- [2. 系统与窗口管理](#2-系统与窗口管理)
- [3. 浏览器高频操作](#3-浏览器高频操作)
- [4. Office 文档（Word/Excel）](#4-office-文档wordexcel)
- [5. IDE / 代码编辑器通用](#5-ide--代码编辑器通用vs-code--jetbrains--vs)
- [6. 命令行 / 终端](#6-命令行--终端)
- [7. 调试专用（VS / VS Code / JetBrains / Xcode）](#7-调试专用)
- [8. 影音操作](#8-影音操作)
- [9. 快捷键冲突排查与解决](#9-快捷键冲突排查与解决)
- [10. 效率增强](#10-效率增强)
- [11. 官方速查表入口](#11-官方速查表入口)
- [12. 关键差异提示](#12-关键差异提示)

---

## 1. 通用基础操作

| 功能 | Windows | macOS | 备注 |
| :--- | :--- | :--- | :--- |
| 复制 / 剪切 / 粘贴 | `Ctrl+C/X/V` | `⌘+C/X/V` | Finder 移动文件：`⌘+C` 后 `⌥⌘+V` |
| 撤销 / 重做 | `Ctrl+Z` / `Ctrl+Y` | `⌘+Z` / `⇧⌘+Z` | |
| 全选 | `Ctrl+A` | `⌘+A` | |
| 查找 / 替换 | `Ctrl+F` / `Ctrl+H` | `⌘+F` / `⌥⌘+F` | 替换键位随应用而异（Word Mac 用 `⇧⌘+H`） |
| 保存 / 新建 / 打开 | `Ctrl+S/N/O` | `⌘+S/N/O` | |
| 关闭窗口 / 标签 | `Ctrl+W` | `⌘+W` | Mac 关窗口≠退出程序 |
| 退出程序 | 关窗口即退出 | `⌘+Q` | Mac 必须 `⌘+Q` 才真正退出 |
| 永久删除（不进回收站） | `Shift+Del` | `⌥⌘+Del` | |
| 重命名文件 | `F2` | `Return` | Mac 回车=重命名，打开文件用 `⌘+↓` |
| 粘贴为纯文本 | `Ctrl+Shift+V` | `⌥⇧⌘+V` | 去格式粘贴 |
| 关闭程序 / 窗口 | `Alt+F4` | `⌘+Q` / `⌘+W` | Alt+F4 在桌面按=关机对话框 |

## 2. 系统与窗口管理

| 功能 | Windows | macOS | 说明 |
| :--- | :--- | :--- | :--- |
| 全局搜索 | `Win+S` | `⌘+Space`（Spotlight） | |
| 切换应用 | `Alt+Tab` | `⌘+Tab` | 加 `Shift` 反向 |
| 切换同应用多窗口 | 无原生（部分应用 `Ctrl+Tab`） | ``⌘+` ``（反引号） | |
| 显示桌面 | `Win+D` | `Fn+F11`（主）；旧版/部分机型 `⌘+F3` | 以 系统设置>桌面与程序坞>Mission Control>显示桌面 为准 |
| 锁定屏幕 | `Win+L` | `⌃⌘+Q` | |
| 强制退出 | `Ctrl+Shift+Esc`（任务管理器）/ `Ctrl+Alt+Del` | `⌥⌘+Esc` | |
| 截图（区域） | `Win+Shift+S` | `⌘⇧+4` | Win 截图工具；Mac：3=全屏、4=区域、5=工具栏 |
| 录屏 | `Win+Alt+R`（Xbox Game Bar） | `⌘⇧+5` → 录制 | |
| 虚拟桌面切换 | `Win+Ctrl+←/→` | `⌃+←/→` | |
| 新建虚拟桌面 | `Win+Ctrl+D` | 无默认键（Mission Control 内点 `+`） | 原手册"⌃+↑/⌃+↓ 新建"有误：那是进入调度中心/显示应用窗口 |
| 关闭当前虚拟桌面 | `Win+Ctrl+F4` | — | 不是单个 `F4` |
| 任务视图 / 调度中心 | `Win+Tab` | `⌃+↑` | |
| 隐藏当前 / 其他应用 | 无原生 | `⌘+H` / `⌥⌘+H` | |
| 只保留当前窗口、最小化其余 | `Win+Home` | — | |
| 打开设置 | `Win+I` | `⌘+,`（应用内） | |
| 资源管理器 / Finder | `Win+E` | `⇧⌘+C`（电脑）/ Dock | |
| 剪贴板历史 | `Win+V`（需开启） | 需第三方（Maccy/Paste） | 详见 §10.2 |
| 通知中心 / 快速设置 | `Win+N` / `Win+A` | 点右上角 | Win11 |
| 表情符号面板 | `Win+.` 或 `Win+;` | `⌃⌘+Space` | |

## 3. 浏览器高频操作

| 功能 | Windows | macOS | 备注 |
| :--- | :--- | :--- | :--- |
| 新建 / 关闭标签 | `Ctrl+T` / `Ctrl+W` | `⌘+T` / `⌘+W` | |
| 重开刚关的标签 | `Ctrl+Shift+T` | `⇧⌘+T` | 可连续按恢复多个 |
| 切换标签 | `Ctrl+Tab` / `Ctrl+1~8` | `⌘+⌥+←/→`（Chrome）/ `⌃+Tab`（Safari） | `1~8` 跳第 N 个，`9` 跳最后 |
| 地址栏聚焦 | `Ctrl+L` / `Alt+D` | `⌘+L` | |
| 后退 / 前进 | `Alt+←` / `Alt+→` | `⌘+[` / `⌘+]` | |
| 刷新 / 强制刷新（绕缓存） | `F5` / `Ctrl+F5` | `⌘+R` / `⌘⇧+R` | 本控制台改版后看不到新界面就强刷 |
| 清除浏览数据 | `Ctrl+Shift+Del` | `⇧⌘+Del` | 排查缓存/登录问题 |
| 开发者工具 | `F12` / `Ctrl+Shift+I` | `⌘⌥+I` | |
| 全屏 / 无痕窗口 | `F11` / `Ctrl+Shift+N` | `⌃⌘+F` / `⌘⇧+N` | |
| 书签管理器 | `Ctrl+Shift+O` | `⌘⌥+B` | |
| 向下/向上滚一屏 | `Space` / `Shift+Space` | 同左 | |

## 4. Office 文档（Word/Excel）

| 功能 | Windows | macOS | 备注 |
| :--- | :--- | :--- | :--- |
| 加粗 / 斜体 / 下划线 | `Ctrl+B/I/U` | `⌘+B/I/U` | |
| 复制 / 粘贴格式（格式刷键） | `Ctrl+Shift+C` → `Ctrl+Shift+V` | `⌘⌥+C` → `⌘⌥+V` | |
| 插入超链接 | `Ctrl+K` | `⌘+K` | |
| 跳到文档首 / 尾 | `Ctrl+Home` / `Ctrl+End` | `⌘+↑` / `⌘+↓` | |
| 按词移动光标 | `Ctrl+←/→` | `⌥+←/→` | 加 `Shift` 为按词选择 |
| 行首 / 行尾 | `Home` / `End` | `⌘+←` / `⌘+→` | |
| 段落对齐（左/中/右/两端） | `Ctrl+L/E/R/J` | `⌘+L/E/R/J` | |
| 插入分页符 | `Ctrl+Enter` | `⌘+Enter` | |
| Excel 快速填充 | `Ctrl+E` | — | 智能拆分/合并列 |
| Excel 自动求和 | `Alt+=` | — | |
| Excel 绝对引用切换 | `F4` | `Fn+F4`（或设为标准功能键后的 `F4`） | `$A$1` 相对/绝对；Mac 上 `⌘+T` 是"转换为表格"，不是切换引用 |
| Excel 插入时间 / 日期 | `Ctrl+Shift+;` / `Ctrl+;` | `⌃⌘+;` / `⌘+;` | 注意两列顺序：时间在前日期在后 |

## 5. IDE / 代码编辑器通用（VS Code / JetBrains / VS）

> 默认为常见键位，因 IDE 与键位映射方案而异，可用命令面板反查确认。

| 功能 | Windows | macOS |
| :--- | :--- | :--- |
| 快速打开文件 | `Ctrl+P` | `⌘+P` |
| 全局搜索（跨文件） | `Ctrl+Shift+F` | `⇧⌘+F` |
| 命令面板 | `Ctrl+Shift+P` | `⌘⇧+P` |
| 转到定义 | `F12` | `F12` / `⌘+Click` |
| 转到行 | `Ctrl+G` | `⌃+G` |
| 速览定义（不跳转） | `Alt+F12` | `⌥+F12` |
| 查找引用 | `Shift+F12` | `⇧F12` |
| 重命名符号 | `F2` | `F2` |
| 快速操作 / 修复 | `Ctrl+.` | `⌘+.` |
| 格式化代码 | `Shift+Alt+F` | `⇧⌥+F` |
| 多光标（上/下加光标） | `Ctrl+Alt+↓/↑` | `⌃⌥+↓/↑` |
| 选中相同单词（逐个） | `Ctrl+D` | `⌘+D` |
| 选中全部相同词 | `Ctrl+Shift+L` | `⌘⇧+L` |
| 整行移动 | `Alt+↑/↓` | `⌥+↑/↓` |
| 复制当前行（向下） | `Shift+Alt+↓` | `⇧⌥+↓` |
| 删除整行 | `Ctrl+Shift+K` | `⇧⌘+K` |
| 注释 / 取消注释 | `Ctrl+/` | `⌘+/` |
| 折叠全部 / 展开全部 | `Ctrl+K Ctrl+0` / `Ctrl+K Ctrl+J` | `⌘K ⌘0` / `⌘K ⌘J` |
| 集成终端开关 | ``Ctrl+` `` | ``⌃+` `` |

> ⚠️ 原手册"复制当前行 `Ctrl+Shift+D`"有误：那是 VS Code 打开调试视图的键。VS Code 复制行向下是 `Shift+Alt+↓`。

## 6. 命令行 / 终端

> 终端多沿用 Unix/Emacs 风格，与 GUI 差异较大。Bash/Zsh 键位与 macOS 列一致。

| 功能 | Windows（PowerShell/CMD） | macOS（Terminal/iTerm2）/ Bash |
| :--- | :--- | :--- |
| 中断进程 | `Ctrl+C` | `Ctrl+C` |
| 行首 / 行尾 | `Home` / `End` | `Ctrl+A` / `Ctrl+E` |
| 删除前一词 | `Ctrl+Backspace` | `Ctrl+W` |
| 删到行首 / 行尾 | CMD 无；PowerShell（PSReadLine）`Ctrl+Home` / `Ctrl+End` | `Ctrl+U` / `Ctrl+K` |
| 清屏 | `cls` / `clear`（PS 别名） | `Ctrl+L` / `clear`（iTerm2/Terminal 也可 `⌘+K`） |
| 自动补全 | `Tab` | `Tab` |
| 历史命令搜索 | `↑/↓`；PowerShell 支持 `Ctrl+R`（CMD 无，`Ctrl+G` 放弃搜索） | `Ctrl+R`（再按继续向前搜） |
| 历史菜单 | CMD：`F7`（弹出历史列表）；CMD：`F9` 按编号调出 | 无（Bash 用 `Ctrl+R`） |
| 光标左/右一词 | `Ctrl+←/→` | `⌥+←/→`（Terminal 需设置；iTerm2 默认） |
| 退出 Shell | `exit` / `Ctrl+D` | `Ctrl+D` / `exit` |
| 挂起进程（`fg` 恢复） | 无 | `Ctrl+Z` |
| 分屏 | Windows Terminal：`Alt+Shift+D`（自动）/ `Alt+Shift+-`（横向） | iTerm2：`⌘+D`（垂直）/ `⌘⇧+D`（横向） |

## 7. 调试专用

> F 系功能键请先确认已设为标准功能键（见 [9.2](#92-f1-f12-功能键冲突mac-重灾区)）。

### 7.1 Visual Studio（Windows）

| 功能 | 快捷键 | 说明 |
| :--- | :--- | :--- |
| 开始 / 继续调试 | `F5` | |
| 开始执行（不调试） | `Ctrl+F5` | 启动更快 |
| 停止调试 | `Shift+F5` | |
| 单步跳过 / 进入 / 跳出 | `F10` / `F11` / `Shift+F11` | Over / Into / Out |
| 设置 / 取消断点 | `F9` | |
| 条件断点 | 右键断点 → 条件 | |
| 运行至光标 | `Ctrl+F10` | |
| 局部变量 / 监视窗口 | `Ctrl+Alt+V,L` / `Ctrl+Alt+W,W` | |
| 立即窗口 | `Ctrl+Alt+I` | |

### 7.2 VS Code

| 功能 | Windows | macOS |
| :--- | :--- | :--- |
| 启动调试 / 继续 | `F5` | `F5` |
| 开始执行（不调试） | `Ctrl+F5` | `⌃F5` |
| 单步跳过 / 进入 / 跳出 | `F10` / `F11` / `Shift+F11` | `F10` / `F11` / `⇧F11` |
| 停止调试 | `Shift+F5` | `⇧F5` |
| 切换断点 | `F9` | `F9` |
| 运行到光标 | 右键 → 运行到光标处 | 同左 |

### 7.3 JetBrains（IDEA / PyCharm / WebStorm）

| 功能 | Windows/Linux | macOS |
| :--- | :--- | :--- |
| 运行 / 调试 | `Shift+F10` / `Shift+F9` | `⌃+R` / `⌃+D` |
| 继续 Resume | `F9` | `⌘⌥+R` |
| 单步跳过 / 进入 / 跳出 | `F8` / `F7` / `Shift+F8` | `F8` / `F7` / `⇧F8` |
| 强制单步进入 | `Alt+Shift+F7` | `⌥⇧F7` |
| 切换断点 | `Ctrl+F8` | `⌘F8` |
| 查看断点面板 | `Ctrl+Shift+F8` | `⌘⇧F8` |
| 运行到光标 | `Alt+F9` | `⌥⌘+R` |

> ⚠️ 原手册 macOS 单步键写成 `⌘F8/⌘F7` 有误——JetBrains 的 macOS 单步与 Windows 相同（F8/F7/⇧F8）；`⌘F8` 是**切换断点**。

### 7.4 Xcode / LLDB

| 功能 | 快捷键 | 说明 |
| :--- | :--- | :--- |
| 运行 | `⌘+R` | |
| 切换断点（当前行） | `⌘+\` | |
| 单步跳过 / 进入 / 跳出 | `F6` / `F7` / `F8` | 需标准功能键设置 |
| LLDB 继续 / 下一步 / 进入 | `c` / `n` / `s` | |
| LLDB 打印变量 | `p 变量` / `po 对象` | print / print-object |

## 8. 影音操作

### 8.1 网页播放器（B站 / YouTube 等，Win/Mac 通用）

> ⓘ **快捷键生效前提**：先点击视频区域获得焦点，否则按 `Space` 会滚动页面而不是播放——这是最常见的"快捷键没用"误解。

| 功能 | 快捷键 | 说明 |
| :--- | :--- | :--- |
| 播放 / 暂停 | `Space` / `K` | |
| 快退 / 快进 5 秒 | `←` / `→` | YouTube `J/L` 为 10 秒，连按加速 |
| 音量 / 静音 | `↑` / `↓` / `M` | |
| 全屏 / 网页全屏 | `F` / `T`（B站） | 退出按 `Esc` |
| 倍速 增 / 减 / 归位 | `Shift+>` / `Shift+<` / `Shift+0` | `0`=1 倍速 |
| 跳到 10%…90% | 数字键 `1~9` | |
| 字幕开关 | `C`（YouTube） | |
| 弹幕开关 | `D`（B站） | 发弹幕点输入框或 `Enter` |

### 8.2 本地播放器

| 软件 | 播放/暂停 | 快进/快退 | 全屏 | 倍速 | 备注 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| PotPlayer（Win） | `Space` | `←/→` | `Enter`/`F` | `Shift+</>` | 功能极多，可在选项里自定义 |
| VLC | `Space` | `←/→`（±10s） | `F` | `+`/`-` | `N` 下一首、`P` 上一首、`S` 停止（`B` 是切换音轨，不是切歌） |
| IINA（macOS） | `Space` | `←/→` | `F`/`⌘+F` | `[`/`]` | 类 mpv 键位 |
| QuickTime（macOS） | `Space` | `J/K/L`（倒带/暂停/快进） | `⌘+F` | 播放条菜单 | |
| mpv（跨平台） | `Space` / `P` | `←/→` | `f` | `[`/`]` | 章节/曲目切换用 `<` / `>` |

### 8.3 系统媒体控制

| 功能 | Windows | macOS |
| :--- | :--- | :--- |
| 播放/暂停、上一首/下一首 | 媒体键 `⏯⏮⏭`（笔记本常需 `Fn` 组合） | `F7/F8/F9`（视 Fn 设置） |
| 音量 | 媒体键 | `F11/F12`（静音 `F10`） |

## 9. 快捷键冲突排查与解决

### 9.1 输入法 vs 代码补全（最高频）

| 冲突键 | 占用方 | 期望功能 | 解决方案 |
| :--- | :--- | :--- | :--- |
| `Ctrl+Space` | Win 输入法中英切换 | IDE 代码补全 | 输入法设置改用 `Shift` 单键切换；或 PowerToys 重映射 |
| `⌃+Space` | macOS 切换输入源 | IDEA 补全 | 系统设置>键盘>快捷键>输入源 取消，或 IDEA 切 macOS 键位图 |
| `⌘+Space` | macOS Spotlight | 应用命令 | 系统设置>快捷键>聚焦 修改 |

### 9.2 F1-F12 功能键冲突（Mac 重灾区）

Mac 默认 F 键优先执行音量/亮度，导致调试（F5/F10/F11）、刷新、开发者工具（F12）失效。
**推荐**：系统设置 > 键盘 > 快捷键 > 功能键 → 开启「将 F1、F2 等用作标准功能键」（此后调音量亮度需加 `Fn`）。个别键仍被占用（如 F11 显示桌面）去 Mission Control 分类单独取消。
Windows 笔记本若 F 键触发音量/亮度，按 `Fn+Esc`（FnLock）切换。

### 9.3 开发软件之间的键位冲突

| 场景 | 冲突键 | 解决 |
| :--- | :--- | :--- |
| VS Code ↔ IDEA 习惯混用 | `Ctrl+Space`、`Ctrl+Alt+L` 等 | VS Code 装 "IntelliJ IDEA Keybindings" 扩展，或 IDEA 装 VSCode keymap |
| VS Code ↔ 浏览器 DevTools | `F12` | 浏览器 DevTools 用 `⌘⌥I`；IDE 转定义改 `Ctrl+Click` |
| IntelliJ 补全 `⌘+D` ↔ Mac 重复行 | `⌘+D` | IDEA 用 macOS 键位图；VS Code 复制行 `⇧⌥+↓` |
| Windows Terminal ↔ 系统复制 | `Ctrl+Shift+C` | WT 设置>操作 里改复制粘贴键 |
| 远程桌面 ↔ 本地截屏 | `Win+Shift+S` | 远程工具关"应用 Windows 热键" |

### 9.4 第三方软件抢占全局热键（常见示例）

| 软件 | 冲突键 | 被抢占功能 | 解决 |
| :--- | :--- | :--- | :--- |
| 微信/QQ | `Ctrl+Alt+A`（截图） | 自定义截图 | 改/禁用其截图热键 |
| 钉钉/飞书 | `Ctrl+Shift+A`、`Alt+Space` | 搜索/截图 | 应用设置>快捷键 |
| NVIDIA 覆盖层 | `Alt+Z`、`Alt+F9/F10` | 录制/快照 | 关游戏内覆盖快捷键 |
| 网易云音乐 | `Ctrl+Alt+←/→`、`F8` | 代码移动/播放 | 关全局快捷键 |
| Snipaste | `F1`、`F3` | 调试/帮助 | 改贴图/取色热键 |
| Listary/Everything | `Alt+Space` 等 | 窗口菜单 | 调整或禁用 |
| PowerToys Run / Raycast / Alfred | `Alt+Space` / `⌥+Space` | 启动器呼出 | 见 [§10.4](#104-启动器--快捷启动)；建议保留给启动器，其余软件改键 |
| 搜狗/百度输入法 | `Ctrl+Shift+U/F` | 全局搜索/自定义 | 关"简繁切换""造词"热键 |

> 排查工具：Windows 用 **PowerToys Keyboard Manager**（重映射/查占用）或 **OpenArk**（内核级看系统热键）。

### 9.5 冲突排查方法论

1. **完全没反应** → 系统/输入法层拦截，查系统快捷键与输入法设置。
2. **触发别的功能** → 系统快捷键优先级更高，去系统设置关闭。
3. **仅某个应用失效** → 应用内 keymap 覆盖或焦点问题。
   - VS Code：命令面板执行 `Developer: Toggle Keyboard Shortcuts Troubleshooting`，按键后看输出面板显示被谁占用。
   - IDEA：Keymap 搜操作，出现 "conflict with..." 警告可跳转修改。
   - 插件冲突：`code --disable-extensions` 启动后逐个排查。

## 10. 效率增强

### 10.1 跨平台双机党键位统一

| 方案 | 工具 | 思路 | 适用 |
| :--- | :--- | :--- | :--- |
| Mac 模拟 Win | Karabiner-Elements（开源免费） | `Control`↔`Command` 互换 | Win 主力者用 Mac |
| Win 模拟 Mac | AutoHotkey | `Alt`→Option、`Win`→Command | Mac 主力者用 Win |
| 原生修饰键交换 | macOS 系统设置（免装） | 键盘>修饰键>选外接键盘>交换 Ctrl/⌘ | 外接 Win 键盘时 |

> 建议从复制/粘贴/切窗/关标签 3–5 个高频操作起步，适应一周再扩展。

### 10.2 剪贴板历史

| 平台 | 快捷键 | 说明 |
| :--- | :--- | :--- |
| Win10/11 | `Win+V` | 首次按开启；25 条历史，可固定常用片段，跨设备同步 |
| macOS 原生 | 无 | 用 **Maccy**（开源免费）或 **Paste** |

### 10.3 其他高频实用

| 场景 | Windows | macOS |
| :--- | :--- | :--- |
| 地址栏/路径栏定位 | 资源管理器 `Alt+D` 或 `Ctrl+L` | Finder `⌘⇧+G`（前往文件夹） |
| 上级目录 | 资源管理器 `Alt+↑` | Finder `⌘+↑` |
| 文件属性 / 简介 | `Alt+Enter` | `⌘+I` |
| 任务管理器 / 活动监视器 | `Ctrl+Shift+Esc` | Spotlight 搜"活动监视器" |
| 输入法切换 | `Win+Space` | `⌃+Space` |
| 投影/多屏 | `Win+P` | `⌘+F1`（需 Fn，镜像/扩展） |
| 取色器 | PowerToys Color Picker：`Win+Shift+C` | 系统自带无，可用第三方 |
| 重启资源管理器 / Finder | 任务管理器重启 explorer | 终端 `killall Finder` |
| 系统信息 | `Win+Pause`（无 Pause 键：设置>系统>关于） | 苹果菜单 > 关于本机 > 系统报告 |

### 10.4 启动器 / 快捷启动

| 工具 | 平台 | 默认热键 | 说明 |
| :--- | :--- | :--- | :--- |
| PowerToys Run | Windows | `Alt+Space` | 微软官方免费开源：启动/算式/单位换算/`>` 执行命令 |
| Raycast | macOS | `⌥+Space` | Spotlight 增强，剪贴板/窗口管理一体化 |
| Alfred | macOS | `⌥+Space` | 老牌启动器，Workflow 自动化强 |

> ⚠️ 启动器默认热键正是 [§9.4](#94-第三方软件抢占全局热键常见示例) 里 `Alt+Space` 的冲突高发区（钉钉/飞书/Listary 也在抢）。启用 PowerToys Run 后建议**保留给启动器，其余软件改键**。

> ⚠️ 原手册两处更正：资源管理器定位地址栏是 `Alt+D`/`Ctrl+L`（`Ctrl+E` 是搜索框）；PowerToys 取色器默认 `Win+Shift+C`（`Win+Shift+V` 不是取色）。

## 11. 官方速查表入口

| 软件 | 入口 |
| :--- | :--- |
| VS Code | 命令面板 `Open Keyboard Shortcuts` 或 `Ctrl+K Ctrl+S`（`⌘K⌘S`）；官方 PDF 速查表 |
| JetBrains | Settings>Keymap，齿轮 > Find Actions by Shortcut（按组合键反查）；官方 Reference Card PDF |
| Visual Studio | 工具>选项>环境>键盘；Microsoft Learn 打印速查表 |
| Sublime / Figma / Notion / Obsidian / Blender | 应用内快捷键设置页或官网 cheat sheet（Figma `Ctrl+/` 弹出） |
| Vim/Neovim | `:help index` / `:map` |

**通用方法**：① 应用内命令面板搜索反查（最准）；② 官网搜 keyboard shortcuts / cheat sheet；③ 用导出功能迁移键位配置。

## 12. 关键差异提示

1. **修饰键映射**：Win 键盘接 Mac，物理 `Alt`=Option、`Win`=Command，可在系统设置>修饰键调整。
2. **关窗口≠退出**：Mac `⌘+W` 仅关窗口，真正退出用 `⌘+Q`。
3. **Finder vs 资源管理器**：Mac `Return`=重命名、`⌘+↓`=打开，与 Windows 相反。
4. **IDE 键位**：上表取跨平台通用默认值，实际以各 IDE 命令面板反查为准。
