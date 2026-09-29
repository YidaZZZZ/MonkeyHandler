"""动机设计层：让训练本身有吸引力，且服务于用户的长期利益。

「痴迷」的来源不是打卡焦虑，而是几条被反复验证的机制（均可在
humanity/ 著作库中追溯到出处）：
- 心流通道：难度压在「踮脚够得着」的区间，目标成功率约 85%；
- 即时可见的进度：每次训练都留下可感知的痕迹；
- 变量奖励：不定期、不可完全预测的里程碑比固定奖励更有效；
- 身份叙事：把「坚持」转译成「我是一个不缺席的人」。

伦理底线：动机设计服务于用户的长期利益（可持续、防倦怠）；
不制造焦虑、不用负反馈惩罚用户。减量与休息同样是被设计的正反馈。
"""
from __future__ import annotations

TARGET_SUCCESS_RATE = 0.85  # 心流通道目标成功率（u_flow_challenge）


def adjust_difficulty(recent_success_rate: float, current: float, step: float = 0.05) -> float:
    """依据最近成功率把难度拉回流通道（M3 在再校准中调用）。"""
    if recent_success_rate > 0.9:
        return min(1.0, current + step)
    if recent_success_rate < 0.7:
        return max(0.0, current - step)
    return current


def milestone(streak_days: int) -> str | None:
    """变量奖励：不在每个整数天数都给奖励，保持新鲜感（M3 接入执行闭环）。"""
    if streak_days in (3, 7, 14, 30, 60, 100):
        return f"连续 {streak_days} 天——解锁一个新里程碑"
    return None
