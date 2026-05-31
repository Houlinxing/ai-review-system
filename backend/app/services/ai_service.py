from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)

def generate_summary(comments: list[str]):

    all_comments = "\n".join(comments)

    prompt = f"""
    Summarize the main opinions from these comments:

    {all_comments}

    Give short bullet points.
    """

    completion = client.chat.completions.create(
        model="minimaxai/minimax-m2.7",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5,
        max_tokens=300
    )

    return completion.choices[0].message.content