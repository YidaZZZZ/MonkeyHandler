# 一个用户界面的交互系列工程，可以拆解成哪些更细化的元素，直到对这个工程能达到尽可能完备的描述

**用户:**

一个用户界面的交互系列工程，可以拆解成哪些更细化的元素，直到对这个工程能达到尽可能完备的描述

**元宝:**

模板已按"研发/产品团队自检"口径做成 Word，核心是把一个交互工程拆成**目标→结构→行为→观感**四层，一路细化到可被开发实现、被测试断言的最小颗粒度。

**最关键的拆解逻辑**（比表格本身更值得先看）：

- **结构层四层编号**：界面 S → 区域 R → 组件 C → 状态 ST。组件只定义一次、多处引用，靠编号复用，避免同一组件在不同界面各写一套规则。
- **行为层最小单元**：一次交互 = 一个事件 E（触发—约束—过程—结果—反馈—可撤销性）。事件必须穷举到成功、失败、超时、中断、重复触发五种结果。
- **状态是最易漏的一层**：要求每个组件列出完整状态全集（默认/悬停/聚焦/按下/加载/成功/失败/空/禁用/只读/部分选中），并规定每个状态都要写全"视觉+文案+可访问性+焦点"四处表达。
- **状态 × 异常交叉表**：把场景状态（空、加载、失败、断网、无权限、冲突…）与组件状态做笛卡尔积，是发现遗漏状态最快的方法。
- **多通道逐条声明**：鼠标/触控/键盘/读屏四种通道必须显式写"支持或不支持"，不允许默认假设。
- 附录给了"最小完备性自检"十条，写完问一遍就能判断够不够。

文档含目录、页脚页码、编号规范、评审门禁与变更追溯矩阵，正文以留白表格形式交付，可直接填项目内容。可访问性部分参考 WCAG 2.2 的 AA 要求与 WAI-ARIA 的角色/状态/属性模型；设计规格的"设计文件+开发事项"双层结构也按此组织。

需要提醒：第 12 章的质量阈值（100ms 反馈、60fps、目标 WCAG 等级）是**建议值**，必须按你们团队自己的基线确认后再定稿，我没法替你定这个数字。

用户界面交互系列工程拆解规格模板.docx

<details><summary>引用 21 篇资料作为参考</summary>

1. [Design Specifications Explained for UI-UX](https://uxpilot.ai/blogs/design-specifications)
2. [WCAG 2.2: A Guide to the Latest Web Accessibility Standard](https://www.accessibilitychecker.org/?p=97764/)
3. [ARIA & Keyboard Patterns](https://www.humanstandards.org/code-design-tokens/aria-keyboard-patterns)
4. [Usability Heuristics for User Interface Design Checklist](https://cleverchecklist.com/templates/design/usability-heuristics-for-user-interface-design-checklist)
5. [New in WCAG 2.2](https://webaim.org/standards/wcag/wcag22)
6. [AccessibleRichInternetApplications(WAI-ARIA)1.3](https://pr-preview.s3.amazonaws.com/w3c/aria/2535/b085915...0c83aea.html)
7. [10 Usability Heuristics for User Interface Design](https://useit.com/articles/ten-usability-heuristics/)
8. [WCAG 2.2 vs 2.1: What Changed and What It Means for Your Website (2026)](https://wcagsafe.com/blog/wcag-2-2-vs-wcag-2-1)
9. [Accessible Rich Internet Applications (WAI-ARIA) 1.3](https://w3c.github.io/aria/)
10. [UI/UX Audit Checklist for SaaS Products](https://lcgc.dev/blog/ui-ux-audit-checklist-for-saas-products)
11. [专家解读丨W3C正式推荐标准:Web内容无障碍指南(WCAG)2.2](https://siaa.org.cn/news_content?id=872)
12. [Module 6: Custom Widgets in Developer Modules, Curricula on Web Accessibility](https://w3.org/WAI/curricula/developer-modules/custom-widgets/)
13. [Creating Design Specs for Development](https://www.nngroup.com/articles/creating-design-specs-for-development/)
14. [Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/2020/WD-WCAG22-20200811)
15. [ARIA states and properties (attributes)](https://pr18914.content.dev.mdn.mozit.cloud/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes)
16. [A Checklist for Designing Mobile Input Fields](https://nngroup.com/articles/mobile-input-checklist/?lm=mobile-ux&pt=article)
17. [Everyone needs to know – New criteria in WCAG 2.2](http://service-manual.nhs.uk/accessibility/new-criteria-in-wcag-2-2)
18. [WAI-ARIA Overview](https://www-html@w3.org/WAI/standards-guidelines/aria)
19. [译文输入框的设计自查清单](https://www.sohu.com/a/19512656_114819)
20. [Web Content Accessibility Guidelines (WCAG) 2.2](https://equalweb.com/platform/standards/wcag-2-2.html)
21. [ARIA 状态及属性](https://developer.mozilla.org/zh-CN/docs/Web/Accessibility/ARIA/Reference/Attributes)

</details>

**用户:**

那么在细分拆解的完备描述之上一层是什么？从逻辑层面能够解释各个细节为什么选择现在这种表现形式

**元宝:**

上一层的答案，是**设计意图（Design Intent）**——一个比"交互规格"高一层的对象，它专门回答"为什么是这个样子，而不是另一个样子"。

规格是**判决性**的（必须如何）；意图是**解释性**的（为何如此）。两者合起来才是闭环：规格描述"是什么"，意图描述"为什么"和"凭什么判断它是好的"。

## 一、意图的五层结构

这是把意图从抽象落到可评审的关键。自下而上，每一层都为下一层提供理由，且**向上可追溯到业务价值，向下可推导到像素**。

**第 1 层 · 存在性理由（Why this at all）**

- 它解决谁的什么真实问题？证据是什么（访谈、数据、投诉、复盘）？
- 不做会损失什么，做了会引入什么代价？
- 这一层把"需求"变成"被验证过的命题"，是防需求蔓延的第一道闸门。

**第 2 层 · 价值与权衡（What trade-off）**

- 同时被服务的是谁：用户目标、商业目标、工程可持续性、合规要求？
- 冲突时按什么**排序规则**取舍？例如"撤销性 \> 操作效率 \> 视觉简洁"。
- 这一层是最容易失传的部分——决策人走了，只剩下一个看起来"莫名其妙"的规格。

**第 3 层 · 设计原则（By what rule）**
从跨学科理论中挑出与当前场景匹配的若干条，作为裁判依据，而非审美口癖：

- **认知层**：认知负荷（内在/外在/相关）、Miller 7±2、席克定律、心智模型与外推一致性、注意与感知选择
- **动作层**：菲茨定律（目标越大越近越快）、动作时间阈值（≈0.1s 即时 / 1s 保流 / 10s 注意力上限）、Doherty Threshold、转向/窄路径成本
- **系统层**：Tesler 复杂性守恒（复杂度必须有人承担，应尽量由系统而非用户承担）、渐进披露、防错优先于容错、可逆性
- **形式层**：格式塔分组原则（邻近、相似、封闭、连续、共同命运）、视觉层级、对齐与节奏
- **人本层**：可访问性作为底线而非功能、尊严与自主、选择权架构的伦理（默认值偏向谁的利益）

**第 4 层 · 设计模式与证据（What pattern, with what evidence）**

- 这里才出现"模式"：不是控件库里的按钮，而是**反复出现的、可迁移的问题—情境—解法三元组**。
- Christopher Alexander 的《建筑模式语言》用 253 个模式构成一套语言，每个模式都是"对问题情境的当前最佳猜测"，且明确标注了**置信度星级**——本身就是待经验修正的假说，而非教条
- 每个模式写清：适用情境 → 反作用力（forces）→ 解法 → 该模式支撑的上层与相邻模式
- 证据来源分层：领域数据/用户测试 \> 已验证的设计模式 \> 理论推导 \> 同行经验 \> 个人直觉。层级决定它在冲突中能赢多少次。

**第 5 层 · 形式映射（How principle becomes form）**

- 这是意图与规格的交界：把抽象原则落成**可观察的形式变量**。
- 例如"降低外在认知负荷"→ 主操作唯一且视觉权重最高、同屏 ≤ 3 个主操作、次要动作降一级语义色。
- 必须写出**中间变量**（认知负荷、操作时间、错误率、信任），否则无法验证，只能争吵。

## 二、逻辑上如何"证明"一个表现形式

单个表现形式的成立需要一整条推导链，缺一不可：

> **事实前提**（用户在该情境下做什么、怕什么、会怎么错）
> → **目标命题**（要让用户能感知/能撤销/能预期）
> → **设计原则**（菲茨/席克/认知负荷/可逆性…）
> → **机制假设**（为何该形式能改变该中间变量）
> → **形式决策**（热区 44pt、反馈 100ms 内、破坏性操作需二次确认）
> → **反证条件**（什么数据出现即推翻：误操作率未降、转化率跌穿阈值、键位路径失败）
> → **可测推论**（可被实验或埋点验证的预测）

没有"反证条件"的意图不是意图，只是事后包装。真正可解释的设计允许自己被证伪。

## 三、意图之间的三类关系：这才是"解释为什么"的实质

表现形式不是由单一意图线性推出的，**而是意图之间冲突后的产物**。

- **协作（support）**：一个决策同时支撑多个意图，是高质量方案的特征。
- **张力（tension）**：安全性要求二次确认，与效率要求一步完成冲突。解法不是"折中"，而是**分层**——默认路径最短、危险路径设闸、专家模式可配置。
- **涌现（emergence）**：Christopher Alexander 指出，"无名特质"不是由孤立模式产生的，而是**整个系统中相互依赖、多层级的模式全部稳定**时才涌现；死的模式会把内部张力泄漏到相邻模式 。对应到界面：**一个细节别扭，往往是它上一级意图与其他路径的意图不一致**，改它没用，要改那层规则。

## 四、意图本身也要分层治理

| 层级 | 内容 | 变更频率 |
| --- | --- | --- |
| 战略意图 | 产品使命、服务的人群、不可让步的底线 | 年 |
| 领域意图 | 该业务域的信任模型、风险等级、默认行为 | 季度 |
| 流程意图 | 某条任务的信息架构与决策顺序 | 版本 |
| 界面意图 | 某屏的唯一主操作与失败兜底 | 迭代 |
| 元素意图 | 某个按钮为何是主要动作、为何禁用 | 天 |

关键原则：**意图只挂在它需要的最小层级上**。一个元素级的意图不要塞进战略文档，一个战略级约束也不应藏在某个组件的批注里。

## 五、从"完备规格"到"完备规格+意图"的差距

上一版模板写的是"做什么/是什么"。要让它能被解释，还需补三张表：

- **意图登记表**：每条意图有 ID、归属层级、提出者、证据来源、置信度、适用条件、反证条件、到期复审日。
- **决策记录（ADR）**：决策背景 → 候选方案与各自代价 → 最终选择 → 被牺牲的东西 → 验证指标 → 复审触发条件。重点必须写"**被牺牲的东西**"，否则等于没权衡。
- **意图追溯矩阵**：意图 ID → 原则 → 模式 → 规格条目 → 验收指标，双向可达。

## 六、一句话总结

**规格告诉人"做成一个什么样子"；意图告诉人"这个样子凭什么比别的样子更对，以及在什么条件下该放弃它"。**

它之上是战略/使命（为什么做这个产品），之下才是交互规格。而意图真正可解释的条件只有三个：**能追溯到事实、能被冲突检验、能被数据证伪**。

> 提示：上述原则与阈值属于设计理论的通用层，具体到你项目的"默认值偏向谁""可接受的错误率""何时牺牲效率换安全"，必须由团队依据自身用户数据与合规边界**显式裁定**并写入决策记录——这部分没法从理论推出来。

需要的话，我可以把这五层意图结构、ADR 模板和意图追溯矩阵补成上一版 Word 文档的续章，合并成一个完整交付物。

<details><summary>引用 19 篇资料作为参考</summary>

1. [Christopher Alexander's A Pattern Language: analysing, mapping and classifying the critical response](https://cityterritoryarchitecture.springeropen.com/track/pdf/10.1186/s40410-017-0073-1)
2. [UX Design: Deep Dive into Human-Computer Interaction: Principles and Practices for Undergraduates](https://www.visualize-ai.com/ux-design-human-computer-interaction-principles-undergraduates)
3. [Living Structure Down to Earth and Up to Heaven: Christopher Alexander](https://arxiv.org/pdf/1909.11757)
4. [A Pattern Language: Towns, Buildings, Construction (Center for Environmental Structure Series)](https://seabc.librarika.com/search/detail/4177480)
5. [Design Theory](https://uxcel.com/glossary/theory)
6. [Philosophical Connections: Pattern Language](https://memeticcowboy.github.io/nemetics/knowledge/pattern-language.html)
7. [(un)Finished: Pattern Language for Human-Centric Architectural Evolution](https://www.mobt3ath.com/uplode/book/book-82500.pdf)
8. [Laws of UX & Cognition.](https://www.sinhaankur.com/framework)
9. [The Architecture of Choice: Designing Decision-Making Interfaces That Reduce Anxiety and Empower Users](https://timgraf.com/ux-design/the-architecture-of-choice-designing-decision-making-interfaces-that-reduce-anxiety-and-empower-users)
10. [The Timeless Way of Building](https://superbook.ai/books/the-timeless-way-of-building)
11. [模式语言](https://baike.baidu.com/item/%E6%A8%A1%E5%BC%8F%E8%AF%AD%E8%A8%80/4762141)
12. [Cognitive Psychology in Service Design – Services Management](https://uen.pressbooks.pub/servicesmgt?p=46)
13. [Teaching Patterns: A Pattern Language for Improving the Quality of Instruction in Higher Education Settings](https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=1050&context=etd)
14. [Pattern Language](https://emergent.wiki/wiki/Pattern_Language)
15. [Principles of great design](https://wwdc.ai/2026/250)
16. [The Quality Without a Name](https://www.metaphorex.org/entries/the-quality-without-a-name)
17. [Design Needs Complexity Theory](https://www.kaseyklimes.com/blog/design-needs-complexity-theory)
18. [交互设计原则全解析:构建用户友好型产品的理论基石](https://cloud.baidu.com/article/5285207)
19. [Lessons from Christopher Alexander](https://www.antoinebuteau.com/lessons-from-christopher-alexander/)

</details>

**用户:**

意图层上面还有层吗

**元宝:**

有。而且不止一层——**意图本身不是顶点，它是整条链的中段**。意图仍然在回答"这个系统应该如何设计"，它之上是\*\*规定"意图为什么是值得的、由谁决定、凭什么成立"\*\*的东西。

## 一、意图之上的四层

按"规定力"递减、抽象度递增排列：

**第 1 层 · 目的与价值主张（Purpose / Value Proposition）**
意图回答"为什么是这个样子"，这层回答"为什么要做这件事、为谁创造什么价值"。

- 服务谁、缓解什么困境、凭什么比现状好、我们凭什么做这件事。
- 关键：价值必须是**可失去的**——能说清"如果用户不因此受益，这个产品就没有存在理由"。这一层是意图的合法性来源，意图只是它的落地路径。

**第 2 层 · 立场、伦理与不可让步（Stance / Ethics / Non-negotiables）**
意图层做权衡，这层规定**权衡的边界与方向**——哪些东西不允许被交换掉。

- 隐私、尊严、公平、安全、可持续、合规底线；默认值的偏向；风险由谁承担；是否允许操纵、暗黑模式、成瘾设计。
- 这不是设计原则，而是**价值立场**。设计原则可以在不同方案间比较优劣，立场只分"接受或不接受"。它是意图层"取舍排序规则"的上游。

**第 3 层 · 战略与理论视角（Strategy / Theory of Change）**
规定"如何达成目的"的整体路径，也规定团队**看世界的方式**。

- 商业模式、生态位置、竞争取舍、增长路径、资源约束。
- 更深一层是**世界观/理论视角**：你怎么理解人与技术的关系、什么是"好体验"、进步意味着什么。同一套事实，换一个视角会推出完全不同的意图。

**第 4 层 · 使命与存在前提（Mission / Why-why-why…）**
"我们为什么做这个、而非别的事"的终极回答。

- 通常很短，且几乎不变。它不能证明什么，但它决定了**哪些问题值得被提出**。

## 二、全链一览

```
使命/存在前提       ← 为什么做这件事（几乎不变）
   └─ 战略/理论视角   ← 凭什么路径达成（年）
       └─ 立场/伦理/底线 ← 什么不可交换（年）
           └─ 目的/价值主张 ← 为谁创造什么价值（季度）
               └─ 意图       ← 为什么是这种形式（版本/迭代）
                   └─ 交互规格 ← 是什么（天）
```

这条链的本质是一条**合法性传递链**：上层为下层提供"值得性"和"边界"，下层为上层提供"可实现性"的反馈。任何一层断裂，整条链都会塌。

## 三、容易被漏掉的反向：约束层

意图之上还有一类东西，不是"我们想怎样"，而是"我们被允许怎样"——**不可控的外在约束**：

| 约束来源 | 内容 |
| --- | --- |
| 物理/生理 | 感官能力差异、注意力带宽、手部尺寸、屏幕与网络极限 |
| 技术与平台 | 浏览器能力、平台规范、性能与设备门槛 |
| 法律与合规 | 隐私法、可访问性法规（如 WCAG 的强制要求）、行业监管 |
| 组织 | 品牌资产、技术债、预算与工期、团队能力 |
| 生态 | 用户已有的习惯、市场惯例、竞争者的设定 |

意图必须在约束内成立。这解释了为什么"理论上最优"常常不是最终方案——**意图是被约束优化后的产物，不是无约束推导的产物**。

## 四、意图层最容易被忽略的三件事

1. **意图要能被反驳**。写不出的反证条件，说明它只是审美偏好。
2. **意图有保质期**。用户会迁移、技术会变、法规会变。每条意图必须带**复审触发条件**（"当 X 数据出现 / 当 Y 法规生效 / 当 Z 功能上线时复审"）。
3. **意图是承诺，不是灵感**。它一旦写入，就意味着"未来所有同类决策都要与之相容"，因此它比形式更难改、也更值得慎写。

## 五、一句话

**意图之上是立场与目的，再上是战略与使命——它们共同规定意图的"值得性、边界与方向"；而意图的成立还依赖另一条线：不可控的约束。**

一个方案能被完整解释，需要同时交代这两条线：**为什么要做（上链）+ 只能在什么范围内做（约束）**。只讲其中一条，都是不完整。

> 注意：这一层（立场、使命、伦理底线）通常是**组织层面的既有设定**，而非设计师可以自行推导的东西。落到具体项目时，应向产品负责人或决策层索取或共同确认，而不是凭理论代写——否则只是替别人编了一套漂亮的价值观。

要不要我把"意图层+之上四层+约束层"作为新的一章并入之前的 Word，做成一个从使命一路贯通到像素的完整规格文档？

（注：文档部分内容可能由 AI 生成）
