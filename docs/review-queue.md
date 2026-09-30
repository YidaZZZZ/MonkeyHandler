# 审核队列（D5 裁决 · 2026-09-30 建立）

> **裁决背景**：创始人选择**亲自审核**（否决了「降级为 AI 草稿」方案），故建立本队列作为唯一审核台账。
> **使用方式**：按批次从上往下审；每审完一行，把「状态」改为 `已审核（日期）`；有问题直接在行内批注（格式：`> 审核意见：……`），由构筑侧修订后复审。
> **审核纪律**：著作的审核点 = ① 总结是否忠实 ② 降级/入库判定是否认可 ③ 提取的提示词是否可用；文档的审核点 = 每份文件开头的「状态」行所列内容。
> **状态图例**：⬜ 待审核 · ✅ 已审核 · 🔧 修订中 · ❌ 驳回待重做

## 批 1 —— 解锁生成链路与 Prompt 库（D4 开工前需完成）

| # | 对象 | 位置 | 审什么 | 状态 |
| --- | --- | --- | --- | --- |
| W1 | 掌控习惯（样例基准） | humanity/works/atomic-habits/ | 格式基准；「1% 复利→存疑」「身份叙事降级」判定；提取 P1-P3/M1-M3 | ⬜ |
| W2 | 心流（样例基准） | humanity/works/flow/ | 格式基准；「85% 可校准启发式」处理；危机段删除后的验证 | ⬜ |
| W3 | 认知天性 | humanity/works/make-it-stick/ | 唯一全条目高置信，快速过 | ⬜ |
| W4 | 自我决定理论 | humanity/works/self-determination-theory/ | 动机质量/过度理由效应（喂 P-MOT-3） | ⬜ |
| W5 | 追求理解的教学设计 | humanity/works/understanding-by-design/ | 逆向设计（喂 P-PLAN-1 强制顺序） | ⬜ |
| W6 | 刻意练习 | humanity/works/peak/ | 10000h 澄清 + 1993 研究未复现存疑 | ⬜ |
| S1 | 影响因素网 | humanity/synthesis/factor-network.md | G1×G2 目标定义、F 节点、R1-R6 回路、风险因素表 | ⬜ |
| S2 | 逐层推导 | humanity/synthesis/derivation.md | 依从不等式、七构件、需求汇总表 | ⬜ |
| S3 | 工作流 W1-W6 | humanity/synthesis/workflows.md | 步骤合理性、守护节点标注 | ⬜ |
| S4 | Prompt 库总则 | humanity/synthesis/prompts/README.md | 唯一闸门原则、溯源链、风险标注 | ⬜ |
| S5 | 计划生成 Prompt | humanity/synthesis/prompts/planning.md | P-PLAN-1 强制顺序、P-REV-1 审核四问 | ⬜ |
| C2 | 平台 UI 意图基线 | construction/ui-system.md | D1-D5 决策与反证条件（居中单列/绿色弱实证/主导权分离/被看见剥离数字/克制动效） | ⬜ |
| C1 | 产品理念 | construction/philosophy.md | §〇 内核呈现分离；爽的七构件；成瘾对象错位表 | ⬜ |

## 批 2 —— 心理侧与其余基础著作

| # | 对象 | 位置 | 审什么 | 状态 |
| --- | --- | --- | --- | --- |
| C3 | 被看见内核 | construction/being-seen.md | 五步法、危机协议、训猴和解、L0-L3 阶梯、D1-D5 裁决记录 | ⬜ |
| C9 | 被看见实装 | construction/demo/main.html（see 模块 + SEE_PROMPT v2） | SEE_PROMPT（guanzi 并入版）、危机关键词与覆盖层、本心卡片表单 | ⬜ |
| C5 | 个性化了解构筑策略 | construction/profiling/（README/map/prompts/workflow） | 识人方法论迁移是否完整、CUP 验收线 | ⬜ |
| W7 | 思考，快与慢 | humanity/works/thinking-fast-and-slow/ | 社会启动不入库维持；锚定入库 | ⬜ |
| W8 | 终身成长 | humanity/works/mindset/ | 干预效应量降级维持 | ⬜ |
| W9 | 驱动力 | humanity/works/drive/ | 削弱效应边界（奖励形态三问） | ⬜ |
| W10 | 我们为什么要睡觉 | humanity/works/why-we-sleep/ | 具体数字待复核维持；核心结论入库 | ⬜ |
| W11 | 运动改造大脑 | humanity/works/spark/ | 相关性定性维持 | ⬜ |
| W12 | 沉思录 | humanity/works/meditations/ | 哲学标准声明；可控性归属 | ⬜ |
| W13 | 传习录 | humanity/works/chuanxilu/ | 知行合一→行为证据 | ⬜ |
| W14 | 坚毅 | humanity/works/grit/ | 特质归因降级维持（Credé 2017） | ⬜ |
| W15 | 习惯的力量 | humanity/works/the-power-of-habit/ | 自我损耗复制失败降级维持 | ⬜ |
| W16 | 人性的弱点 | humanity/works/how-to-win-friends/ | 证据不足排除维持（名字效应/让对方说是） | ⬜ |
| W17 | 社会心理学（Myers） | humanity/works/social-psychology/ | 教材高置信快审 | ⬜ |
| W18 | 影响力 | humanity/works/influence/ | 稀缺使用面条目（P5）；石化林风险注记 | ⬜ |
| W19 | 助推 | humanity/works/nudge/ | 四条件为书内主张的定位 | ⬜ |
| W20 | "错误"的行为 | humanity/works/misbehaving/ | 新鲜感随访方法论 | ⬜ |
| W21 | 乌合之众 | humanity/works/the-crowd/ | 大量不入库维持（群体智力/种族性别断言）；重复-熟悉度 M3 | ⬜ |

## 批 3 —— 相邻学科与其余构筑文档

| # | 对象 | 位置 | 审什么 | 状态 |
| --- | --- | --- | --- | --- |
| W22-W36 | 相邻学科 15 本 | humanity/works/（rules-of-play → thinking-in-systems） | 各自「使用面补充」条目（留存钩子/紧迫稀缺/唤起音效/沉浸连续性/紧迫度编码等）+ 证据性排除维持 | ⬜ |
| C4 | 构筑总览 | construction/README.md | D1 裁决后的全景与初衷表述 | ⬜ |
| C5 | 意图层框架与映射 | construction/intent/（README/methodology-map） | 五层意图框架、方法论归属 | ⬜ |
| C6 | 细节层框架与映射 | construction/detail/（README/methodology-map） | S/R/C/ST 框架、映射调整后的完整性 | ⬜ |
| C7 | 实用资源清单 | construction/resources.md | 资源选型与许可证 | ⬜ |

## 统计

- 著作：36 本（批 1×6 / 批 2×15 / 批 3×15）
- synthesis：8 件（批 1×5 / 批 2×3）
- 构筑与内核：9 件（批 1×2 / 批 2×4 / 批 3×3）
- **合计 53 项**；批 1 完成（13 项）即可开工 D4 生成链路与解锁 Prompt 库运行时消费。
