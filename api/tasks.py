from celery import Celery, group, chord
from crud import (
    get_text,
    get_translation,
    update_translation_fields,
    get_translations_for_text,
    update_text_status,
)
from translation_gateway import translate
from helpers import split_text_into_sentence_groups
import concurrent.futures
from typing import List, Any

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="sqla+postgresql://user:password@database:5432/translations",
)


@celery_app.task(bind=True)
def process_translation(self, text_id: int) -> None:
    """
    Celery task to process translations for a given text.

    This task fetches all translations for the specified text and initiates
    individual translation processing tasks for each. It then schedules a final
    task to update the status of the text once all translations are processed.

    Args:
        self: The Celery task instance (passed automatically by Celery).
        text_id (int): The ID of the text to be translated.

    Returns:
        None
    """
    translations = get_translations_for_text(text_id)
    tasks = [process_individual_translation.s(t.id) for t in translations]
    final_task = update_task_status.s(text_id=text_id)
    chord(group(tasks), final_task).delay()


@celery_app.task(bind=True)
def process_individual_translation(self, translation_id: int) -> None:
    """
    Celery task to process an individual translation.

    This task retrieves the translation and corresponding text, splits the text
    into chunks, and translates each chunk concurrently. It then updates the
    translation record with the completed translated text.

    Args:
        self: The Celery task instance (passed automatically by Celery).
        translation_id (int): The ID of the translation to be processed.

    Returns:
        None
    """
    translation = get_translation(translation_id)
    text = get_text(translation.text_id)
    chunks = split_text_into_sentence_groups(text.text)

    translated_sentences: List[str] = []

    def translate_chunk(chunk: str) -> str:
        return translate(chunk, translation.language)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        translated_sentences = list(executor.map(translate_chunk, chunks))

    translated_text = " ".join(translated_sentences)

    update_translation_fields(
        translation_id, status="complete", translated_content=translated_text
    )


@celery_app.task(bind=True)
def update_task_status(self, *args: Any, **kwargs: Any) -> None:
    """
    Celery task to update the status of a text.

    This task updates the status of a text to "completed" after all translations
    have been processed.

    Args:
        self: The Celery task instance (passed automatically by Celery).
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments. Expected to contain 'text_id'.

    Returns:
        None
    """
    update_text_status(kwargs.get("text_id"), "completed")
