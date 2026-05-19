# 记忆助手 - 解析逻辑详情

**RawContent → ProcessedContent 解析规则**

### 1. memory 类型
- question = 整个 raw_text 内容
- answer = "NONE"
- extra = null

### 2. word 类型
- question = "answer:" 之前的内容
- answer = "answer:" 之后的内容
- extra = null

### 3. single_choice 类型（单选题）
- question = "answer option:" 之前的内容
- answer = "answer option:" 后面的正确答案字母（如 "C"）
- extra 中保存 options 和 correct_answers

### 4. multiple_choice 类型（多选题）
- question = "answer check:" 之前的内容
- answer = "answer check:" 后面的正确答案字母（如 "B,D"）
- extra 中保存 options 和 correct_answers