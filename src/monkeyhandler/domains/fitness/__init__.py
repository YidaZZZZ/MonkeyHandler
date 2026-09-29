"""健身领域包：第一个内置领域，也是 DomainPack 的参考实现。"""

from .pack import FitnessPack
from .research import FitnessOfflineResearch

__all__ = ["FitnessOfflineResearch", "FitnessPack"]
