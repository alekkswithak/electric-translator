import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database import Base, db_context
from api.crud import (
    create_text,
    get_text,
    update_text_status,
    create_translation,
    get_translation,
    get_translations_for_text,
    update_translation_fields,
    create_translation_task,
)
from schemas import TranslationInSchema, TranslationRequestSchema
from models import OriginalText, Translation
from test_config import TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    """
    Creates and drops the database schema for the tests.

    Yields:
        None
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db) -> Session:
    """
    Creates a new database session for a test.

    Args:
        test_db (None): Fixture for creating and dropping the test database schema.

    Yields:
        Session: A SQLAlchemy session object.
    """
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function", autouse=True)
def override_db_context(db_session: Session) -> Session:
    """
    Overrides the db_context function to use the testing session.

    Args:
        db_session (Session): The SQLAlchemy session object for the test.

    Yields:
        Session: The SQLAlchemy session object.
    """

    def _db_context():
        yield db_session

    db_context._get_current_object = _db_context
    return db_session


@pytest.fixture
def sample_text() -> str:
    """
    Provides a sample text for testing.

    Returns:
        str: A sample text string.
    """
    return "This is a sample text."


@pytest.fixture
def sample_translation_in_schema() -> TranslationInSchema:
    """
    Provides a sample TranslationInSchema object for testing.

    Returns:
        TranslationInSchema: A sample TranslationInSchema object.
    """
    return TranslationInSchema(
        text_id=1,
        language="es",
        status="pending",
        translated_content="Este es un texto de muestra.",
    )


@pytest.fixture
def sample_translation_request_schema() -> TranslationRequestSchema:
    """
    Provides a sample TranslationRequestSchema object for testing.

    Returns:
        TranslationRequestSchema: A sample TranslationRequestSchema object.
    """
    return TranslationRequestSchema(
        text="This is a sample text.", languages=["es", "fr"]
    )


def test_create_text(sample_text: str, db_session: Session):
    """
    Tests the create_text function.

    Args:
        sample_text (str): A sample text string.
        db_session (Session): The SQLAlchemy session object for the test.
    """
    text_out_schema = create_text(sample_text)
    assert text_out_schema.text == sample_text
    assert text_out_schema.status == "pending"


def test_get_text(db_session: Session):
    """
    Tests the get_text function.

    Args:
        db_session (Session): The SQLAlchemy session object for the test.
    """
    original_text = OriginalText(text="Sample text", status="pending")
    db_session.add(original_text)
    db_session.commit()
    result = get_text(original_text.id)
    assert result.id == original_text.id
    assert result.text == original_text.text
    assert result.status == original_text.status


def test_update_text_status(db_session: Session):
    """
    Tests the update_text_status function.

    Args:
        db_session (Session): The SQLAlchemy session object for the test.
    """
    original_text = OriginalText(text="Sample text", status="pending")
    db_session.add(original_text)
    db_session.commit()
    update_text_status(original_text.id, "completed")
    db_session.refresh(original_text)
    assert original_text.status == "completed"


def test_create_translation(
    sample_translation_in_schema: TranslationInSchema, db_session: Session
):
    """
    Tests the create_translation function.

    Args:
        sample_translation_in_schema (TranslationInSchema): A sample TranslationInSchema object.
        db_session (Session): The SQLAlchemy session object for the test.
    """
    original_text = OriginalText(text="Sample text", status="pending")
    db_session.add(original_text)
    db_session.commit()
    sample_translation_in_schema.text_id = original_text.id
    translation_out_schema = create_translation(sample_translation_in_schema)
    assert translation_out_schema.text_id == sample_translation_in_schema.text_id
    assert translation_out_schema.language == sample_translation_in_schema.language
    assert translation_out_schema.status == sample_translation_in_schema.status


def test_get_translation(db_session: Session):
    """
    Tests the get_translation function.

    Args:
        db_session (Session): The SQLAlchemy session object for the test.
    """
    translation = Translation(
        text_id=1,
        language="es",
        status="pending",
        translated_content="Este es un texto de muestra.",
    )
    db_session.add(translation)
    db_session.commit()
    result = get_translation(translation.id)
    assert result.id == translation.id
    assert result.text_id == translation.text_id
    assert result.language == translation.language
    assert result.status == translation.status
    assert result.translated_content == translation.translated_content


def test_get_translations_for_text(db_session: Session):
    """
    Tests the get_translations_for_text function.

    Args:
        db_session (Session): The SQLAlchemy session object for the test.
    """
    original_text = OriginalText(text="Sample text", status="pending")
    db_session.add(original_text)
    db_session.commit()
    translation1 = Translation(
        text_id=original_text.id,
        language="es",
        status="completed",
        translated_content="Este es un texto de muestra.",
    )
    translation2 = Translation(
        text_id=original_text.id,
        language="fr",
        status="completed",
        translated_content="Ceci est un texte d'exemple.",
    )
    db_session.add_all([translation1, translation2])
    db_session.commit()
    result = get_translations_for_text(original_text.id)
    assert len(result) == 2
    assert result[0].language == "es"
    assert result[1].language == "fr"


def test_update_translation_fields(db_session: Session):
    """
    Tests the update_translation_fields function.

    Args:
        db_session (Session): The SQLAlchemy session object for the test.
    """
    translation = Translation(
        text_id=1, language="es", status="pending", translated_content=""
    )
    db_session.add(translation)
    db_session.commit()
    result = update_translation_fields(
        translation.id, "completed", "Este es un texto de muestra."
    )
    assert result.status == "completed"
    assert result.translated_content == "Este es un texto de muestra."


def test_create_translation_task(
    sample_translation_request_schema: TranslationRequestSchema, db_session: Session
):
    """
    Tests the create_translation_task function.

    Args:
        sample_translation_request_schema (TranslationRequestSchema): A sample TranslationRequestSchema object.
        db_session (Session): The SQLAlchemy session object for the test.
    """
    result = create_translation_task(sample_translation_request_schema)
    assert result.text == sample_translation_request_schema.text
    assert result.status == "pending"
    translations = (
        db_session.query(Translation).filter(Translation.text_id == result.id).all()
    )
    assert len(translations) == len(sample_translation_request_schema.languages)
    assert translations[0].language in sample_translation_request_schema.languages
    assert translations[1].language in sample_translation_request_schema.languages
