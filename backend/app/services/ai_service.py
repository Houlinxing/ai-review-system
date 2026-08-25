from openai import OpenAI
from dotenv import load_dotenv
from app.core.logger import setup_logger
import os
import json

load_dotenv()

logger = setup_logger(__name__)

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)


def generate_summary(comments: list[str], topic: str = "") -> dict:
    """
    输入：评论列表 + 主题关键词
    输出：结构化 JSON dict
    """
    if not comments:
        return _empty_summary()

    # 直接用传入顺序（routes.py 已按 like_count 排序），不再随机打乱
    sampled = comments[:30]

    comments_text = "\n".join(
        f"{i+1}. {c}" for i, c in enumerate(sampled)
    )

    prompt = f"""你是一个专业的舆情分析师。以下是用户在社交媒体上关于「{topic}」的真实评论：

---
{comments_text}
---

请严格基于以上评论内容进行分析，不要引入评论中未提及的信息。

请用以下 JSON 格式输出分析结果（直接输出 JSON，不要加任何解释或 markdown 代码块）：

{{
  "verdict": "推荐 / 不推荐 / 中立",
  "verdict_reason": "一句话说明推荐理由",
  "pros": ["优点1", "优点2", "优点3"],
  "cons": ["缺点1", "缺点2"],
  "tips": ["实用建议1", "实用建议2"],
  "summary": "两到三句话的综合总结"
}}

要求：
- verdict 只能是「推荐」「不推荐」「中立」三选一
- pros/cons/tips 每项 2~4 条，每条控制在 20 字以内
- summary 控制在 80 字以内
- 所有内容必须来自评论，不要编造
- 输出语言与评论主要语言一致（中文评论输出中文，英文评论输出英文）"""

    try:
        response = client.chat.completions.create(
            model="minimaxai/minimax-m3",
            messages=[
                {
                    "role": "system",
                    "content": "你是专业的舆情分析师，只输出 JSON 格式的分析结果，不输出任何其他内容。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )

        content = response.choices[0].message.content or ""
        content = content.strip()

        # 清理可能的 markdown 代码块
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        result = json.loads(content)
        logger.info(f"summary generated: topic={topic} verdict={result.get('verdict')}")

        return {
            "verdict":        result.get("verdict", "中立"),
            "verdict_reason": result.get("verdict_reason", ""),
            "pros":           result.get("pros", []),
            "cons":           result.get("cons", []),
            "tips":           result.get("tips", []),
            "summary":        result.get("summary", ""),
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败: {e}\n原始内容: {content}", exc_info=True)
        return {
            "verdict":        "中立",
            "verdict_reason": "",
            "pros":           [],
            "cons":           [],
            "tips":           [],
            "summary":        content,
        }

    except Exception as e:
        logger.error(f"AI summary error: {e}", exc_info=True)
        return _empty_summary()


def _empty_summary() -> dict:
    return {
        "verdict":        "中立",
        "verdict_reason": "暂无足够评论数据",
        "pros":           [],
        "cons":           [],
        "tips":           [],
        "summary":        "No comments available",
    }