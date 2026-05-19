我现在给你带字段说明的完整版，方便你复制保存：

RawContent 表（原始数据表）

RC_ID：主键，格式 RC_0000123
category：分类名称
content_type：内容类型（自动识别：memory/word/single_choice/multiple_choice）
raw_text：Excel中一个单元格的完整原始内容
source：数据来源（excel_cell）
process_status：处理状态（unprocessed/processed/failed）
data_flag：数据标记（0=正常）
imported_at：导入时间

ProcessedContent 表（加工数据表）

PC_ID：主键，格式 PC_0000456
RC_ID：关联 RawContent 的 ID
content_type：内容类型
question：问题或正面显示的内容
answer：答案（无答案填 NONE）
extra：额外信息（JSON格式，存选项、解释等）
category：分类
usage_type：用途类型（english_word / exam_practice 等）
curve_id：使用哪套记忆曲线
current_level：当前记忆等级（1-7）
last_reviewed_at：上次复习时间
next_review_time：下次复习时间
process_version：处理版本号
data_flag：数据标记
processed_at：处理时间

MemoryCurve 表（记忆曲线表）

curve_id：主键，格式 MC_000001
curve_name：曲线名称（如标准单词曲线）
description：描述
intervals：7个间隔时间（JSON数组，单位小时）
overdue_multiplier：严重过期倍数（默认10）
created_at：创建时间
data_flag：数据标记