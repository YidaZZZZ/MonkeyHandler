# MonkeyHandler 项目状态固化（STATE）

> **用途**：本文件是项目的**恢复点**（上下文恢复用；权威以仓库文档与审核门为准）——对话上下文被压缩或新会话接入时，以本文件 + git 历史 + 记忆恢复全部上下文。
> **更新纪律**：每完成一个里程碑或重大裁决，更新本文件。
> **最后更新**：2026-10-03（D15 批复；exe 走查 + 白屏修复 cdd57b6；重建重发 ×2 + 构建区分 8c4a11b；**D17 按目标动态调研管线落地**——三本著作 + 逐项 src 引用强制）

## 一、产品一页纸

**MonkeyHandler**：创始人自用的双引擎陪伴平台，同时是可复用的元平台。

- **第一性原理**：软件的耐心无限——被完全看见的成本在架构上为零（创始人自述：拧巴、高敏感的抑郁症与发作性睡病患者；对他人倾诉是渴望被看见但注定不完全）。
- **双引擎**：觉察引擎「被看见」（心理侧：无评判倾诉与梳理、本心卡片）+ 技能引擎「训练平台」（技能侧：把第一步拆到低于心力阈值）。
- **目标人群**：低心力、高敏感人群（亚临床谱系；临床信号一律转介，D3）。
- **上瘾对象**：自我提升本身，不是机制（philosophy §〇）。
- **三层架构**（refer2）：价值观层（暂空）→ 意图层（五层结构+推导链+反证条件）→ 细节层（可判决规格）。
- **元平台 vs 实例**：本仓库=呈现与生产；训练计划平台=阶段性产物，数据回流（飞轮=本地迭代）。
- **北极星**：第 8 周还在练的比例。当前 n=1 自实验（创始人为唯一用户）。

## 二、关键裁决索引

| 编号 | 裁决 | 状态 |
| --- | --- | --- |
| D1 | 自用双引擎产品为主，可复用元平台次之，框架副产品 | ✅ 已落地 |
| D2 | guanzi 并入（见/格方法论平移，仓库归档为前身） | ✅ SEE_PROMPT v2 已并入 |
| D3 | 人群边界=亚临床谱系，临床转介 | ✅ 已入档 |
| D4 | 生成链路两周授权 | ✅ 第一段完成；双语/质量打磨中 |
| D5 | 审核队列建立，创始人亲自审核 | ✅ 53/53 已批准 |
| D6 | n=1 声明 + 危机资源国际化 | ✅ |
| D7 | 数据户口 = ~/.monkeyhandler | ✅ 已迁移 |
| D8 | 回程最小闭环 = M1 第一验收 | ✅ 已实现（test_history_reaches_prompt） |
| D9 | 快修包（README/U 编号/ADR/外发清单） | ✅ |
| D10 | 产品表面晋升（出 construction/demo，bat 转正） | ⬜ D4 收口后两周 |
| D11 | 危机文本外发=继续外发+如实标注 | ✅ 已落地 |
| D12 | 「越来越懂你」tab 登记/裁撤 | ⬜ 随 D10 |
| D13 | CLI 冒烟测试 + comu 回写 + 空目录清理 | ✅ |
| N 系 | 第二轮 N1-N10 与第三轮 N8-N11 详见 comu/质询书存档.md 与 git 历史 | ✅ 除 D10/D12 |
| D14 | 数据导出通道（设置页「导出全部数据」→ JSON，桌面模式落 ~/.monkeyhandler/exports） | ✅ |
| D16 | 使用说明五缺口（SmartScreen/findahelpline/n=1 版本化/CORS/版本号） | ✅ |
| D15 | v0.1.0 受众/承诺边界（ADR-0002 **已批准**：受众=有需要的人——被动可及≠主动推广，N7 挂起点不变；对 D1=补充；承诺边界三列生效） | ✅ 2026-10-03 批复 |
| D17 | **按目标动态调研**（创始人裁决，替代静态第二领域包路线）：每种训练目标出现 → 调研领域最相关三本著作 → 依托其方法论拆解 → **每个练习项 src 必须引用所列著作（代码强制）**；is_physical 分流保护文案（理论只在适用范围内迁移，健身文案不进认知域）；著作由 AI 检索、实例页如实标注「未经人工审核」 | ✅ 2026-10-03 落地（tests 20 绿） |
| Key | 旧 DashScope Key 已删除并复测作废（401）；新 Key 有效 | ✅ |
| 第四轮 N8/N9/N10/N11 | 危机外发如实标注（D11①）/机制叙事禁令/CliRunner 冒烟/快照盖章 | ✅ 全部关闭 |

## 三、关键文件地图

| 路径 | 内容 |
| --- | --- |
| `construction/philosophy.md` | 产品理念（§〇 内核呈现分离+机制叙事禁令 / 爽的七构件 / 价值层） |
| `construction/being-seen.md` | 被看见内核（五步法/危机协议/训猴和解/L0-L3 阶梯/D 裁决记录） |
| `construction/ui-system.md` | 平台 UI 意图基线（U1-U5 决策+反证条件）+ 细节层 token 依据 |
| `construction/intent/` · `detail/` · `profiling/` | 三套构筑策略（CWI/CWD/CUP 工作流与 P-INT/P-DTL/P-UPF prompt） |
| `construction/resources.md` | agent 实用资源清单（图标/图表/动效/音效） |
| `humanity/` | 著作库：36 本已批准 + 8 本候选；流水线规范；synthesis/（因素网/工作流/Prompt 库，已批准） |
| `docs/review-queue.md` | 审核台账（53/53；N5 每月抽审，首次 2026-10-31） |
| `docs/outbound-data.md` | 外发数据清单（D11 裁决：AI 模式危机文本随对话外发） |
| `docs/adr/ADR-0001` | LLM-only 裁决（被牺牲的东西） |
| `src/monkeyhandler/` | 引擎：core（humanity/profiling/user_model/llm/generate/render）、domains/fitness、cli、app（桌面桥） |
| `construction/demo/` | 主平台与训练平台界面（D10 将晋升出 demo 目录） |
| `dist/MonkeyHandler.exe` | 桌面单文件（v0.1.0 已发布） |
| `comu/`（不进 git） | 场外沟通：澄清报告、质询书存档、本轮回复 |

## 四、桌面版使用与分发

- 启动：双击 `MonkeyHandler.bat`（仓库根）或 `python -m monkeyhandler app`（pywebview 优先，Edge/Chrome --app 兜底）；
- **创始人手动测试 = 运行 `dist\MonkeyHandler.exe`**（不是 bat、不是下载副本）——因此执行侧纪律：**每次源码变更后必须重建双版本并报构建时间**；创始人用设置页版本号的「（构建 …）」时间戳核对 dist 是否最新（旧构建无时间戳=10-03 22:34 之前的版本，含死按钮/白屏 bug）；重建时若 exe 被占用（创始人正开着）会 PermissionError——需先结束进程（数据在本机 localStorage，不丢）；
- 打包（版本号唯一来源 = pyproject.toml）：`python build_exe.py` → **开发者版** `dist/MonkeyHandler-dev.exe`（设置页版本号带 -dev+本地构建时间，窗口标题标「开发版」，不产 zip）；`python build_exe.py --release` → **发布版** `dist/MonkeyHandler.exe` + `MonkeyHandler-v<ver>-win64.zip`（Release 资产，标题/版本号干净）；源码运行（bat / python -m）标题同样标「开发版」，设置页版本号显示 v0.1.0+src；
- 数据：`~/.monkeyhandler/`（ai.json / webview / instances / app-profile）；
- **分发**：v0.1.0 已发布 GitHub Releases（exe + zip 含双语说明）；README 快速开始指向 Releases。

## 五、进行中与待办

| 项 | 说明 |
| --- | --- |
| D4 收口 | 双语实例；生成内容质量打磨（D17 管线就位后以真实计划检验） |
| D17 复验 | 用真实 Key 从 UI 重新生成「掌握大模型」计划；**人工核对三本著作是否真实、逐项依据是否成立**（AI 检索未经人工审核——审核门补位待做） |
| D10 | 产品表面晋升（界面出 demo 目录、bat 转正、tab 集合重审） |
| D12 | 「越来越懂你」登记或裁撤 |
| N5 | 2026-10-31 首次台账抽查（5 项） |
| M1 | SQLite（数据户口落位）、计划生成器接桌面、guanzi「格」平移 |
| 双语 | 实例界面英文（主平台已双语） |
| exe 走查 | ✅ 2026-10-03 完成（UIA 黑盒 × USERPROFILE 隔离）：危机路径/版本行/D14 导出全通过；发现并修复 genBtn/openInst2/langToggle 三死按钮（8c33d6f）+ **实例「打开」白屏（第三次反映：manifest 无 uri → open_uri('') → pywebview 空白页；cdd57b6）**；重建重发 ×2（Release 资产同步更新）；SmartScreen 腿待真实下载补测。记录在 comu/走查-2026-10-03/ |

## 六、技术教训（踩过的坑）

1. `t()` 自动调用函数字段——勿再写 `t("langBtn")()`（双重调用中断渲染）；
2. `python -m 包名` 需要 `__main__.py`；cli 命令函数名勿遮蔽 Typer 实例名（`def app()` 曾让子命令全失效——已改 app_window）；
3. Bridge.__init__：manifest 赋值必须先于 _migrate_legacy；
4. Windows 本地服务对中文文件名不可靠——生成实例文件名一律 ASCII（前缀+哈希）；
5. `chime()` 定义在 index.html——跨文件调用前确认目标模块有定义；
6. 本地 http.server 后台进程会在回合间死掉，浏览器测试前重启 + cache-bust；
7. Playwright 对 sticky 头部遮挡的按钮 click 会超时——用 evaluate 内 el.click() 绕过；
8. heredoc 传长中文脚本有截断风险——用 Write 工具写补丁脚本再执行；
9. PyInstaller 6.22.3 兼容 Python 3.14（担忧解除）；pywebview 数据持久化需 `private_mode=False, storage_path=…`；
10. **死按钮类 bug**：渲染型界面（innerHTML 重建视图）里按钮必须走 #app 事件委托；直接 `getElementById(...).addEventListener` 只对初始视图存在的元素有效。新加按钮后用「grep id → 找 `e.target.id ===` 分支」自查一遍（走查发现 genBtn 自诞生起从未被调用）；
11. **桌面走查方法**：exe 无法外部开 CDP（pywebview 程序化 AdditionalBrowserArguments 压掉 WEBVIEW2_* 环境变量）→ 用 PowerShell UIA 驱动真实窗口（脚本需 BOM；Chromium 可访问性要预热触碰两遍才放开；textContent 原位更新后 UIA Name 不刷新——用磁盘副作用做证据；pywebview 空 URL 会加载内置空白页，a11y 文档名形如 data:text/html;base64）；数据隔离用 `USERPROFILE=<tmp>` 重定向（全部数据路径派生自 `Path.home()`），真实户口零触碰；
12. **「当场路径」≠「回流路径」**：generate() 当场返回 uri 所以生成后打开一直正常，重启后从 manifest 重开才暴露 uri 缺失——测试与走查必须覆盖「重启后的数据回流」，用户反映三次的 bug 往往藏在没人重跑的老路径上。

## 七、质询记录

- 第一轮（九问 + D1-D6）：全部关闭，见 comu/质询书存档.md 与 git 历史（37334c7 前后）；
- 第二轮（N1-N10 + D7-D9）：全部关闭（数据户口、回程闭环、N4 三件、N5/N6）；
- 第三轮（N8-N11 + D11-D13 + Key）：全部关闭（D11 裁决①、机制叙事禁令、CliRunner、快照盖章、Key 删除+复测）；
- 第四轮（N12-N15 + D14/D15/D16 + N7 重申）：D14/D16/N15 已闭环（ae9e010/642feb4）；D15 已批复（2026-10-03，ADR-0002 生效）；N7 维持 re-park 至首次推广动作前；exe 全流程走查（外包预案必做）待派发；
- 质询方预告下轮验收：回程数据流 ✓、数据户口 ✓——均已于第三轮交付；下轮验收 D15「有没有编号」→ 已有（本表 D15 行）。
