记忆助手 - 完整技术确认文档（2026.5.5 最终版）
1. 项目定位
基于7级遗忘曲线的通用记忆管理系统，支持多套记忆曲线和多分类管理。
2. 数据库表结构
2.1 RawContent 表（原始数据表）
作用： 完整保存 Excel 中每个 Cell 的原始内容。
字段：

RC_ID（主件）
category（分类）
content_type（memory / word / single_choice / multiple_choice）
raw_text（完整原始文本）
source（excel_cell）
process_status
data_flag
imported_at

2.2 ProcessedContent 表（加工数据表）
作用： 解析后用于实际复习的结构化记录。
字段：

PC_ID（主件）
RC_ID（关联原始表）
content_type
question
answer
extra（JSON）
category
usage_type
curve_id
current_level（1-7）
last_reviewed_at
next_review_time
data_flag
processed_at

2.3 MemoryCurve 表（记忆曲线表）
作用： 管理系统中多套不同的遗忘曲线。
字段：

curve_id（主件）
curve_name
description
intervals（JSON数组，单位：小时）
created_at
data_flag

默认曲线：

标准单词曲线
高频强化曲线
文章记忆曲线
日语单词曲线