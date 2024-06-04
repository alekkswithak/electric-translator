from openai import OpenAI
import os

API_KEY = os.environ.get("API_KEY")
print(API_KEY)


def query_gpt(user_content: str, language: str) -> str:
    system_content = f"Translate into {language}"
    client = OpenAI(api_key=API_KEY)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": user_content,
            },
        ],
    )
    return completion.choices[0].message.content


def translate(text: str, language: str) -> str:
    """Translation wrapper."""
    return query_gpt(text, language)
