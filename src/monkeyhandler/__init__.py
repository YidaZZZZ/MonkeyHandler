"""MonkeyHandler —— AI 驱动的个体化学习/训练工作台框架。

三大能力 + 一个闭环：
- 识人（humanity / profiling / user_model）：人类通识知识库（共性 + 个体差异
  维度，源自 humanity/ 著作库的审核产物）与采集方法论，产出带证据的个体画像；
- 识域（research / domain）：领域可插拔（DomainPack），带引用的领域调研；
- 成案（plan / motivation）：可解释、可持续、有动机设计的训练计划；
- 执行闭环（M3+）：check-in、依从性追踪、再校准。

详见 docs/architecture.md、docs/roadmap.md 与 humanity/README.md。
"""

__version__ = "0.0.1"

from .core.domain import DomainPack
from .core.humanity import HumanKnowledgeBase, KnowledgeEntry
from .core.plan import Load, Phase, Plan, Session
from .core.profiling import Question, Questionnaire
from .core.research import DomainProfile, NullResearchEngine, ResearchEngine
from .core.user_model import Dimension, Evidence, EvidenceSource, UserModel

__all__ = [
    "Dimension",
    "DomainPack",
    "DomainProfile",
    "Evidence",
    "EvidenceSource",
    "HumanKnowledgeBase",
    "KnowledgeEntry",
    "Load",
    "NullResearchEngine",
    "Phase",
    "Plan",
    "Question",
    "Questionnaire",
    "ResearchEngine",
    "Session",
    "UserModel",
    "__version__",
]
