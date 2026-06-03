# app/utils/text_cleaner.py

import re
from html import unescape


def clean_text(text: str) -> str:

    if not text:
        return ""

    # HTML实体解码
    text = unescape(text)

    # 删除标签
    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    # 删除URL
    text = re.sub(
        r"http\S+",
        "",
        text
    )

    # 删除多余空白
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = re.sub(
    r"#\S+",
    "",
    text
    )

    return text.strip()