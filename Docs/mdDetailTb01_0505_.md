# 记忆助手 - 表结构详情

### 1. RawContent 表（原始数据表）
- RC_ID：格式 RC_0000123
- category：分类名称
- content_type：memory / word / single_choice / multiple_choice（自动识别）
- raw_text：Excel Cell 的完整原始内容
- source：excel_cell
- process_status：unprocessed / processing / processed / failed
- data_flag：0=正常, 1=已删除, 2=测试
- imported_at：导入时间

### 2. ProcessedContent 表
- PC_ID：格式 PC_0000456
- RC_ID：关联 RawContent
- content_type
- question
- answer（无答案填 NONE）
- extra：JSON（存放选项、正确答案、解释）
- category
- usage_type：english_word / chinese_word / exam_practice / daily_review
- curve_id
- current_level：1~7
- last_reviewed_at：上次复习时间
- next_review_time：下次复习时间
- data_flag
- processed_at

### 3. MemoryCurve 表
- curve_id：格式 MC_000001
- curve_name
- intervals：JSON数组（7个间隔，单位小时）
- overdue_multiplier：默认10
- created_at