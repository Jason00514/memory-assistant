记忆助手 - 数据库表结构（2026.5.5 版）
1. RawContent 表（原始数据表）
表作用： 用于完整保存从 Excel 读取的每个 Cell 的原始内容，不做任何拆分处理。
字段说明：

RC_ID：字符串(10)，主键，格式为 RC_0000123（前两位 RC_ + 7位数字）
category：字符串(50)，分类名称（如：英语核心词汇）
raw_text：长文本，完整保存 Excel 中一个 Cell 的原始内容
source：字符串(20)，数据来源（excel_cell 或 manual）
keyword_front：字符串(100)，正面关键词（如单词）
keyword_back：字符串(100)，答案关键词（无答案时填 NONE）
process_status：字符串(20)，处理状态（unprocessed、processing、processed、failed）
data_flag：整数(1)，数据标志（0=正常使用，1=已删除，2=测试数据）
imported_at：日期时间，数据导入时间


2. ProcessedContent 表（加工数据表）
表作用： 对原始数据进行解析处理后，生成结构化可用于复习的数据。
字段说明：

PC_ID：字符串(10)，主键，格式为 PC_0000456
RC_ID：字符串(10)，外键，关联 RawContent 表的 RC_ID
content_type：字符串(20)，内容类型（word、memory、choice）
question：长文本，问题/正面显示内容
answer：长文本，答案内容（无答案时填 NONE）
extra：长文本（JSON格式），额外信息（如选项、解释、例句等）
category：字符串(50)，最终使用的分类
process_purpose：字符串(30)，处理目的（如 english_word、exam_practice、daily_review）
process_version：整数，第几次被处理
data_flag：整数(1)，数据标志（0=正常，1=已删除，2=测试数据）
processed_at：日期时间，处理完成时间