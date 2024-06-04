from fastapi import FastAPI

from database import engine
from models import Base
from schemas import TranslationRequestSchema, TextTranslationsSchema
from crud import create_translation_task, get_text, get_translations_for_text

from tasks import process_translation
from typing import Union

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.post("/translate")
def translate(languages: list[str], text: str):
    """
    Initiates a translation task for the provided text in the specified languages.

    Args:
        languages (list[str]): A list of target languages for the translation.
        text (str): The text to be translated.
        background_tasks (BackgroundTasks): Background task management object
                                             injected by FastAPI.

    Returns:
        dict: A dictionary containing the key "task_id" with the ID of the
              created translation task.
    """
    text = create_translation_task(
        TranslationRequestSchema(text=text, languages=languages)
    )
    process_translation.delay(text.id)

    return {"task_id": text.id}


@app.get("/translate/{task_id}", response_model=Union[TextTranslationsSchema, dict])
def get_translate(task_id: str):
    """
    Retrieves the status and results of a translation task identified by its ID.

    Args:
        task_id (str): The unique identifier of the translation task.

    Returns:
        Union[TextTranslationsSchema, dict]:
            - If the task is ongoing, a dictionary with a key "status" set to
              "in progress".
            - If the task is complete, a `TextTranslationsSchema` object
              containing the task ID, original text, and translated content.
    """
    task = get_text(task_id)

    if task.status == "pending":
        return {"status": "in progress"}
    else:
        translations = get_translations_for_text(task_id)
    return TextTranslationsSchema(id=task.id, text=task.text, translations=translations)
