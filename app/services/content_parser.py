"""
Parse RawContent records into ProcessedContent records.

Parsing rules per content_type:
  memory        -> question=raw_text, answer=NONE, extra=null
  word          -> split on "answer:", question/answer
  single_choice -> split on "answer option:", extra has options+correct_answers+explanation
  multiple_choice -> split on "answer check:", extra has options+correct_answers+explanation
"""
import json
import re
from typing import Optional


def _extract_explanation(text: str) -> tuple[str, Optional[str]]:
    """Split off a trailing 'explain: ...' line and return (body, explanation)."""
    pattern = re.compile(r"\nexplain\s*:\s*(.+)$", re.IGNORECASE | re.DOTALL)
    m = pattern.search(text)
    if m:
        body = text[: m.start()].strip()
        explanation = m.group(1).strip()
        return body, explanation
    return text.strip(), None


def _parse_options(option_block: str) -> list[str]:
    """
    Extract lettered options from a block of text.
    Handles lines like: "A. text", "B) text", "A、text"
    """
    lines = option_block.strip().splitlines()
    options = []
    for line in lines:
        line = line.strip()
        if re.match(r"^[A-Ea-e][.\)、]\s*", line):
            options.append(line)
    return options


def parse_memory(raw_text: str) -> dict:
    return {
        "question": raw_text.strip(),
        "answer": "NONE",
        "extra": None,
        "usage_type": "daily_review",
    }


def parse_word(raw_text: str) -> dict:
    parts = re.split(r"\nanswer\s*:\s*", raw_text, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) == 2:
        question = parts[0].strip()
        answer_block, explanation = _extract_explanation(parts[1])
        answer = answer_block.strip()
    else:
        question = raw_text.strip()
        answer = "NONE"
        explanation = None

    extra = {"explanation": explanation} if explanation else None
    return {
        "question": question,
        "answer": answer,
        "extra": extra,
        "usage_type": "english_word",
    }


def parse_single_choice(raw_text: str) -> dict:
    parts = re.split(r"\nanswer option\s*:\s*", raw_text, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) != 2:
        return parse_memory(raw_text)

    question_block = parts[0].strip()
    answer_block, explanation = _extract_explanation(parts[1])
    answer_letter = answer_block.strip().upper()

    options = _parse_options(question_block)
    if options:
        # question is everything before the first option line
        first_option_match = re.search(r"^[A-Ea-e][.\)、]", question_block, re.MULTILINE)
        if first_option_match:
            question = question_block[: first_option_match.start()].strip()
            option_block = question_block[first_option_match.start():]
            options = _parse_options(option_block)
        else:
            question = question_block
    else:
        question = question_block

    extra = {
        "options": options,
        "correct_answers": [answer_letter],
        "explanation": explanation,
    }
    return {
        "question": question,
        "answer": answer_letter,
        "extra": extra,
        "usage_type": "exam_practice",
    }


def parse_multiple_choice(raw_text: str) -> dict:
    parts = re.split(r"\nanswer check\s*:\s*", raw_text, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) != 2:
        return parse_memory(raw_text)

    question_block = parts[0].strip()
    answer_block, explanation = _extract_explanation(parts[1])
    answer_letters = [a.strip().upper() for a in re.split(r"[,，\s]+", answer_block.strip()) if a.strip()]

    options = _parse_options(question_block)
    first_option_match = re.search(r"^[A-Ea-e][.\)、]", question_block, re.MULTILINE)
    if first_option_match:
        question = question_block[: first_option_match.start()].strip()
        options = _parse_options(question_block[first_option_match.start():])
    else:
        question = question_block

    extra = {
        "options": options,
        "correct_answers": answer_letters,
        "explanation": explanation,
    }
    return {
        "question": question,
        "answer": ",".join(answer_letters),
        "extra": extra,
        "usage_type": "exam_practice",
    }


PARSERS = {
    "memory": parse_memory,
    "word": parse_word,
    "single_choice": parse_single_choice,
    "multiple_choice": parse_multiple_choice,
}


def parse_raw_content(content_type: str, raw_text: str) -> dict:
    parser = PARSERS.get(content_type, parse_memory)
    return parser(raw_text)
