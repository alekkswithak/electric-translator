from database import db_context
from models import OriginalText, Translation
from schemas import (
    TextOutSchema,
    TranslationInSchema,
    TranslationOutSchema,
    TranslationRequestSchema,
)
from typing import Optional, List


def create_text(text) -> TextOutSchema:
    """
    Creates a new original text record in the database.

    This function takes a string containing the original text and creates a new
    entry in the `OriginalText` database table. The initial status of the
    text is set to "pending".

    Args:
        text (str): The original text content.

    Returns:
        TextOutSchema: A schema object representing the created original text
                       record with details like ID, text content, and status.
    """
    db_text = OriginalText(text=text, status="pending")
    with db_context() as db:
        db.add(db_text)
        db.commit()
        db.refresh(db_text)
    return TextOutSchema(**db_text.__dict__)


def get_text(text_id: int) -> Optional[OriginalText]:
    """
    Retrieves an original text record from the database by its ID.

    This function queries the `OriginalText` table based on the provided
    `text_id` and returns the corresponding record if found.

    Args:
        text_id (int): The unique identifier of the original text record.

    Returns:
        Optional[OriginalText]: The original text record object if found,
                                otherwise None.
    """
    with db_context() as db:
        text = db.query(OriginalText).filter(OriginalText.id == text_id).first()
    if text:
        return text


def update_text_status(text_id: int, new_status: str):
    """
    Updates the status of an original text record in the database.

    This function locates the original text record identified by `text_id`
    and updates its status to the provided `new_status`. It then commits
    the changes to the database.

    Args:
        text_id (int): The unique identifier of the original text record.
        new_status (str): The new status to be set for the text record.

    Returns:
        Optional[TextOutSchema]:
            - A schema object representing the updated text record if successful.
            - None if the text record with the provided ID is not found.
    """

    with db_context() as db:
        db_text = db.query(OriginalText).filter(OriginalText.id == text_id).first()
        if db_text:
            db_text.status = new_status
            db.commit()
        else:
            return None


def create_translation(translation: TranslationInSchema) -> TranslationOutSchema:
    """
    Creates a new translation record in the database.

    This function takes a `TranslationInSchema` object containing details
    about the translation and creates a new entry in the `Translation`
    database table.

    Args:
        translation (TranslationInSchema): A schema object representing the
                                            translation details.

    Returns:
        TranslationOutSchema: A schema object representing the created
                              translation record with details like ID, text ID,
                              language, status, and translated content (if available).
    """
    db_translation = Translation(**translation.dict())
    with db_context() as db:
        db.add(db_translation)
        db.commit()
        db.refresh(db_translation)
    return TranslationOutSchema(**db_translation.__dict__)


def get_translation(id: int) -> Optional[Translation]:
    """
    Retrieves a translation record from the database by its ID.

    This function queries the `Translation` table based on the provided
    `id` and returns the corresponding record if found.

    Args:
        id (int): The unique identifier of the translation record.

    Returns:
        Optional[Translation]: The translation record object if found,
                                otherwise None.
    """
    with db_context() as db:
        translation = db.query(Translation).filter(Translation.id == id).first()
    if translation:
        return translation


def get_translations_for_text(text_id: int) -> List[TranslationOutSchema]:
    """
    Retrieves all translation records associated with a specific original text.

    Args:
        text_id (int): The unique identifier of the original text.

    Returns:
        List[TranslationOutSchema]: A list of schema objects representing
                                    all translations associated with the
                                    original text identified by `text_id`.
    """

    with db_context() as db:
        translations = (
            db.query(Translation).filter(Translation.text_id == text_id).all()
        )

        translations = [TranslationOutSchema(**t.__dict__) for t in translations]
    return translations


def update_translation_fields(
    id: int, status: str, translated_content: str
) -> TranslationOutSchema:
    """
    Updates the status and translated content of a translation record.

    Args:
        id (int): The unique identifier of the translation record.
        status (str): The new status to be set for the translation.
        translated_content (str): The translated content for the record (optional).

    Returns:
        Optional[TranslationOutSchema]:
            - A schema object representing the updated translation record if successful.

    """
    with db_context() as db:
        db_translation = db.query(Translation).filter(Translation.id == id).first()
        if db_translation:
            db_translation.status = status
            db_translation.translated_content = translated_content
            db.commit()
            db.refresh(db_translation)
            return TranslationOutSchema(**db_translation.__dict__)
        else:
            return None


def create_translation_task(
    translation_request=TranslationRequestSchema,
) -> TextOutSchema:
    """
    Creates a new original text record and associated translation tasks.

    This function takes a `TranslationRequestSchema` object and performs the
    following actions:

    1. Creates a new record in the `OriginalText` table with the provided text.
    2. Iterates through the `languages` list in the schema object.
    3. For each language, creates a new record in the `Translation` table
       associated with the original text and the specific language, setting
       the initial status to "pending".

    The function finally returns a schema object representing the created
    original text record.

    Args:
        translation_request (TranslationRequestSchema): A schema object containing
                                                        the original text and
                                                        target languages.

    Returns:
        TextOutSchema: A schema object representing the created original text
                       record with details like ID, text content, and status.
    """
    text = create_text(text=translation_request.text)
    for language in translation_request.languages:
        translation = TranslationInSchema(
            text_id=text.id, language=language, status="pending"
        )
        create_translation(translation)
    return text
