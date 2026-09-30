# UI 三层推导：为什么平台长成现在这个样子

> **状态：草稿·待审核。**
> **背景**：2026-09-30 用户批评「UI 非常难看」，并要求按 价值层→意图层→细节层 系统阐述现状依据；理论不足处针对性检索。
> **诚实审计结论**：此前 UI 细节（间距/字号/阴影/行宽）**大部分无据**——凭默认审美随手写；本文补齐理论依据、token 化修正（已应用于两份 demo 的 `ui-system` 样式层），并如实标注每条决策的认识状态。

## 〇、第一性原理：为什么「好看」不是装饰

**美学可用性效应（Aesthetic-Usability Effect）**：Kurosu & Kashimura (1995, Hitachi ATM 26 变体实验) 证明——用户判定**美观的界面更好用、更可信**，即使被明确要求只评价功能；Tractinsky et al. (2000) 跨文化复制；Sauer et al. (2022, IJHCS) 多期研究证明该效应长期存在而非首因错觉；机制解释为**加工流畅性**（好看的东西更好加工）。

对本平台的含义：目标人群（低心力、高敏感）对被对待的方式极度敏感——**丑 = 不可信 + 难用**，这不是审美偏好之争，是 F28 信任资产的直接输入。用户批评 UI 难看，在理论上等价于批评产品「不可信」。

## 1. 价值层（决定气质的三句话）

| # | 价值 | 来源 | 排除项 |
| --- | --- | --- | --- |
| V1 | 这个人心力有限：一切呈现以**降低认知负荷**为先 | 认知负荷理论；Miller 7±2；渐进披露（refer2 意图层原则库） | 排除：仪表盘式多栏密度、一屏多目标 |
| V2 | 这个人值得被好好对待：**本能层观感**直接进入信任 | 情感化设计三层次（候选 #37 Norman）；美学可用性效应（本节 §〇） | 排除：机构化的冷蓝企业感、粗糙默认样式 |
| V3 | 变强必须被看见（产品理念）：提升的呈现优先级最高 | u_progress_competence；philosophy §三 | 排除：把训练进度塞满首屏（主平台/产物平台主导权分离） |

## 2. 意图层（从价值推出的形态决策）

| 决策 | 为什么 | 依据 | 认识状态 |
| --- | --- | --- | --- |
| **单列居中，而非两侧布局** | ① 阅读行宽：正文最佳 50-75 字符/行（≈66 最优），单列文本块才能约束行宽——**Baymard 大规模可用性测试**；② 低心力人群一屏一事：双侧栏=并行信息=持续的认知税（V1 认知负荷）；③ 移动优先，居中单列天然适配；④ 两侧布局保留给未来「仪表盘角色」（如果出现） | Baymard Institute；UXPin；认知负荷理论 | **此前凭直觉，现已补理论 ✓** |
| **绿色系而非蓝色** | ① 语义：提升=生长，绿是「成长/健康/自然」的行业语汇（健身/正念类主流），与品牌隐喻（陪伴成长）同构；蓝=信任/能力/机构（银行/医疗的主流），偏冷、偏"机构感"——对高敏感人群，"不像一个机构"更亲和；② 差异化：健康类蓝色泛滥；③ **诚实声明**：色彩-情绪的实证证据弱于排版证据（效应小、语境依赖、个体差异大），绿色是「语义 + 差异化 + 一致性」的选择而**非强实证**——若随访数据说蓝色更好，换色成本只是一个 token | 行业惯例（Headspace/Calm 系绿色谱系；银行/医疗蓝色谱系）；色彩心理学为弱实证领域 | **原先无记录依据 → 已补（弱实证，诚实声明）✓；蓝色方案保留为 A/B 候选** |
| **每屏一件事 / 渐进披露** | V1 | 认知负荷；refer2 | 既有 ✓ |
| **首屏主导权分离**（主平台=提升轨迹；产物平台=训练进程） | philosophy §三（用户澄清） | 用户裁定 | 既有 ✓ |
| **动效克制 + 尊重 reduced-motion** | V1 + 前庭安全 | game-feel 响应阈值；WCAG | 既有 ✓ |

## 3. 细节层（token 化——本次修正，已应用于两份 demo 的 `ui-system` 样式层）

| token | 旧值（无据） | 新值（依据） | 依据 |
| --- | --- | --- | --- |
| 正文行宽 | 容器 860-920px，**段落不限宽** → 长行伤害阅读 | 段落 `max-width: 46rem`（≈66 个拉丁字符 / ~40 个中文字符/行） | Baymard 50-75ch，66 最优 |
| 间距 | 14/16/18/20/22 随手写 | **4/8pt 网格**：4/8/12/16/24/32/48（软网格；4px 微调 + 8px 步进） | 8pt grid 行业规范（UX Collective；Material） |
| 字号 | 浏览器默认 h 标签 | **1.25 大三度音阶**：14 / 16 / 20 / 25 / 31（UI 最常用比例，温和层级） | Material type system；type scale 实践 |
| 阴影 | 无（仅 1px 边框，层级只靠边框——扁平呆板的主因之一） | **分层柔和阴影**：`0 1px 2px + 0 3px 10px`（静止）/ `0 2px 4px + 0 10px 24px`（强调）——层级用亮度+投影双编码（格式塔） | Gestalt 分组原则（refer2 意图层形式库） |
| 顶栏 | 实色 | 半透明 + backdrop-blur——层级呼吸感 | 加工流畅性（好看=好加工） |
| 按钮（主） | 平色 | 微渐变 + 同色系投影——可按压感（affordance） | Norman 示能；情感化设计本能层 |
| muted 对比度 | #5b6b76（≈4.6:1） | 加深至 ≈5.5:1 | WCAG AA（4.5:1）留余量 |
| 圆角 | 12/14 混用 | 卡 14 / 控件 9 / 徽章 999 三档 | 一致性（重复原则，CRAP） |

**诚实声明**：上表「旧值」列在本次审计前**全部无据**。修正方式为追加 `ui-system` 样式层（两份 demo），旧样式保留可回滚。

## 4. 仍然未定的（不装懂，留给真实用户与数据）

- 绿 vs 蓝 vs 暖底色：弱实证领域，随访/A/B 裁决（token 已隔离，切换成本一个文件）；
- 插画与品牌质感：等候选 #37-44 走流水线后按入库方法论升级；
- 动效幅度：已守 reduced-motion；幅度偏好个体差异大（高敏感人群尤甚）——提供设置项比拍板更诚实。

## 来源

- [Baymard Institute — Readability: The Optimal Line Length](https://baymard.com/research-articles/line-length-readability)（50-75 字符/行，大规模测试）
- [NN/g — The Aesthetic-Usability Effect](https://www.nngroup.com/articles/aesthetic-usability-effect/)；[Laws of UX](https://lawsofux.com/aesthetic-usability-effect/)
- [Sauer et al. 2022, IJHCS — 美学可用性效应的长期研究](https://www.sciencedirect.com/science/article/pii/S1071581922000647)；[Ben-Zeev et al. CHI 2023 — 加工流畅性机制](https://dl.acm.org/doi/10.1145/3544549.3585739)
- [UXPin — Optimal Line Length](https://www.uxpin.com/studio/blog/optimal-line-length-for-readability/)
- [Material Design — The Type System](https://m2.material.io/design/typography/the-type-system.html)；[1.25 Major Third 字阶实践](https://medium.com/sfl-newsroom/typography-scaling-from-the-design-perspective-45d82f77ba95)
- [Marc Andrew — 8pt Soft Grid（UX Collective）](https://uxdesign.cc)
