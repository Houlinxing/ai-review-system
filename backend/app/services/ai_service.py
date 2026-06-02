from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)


def generate_summary(comments: list[str]) -> str:

    if not comments:
        return "No comments available"

    prompt = f"""
Summarize the main opinions:

{comments}

Return bullet points.
"""

    try:
        response = client.chat.completions.create(
            model="minimaxai/minimax-m2.7",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300
        )

        summary = response.choices[0].message.content

        return summary or "No summary available"

    except Exception as e:
        print("AI error:", e)
        return "Summary generation failed"