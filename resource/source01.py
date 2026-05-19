from datetime import datetime, timedelta
from typing import Dict

class ReviewScheduler:
    # 7级记忆曲线的时间间隔（小时）
    INTERVALS = [0, 1, 4, 24, 48, 168, 360, 720]  # 第0级不用

    def calculate_next_review(self, level: int, last_review: datetime) -> datetime:
        """根据当前等级和上次复习时间，计算下次复习时间"""
        if level < 1 or level > 7:
            level = 1
        hours = self.INTERVALS return last_review + timedelta(hours=hours)

    def get_time_status(self, next_review: datetime) -> Dict:
        """计算距离下次复习还有多久（正数=还有多久，负数=已过期多久）"""
        now = datetime.now()
        delta = next_review - now
        hours = delta.total_seconds() / 3600
        
        return {
            "hours_left": round(hours, 1),
            "is_overdue": hours < 0,
            "status": "overdue" if hours < 0 else "pending"
        }