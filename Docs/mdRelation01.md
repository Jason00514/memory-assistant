RawContent → ProcessedContent 解析逻辑（详细版）
1. memory 类型（纯记忆内容）

question：直接等于整个 raw_text 的内容
answer：固定填写 "NONE"
extra：null（或空JSON）
usage_type：默认填写 "daily_review"

2. word 类型（普通答案类型）

question：answer: 之前的全部内容（去掉末尾空行）
answer：answer: 之后的内容
extra：null
usage_type：默认填写 "english_word"（可后续修改为 chinese_word）

3. single_choice 类型（单选题）

question：answer option: 之前的全部内容
answer：answer option: 后面的正确答案字母（例如 C）
extra：JSON格式，结构如下：JSON{
  "options": ["A. 选项内容", "B. 选项内容", "C. 选项内容", "D. 选项内容"],
  "correct_answers": ,
  "explanation": "解释说明文字（如果有）"
}

4. multiple_choice 类型（多选题）

question：answer check: 之前的全部内容
answer：answer check: 后面的所有正确答案字母（例如 B,D）
extra：JSON格式，结构如下：JSON{
  "options": ["A. xxx", "B. xxx", "C. xxx", "D. xxx", "E. xxx"],
  "correct_answers": ,
  "explanation": "解释说明文字"
}

---------------------------------------------------

