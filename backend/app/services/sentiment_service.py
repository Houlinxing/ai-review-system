from openai import OpenAI
import os
import json

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)


def analyze_sentiment(text: str) -> float:

    if not text:
        return 0.0

    try:
        result = analyze_sentiments_batch([text])
        return result[0] if result else 0.0

    except Exception:
        return 0.0


def analyze_sentiments_batch(comments: list[str]):

    if not comments:
        return []

    prompt = f"""
Return JSON only:

[
  {{"sentiment": 0.1}}
]

Comments:
{json.dumps(comments, ensure_ascii=False)}
"""

    try:
        response = client.chat.completions.create(
            model="minimaxai/minimax-m2.7",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=800
        )

        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()

        result = json.loads(content)

        return [
            float(item.get("sentiment", 0))
            for item in result
        ]

    except Exception as e:
        print("Batch sentiment error:", e)
        return [0.0] * len(comments)