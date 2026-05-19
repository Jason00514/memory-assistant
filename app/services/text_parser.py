"""
テキストファイル（.txt）のパーサー。
Excel パーサーと同じフォーマット・同じ戻り値形式で動作する。

サポートするフォーマット：
  # Category: カテゴリ名  ← カテゴリ定義行
  ---                     ← カード区切り（"---" 行のみ）
  カード内容（複数行OK、カード内の空行は許容）
"""
import re
from app.services.excel_parser import detect_content_type


def parse_text_content(text: str) -> list[dict]:
    """
    テキスト文字列を解析して raw record のリストを返す。
    戻り値は excel_parser と同形式: [{category, content_type, raw_text}, ...]

    区切り文字は "---" のみ。カード内の空行は無視せずカード内容として扱う。
    """
    # Normalize line endings (CRLF / CR → LF) and strip BOM
    text = text.replace('\r\n', '\n').replace('\r', '\n').lstrip('﻿')

    records = []
    current_category = "未分類"
    category_pattern = re.compile(r"#\s*[Cc]ategory\s*:\s*(.+)", re.IGNORECASE)

    # Split on "---" separator lines (surrounded by optional whitespace/blank lines)
    blocks = re.split(r'\n\s*-{3,}\s*\n', text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.splitlines()
        first_line = lines[0].strip()
        m = category_pattern.match(first_line)

        if m:
            current_category = m.group(1).strip()
            # Remaining lines after the category header are the card body
            block = "\n".join(lines[1:]).strip()
            if not block:
                continue  # category-only block, no card content

        content_type = detect_content_type(block)
        records.append({
            "category": current_category,
            "content_type": content_type,
            "raw_text": block,
        })

    return records
