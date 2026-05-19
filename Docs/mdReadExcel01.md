记忆助手 - 项目确认文档（2026.5.5 最新版）
1. 项目定位
一个基于7级遗忘曲线的通用记忆管理系统，支持多分类管理。
2. Excel 单列录入格式（已确认）
使用单列格式，以 # Category: xxx 定义分类，用 answer: 标记答案。
3. 数据库表结构
3.1 RawContent 表（原始数据表）
表作用： 粗暴存储从 Excel 读取的每个 Cell 的完整原始内容，不做任何解析处理。
字段详细说明：

RC_ID：主键，格式 RC_0000123
category：分类名称，用于区分不同主题的内容。例如“英语核心词汇”“计算机网络”“资格考试”等，主要用于之后按主题筛选和复习。
content_type：内容类型，由程序自动识别（memory / word / single_choice / multiple_choice），用于区分纯记忆内容、单词、单选题、多选题。
raw_text：完整保存 Excel Cell 中的全部原始文本。
source：数据来源，固定为 excel_cell
process_status：处理状态（unprocessed、processing、processed、failed）
data_flag：数据标志（0=正常使用，1=已删除，2=测试数据）
imported_at：导入时间

3.2 ProcessedContent 表（加工数据表）
表作用： 对原始数据进行解析处理后，生成可用于记忆复习的结构化记录。
字段详细说明：

PC_ID：主键，格式 PC_0000456
RC_ID：关联 RawContent 表的 ID
content_type：内容类型（word / memory / choice 等）
question：问题或正面显示内容
answer：答案内容（无答案填 NONE）
extra：额外信息（JSON格式，存选项、解释等）
category：最终分类名称
process_purpose：处理目的（说明这条记录是用来干什么的）
process_version：第几次处理
data_flag：数据标志（0=正常，1=已删除，2=测试数据）
processed_at：处理时间


------------------------------
Excel 导入最终规则（已确认）
程序按以下顺序处理每个 Cell：

读取整个 Cell 的完整内容，存入 raw_text
自动识别 content_type（新增字段），识别规则如下：
如果内容中不包含 answer: → content_type = memory
如果内容中只包含 answer: → content_type = word
如果内容中包含 answer option: → content_type = single_choice
如果内容中包含 answer check: → content_type = multiple_choice

category：从 # Category:  中提取（如果当前 Cell 没有，则继承上一个 Cell 的 category）


