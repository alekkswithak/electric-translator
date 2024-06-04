from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship


class OriginalText(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    translations = relationship("Translation", back_populates="text")


class Translation(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text_id = Column(Integer, ForeignKey("texts.id"), nullable=False)
    status = Column(String, nullable=False)
    language = Column(String, nullable=False)
    translated_content = Column(Text)
    text = relationship("OriginalText", back_populates="translations")
