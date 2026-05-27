from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)


def analyze_sentiment(text: str) -> float:
    response = client.chat.completions.create(
        model="minimaxai/minimax-m2.7",
        messages=[
            {
                "role": "system",
                "content": "你是情绪分析AI，只返回-1到1之间的小数。"
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    result = response.choices[0].message.content

    return float(result)