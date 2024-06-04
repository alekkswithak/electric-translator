from pydantic import BaseModel
from typing import List, Optional


class TranslationRequestSchema(BaseModel):
    text: str
    languages: List[str]


class TextInSchema(BaseModel):
    text: str
    status: str


class TextOutSchema(BaseModel):
    id: int
    text: str
    status: str


class TranslationInSchema(BaseModel):
    text_id: int
    language: str
    status: str


class TranslationOutSchema(BaseModel):
    id: int
    text_id: int
    language: str
    status: str
    translated_content: Optional[str]


class TextTranslationsSchema(BaseModel):
    id: int
    text: str
    translations: List[TranslationOutSchema]
