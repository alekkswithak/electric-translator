from crud import (
    get_text,
    get_translation,
    update_translation_fields,
    get_translations_for_text,
    update_text_status,
)
from translation_gateway import translate
from helpers import split_text_into_sentence_groups
import asyncio
import httpx


async def process_individual_translation(translation_id: int):
    translation = get_translation(translation_id)
    text = get_text(translation.text_id)
    chunks = split_text_into_sentence_groups(text.text)

    translated_sentences = []

    async def translate_chunk(chunk):
        return await translate(chunk, translation.language)

    tasks = [translate_chunk(chunk) for chunk in chunks]
    translated_sentences = await asyncio.gather(*tasks)

    translated_text = " ".join(translated_sentences)

    update_translation_fields(
        translation_id, status="complete", translated_content=translated_text
    )


async def process_translation(text_id: int):
    translations = get_translations_for_text(text_id)
    tasks = [process_individual_translation(t.id) for t in translations]
    await asyncio.gather(*tasks)
    update_text_status(text_id, "completed")


def process_text_background(text_id: int):
    asyncio.run(process_translation(text_id))


async def query_gpt_async(user_content: str, language: str) -> str:
    system_content = f"Translate into {language}"

    retries = 42
    wait_time = 21

    while retries > 0:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": "Bearer API_KEY"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": system_content},
                            {"role": "user", "content": user_content},
                        ],
                        "temperature": 0.7,
                    },
                    timeout=48,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                retries -= 1
                if retries == 0:
                    raise
                else:
                    print(f"Error: {e}, Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
            except httpx.ReadTimeout as e:
                retries -= 1
                if retries == 0:
                    print(f"ReadTimeout error: {e}, Maximum retries reached.")
                    break
                else:
                    print(f"ReadTimeout error: {e}, Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
