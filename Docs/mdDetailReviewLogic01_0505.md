# 记忆助手 - 复习算法详情

**核心规则：**

1. **正常复习**（当前时间 ≥ next_review_time）
   - 答对：current_level + 1（最高7）
   - 答错：current_level - 1（最低1）

2. **提前复习**（当前时间 < next_review_time）
   - 等级不变化
   - 只更新 last_reviewed_at，并按当前等级顺延 next_review_time

3. **严重过期复习**
   - 判断条件：(当前时间 - next_review_time) > (当前间隔 × overdue_multiplier)
   - 答错：降2级（最低不低于1级）