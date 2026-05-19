"""
Review scheduling algorithm based on 7-level spaced repetition.

Rules:
  Normal review   (now >= next_review_time):
      correct -> level + 1 (max 7)
      wrong   -> level - 1 (min 1)

  Early review    (now < next_review_time):
      level unchanged, next_review_time recalculated from now

  Severely overdue (now - next_review_time > current_interval * overdue_multiplier):
      wrong -> level - 2 (min 1)
"""
from datetime import datetime, timedelta
from typing import Optional


def _get_interval_hours(intervals: list[int], level: int) -> int:
    """intervals is a 7-element list; level is 1-based."""
    idx = max(0, min(level - 1, len(intervals) - 1))
    return intervals[idx]


def get_review_type(
    now: datetime,
    next_review_time: Optional[datetime],
    current_level: int,
    intervals: list[int],
    overdue_multiplier: int,
) -> str:
    if next_review_time is None:
        return "normal"
    if now < next_review_time:
        return "early"
    elapsed_hours = (now - next_review_time).total_seconds() / 3600
    current_interval = _get_interval_hours(intervals, current_level)
    if elapsed_hours > current_interval * overdue_multiplier:
        return "severely_overdue"
    return "normal"


def calculate_new_level(
    review_type: str,
    current_level: int,
    is_correct: bool,
) -> int:
    if review_type == "early":
        return current_level

    if review_type == "severely_overdue" and not is_correct:
        return max(1, current_level - 2)

    if is_correct:
        return min(7, current_level + 1)
    return max(1, current_level - 1)


def calculate_next_review_time(
    now: datetime,
    new_level: int,
    intervals: list[int],
) -> datetime:
    hours = _get_interval_hours(intervals, new_level)
    return now + timedelta(hours=hours)


def process_review(
    now: datetime,
    next_review_time: Optional[datetime],
    current_level: int,
    is_correct: bool,
    intervals: list[int],
    overdue_multiplier: int,
) -> dict:
    review_type = get_review_type(now, next_review_time, current_level, intervals, overdue_multiplier)
    new_level = calculate_new_level(review_type, current_level, is_correct)
    new_next_review = calculate_next_review_time(now, new_level, intervals)

    return {
        "review_type": review_type,
        "old_level": current_level,
        "new_level": new_level,
        "last_reviewed_at": now,
        "next_review_time": new_next_review,
    }
