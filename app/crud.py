import time
import traceback
from models import Author, Book
from sqlalchemy import create_engine, select, orm
import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy.orm import Session
import schemas

RETRY_TIMES = 1


def insert_author( db: Session, author: schemas.AuthorSchema):
    db_author = Author(**author.model_dump())
    db.add(db_author)
    db.commit()
    print(db_author)
    return db_author


def insert_book( db: Session, book: schemas.BookSchema):
    book_dict = book.model_dump()
    author_names = book_dict.pop("authors")
    db_book = Book(**book_dict)
    db.add(db_book)
    db.commit()
    db.refresh(db_book, ["authors"])

    for author_name in author_names:
        query = select(Author).where(Author.name == author_name)
        db_author = (db.execute(query)).scalar_one_or_none()
        if db_author is None:
            db_author = Author(name=author_name)
            db.add(db_author)

        db_book.authors.append(db_author)

    db.commit()
    return db_book


def get_book_by_id( db: Session, book_id):
    query = (
        select(Book).where(Book.id == book_id).options(orm.selectinload(Book.authors))
    )
    book = db.execute(query)
    return book.scalar_one_or_none()


def get_books( db: Session, limit: int):
    query = (
        select(Book).options(orm.selectinload(Book.authors)).limit(limit)
    )
    items = db.execute(query)
    return items.scalars().all()


def get_author_by_id(db: Session, author_id):
    query = (
        select(Author)
        .where(Author.id == author_id)
        .options(orm.selectinload(Author.books))
    )
    book = db.execute(query)
    return book.scalar_one_or_none()


def get_authors(db: Session, limit: int):
    query = (
        select(Author)
        .options(orm.selectinload(Author.books))
        .limit(limit)
    )
    authors = db.execute(query)
    return authors.scalars().all()


def delete_author(db: Session, author):
    books_q = select(Book).join(Book.authors).where(Author.id == author.id)
    books = db.execute(books_q).scalars().all()

    author_q = select(Author).where(Author.id == author.id)
    author = db.execute(author_q).scalar_one()

    for book in books:
        book.authors.remove(author)
        db.add(author)
        db.commit()
    db.delete(author)
    db.commit()


def delete_book( db: Session, book):
    author_q = select(Author).join(Author.books).where(Book.id == book.id)
    authors = db.execute(author_q).scalars().all()

    book_q = select(Book).where(Book.id == book.id)
    book = db.execute(book_q).scalar_one()

    for author in authors:
        author.books.remove(book)
        db.add(book)
        db.commit()
    db.delete(book)
    db.commit()


def update_book(db: Session, book_id, new_book):
    book_dict = new_book.model_dump()
    author_names = book_dict.pop("authors")
    query = (
        select(Book).where(Book.id == book_id).options(orm.selectinload(Book.authors))
    )
    db_book = db.execute(query).scalar_one_or_none()
    db_book.title = book_dict["title"]
    for author in db_book.authors:
        if author.name not in author_names:
            db_book.authors.remove(author)
            db.add(author)
            db.commit()
    for author_name in author_names:
        query = select(Author).where(Author.name == author_name)
        db_author = (db.execute(query)).scalar_one_or_none()
        if db_author is None:
            db_author = Author(name=author_name)
            db.add(db_author)
        if author_name not in [x.name for x in db_book.authors]:
            db_book.authors.append(db_author)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_author( db: Session, authors_id, new_author):
    author_dict = new_author.model_dump()
    query = (
        select(Author)
        .where(Author.id == authors_id)
        .options(orm.selectinload(Author.books))
    )
    db_author = db.execute(query).scalar_one_or_none()
    db_author.name = author_dict["name"]
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author
