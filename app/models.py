from sqlalchemy import (
    Table,
    Column,
    String,
    Integer,
    ForeignKey,
    Numeric,
    BigInteger,
    Boolean,
    Text,
    REAL,
)
from typing import List, Optional
import sqlalchemy.dialects.postgresql as postgresql
import uuid
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.declarative import declarative_base
from uuid import UUID

from database import Base


class BookAuthor(Base):
    __tablename__ = "book_authors"
    book_id: Mapped[UUID] = mapped_column(ForeignKey("books.id"), primary_key=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("authors.id"), primary_key=True)


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    name: Mapped[Optional[str]] = mapped_column(String, nullable=False, unique=True)
    books: Mapped[List["Book"]] = relationship(
        "Book", secondary="book_authors", back_populates="authors"
    )


class Book(Base):
    __tablename__ = "books"
    id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    title: Mapped[Optional[str]] = Column(String(100), nullable=False, unique=True)
    authors: Mapped[List["Author"]] = relationship(
        "Author", secondary="book_authors", back_populates="books"
    )


