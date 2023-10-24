from fastapi import Depends, FastAPI, HTTPException
from typing import List
import schemas, models, crud
import uvicorn
from uuid import UUID
from sqlalchemy.orm import Session
from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/books/", response_model=schemas.BookSchemaOut, tags=["books"])
async def add_book(book: schemas.BookSchema, db: Session = Depends(get_db)):
    book = crud.insert_book(db, book)
    return book


@app.get("/api/books/{book_id}", response_model=schemas.BookSchemaOut, tags=["books"])
async def get_book(book_id: UUID, db: Session = Depends(get_db)):
    book = crud.get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    return book


@app.get("/api/books/", response_model=List[schemas.BookSchemaOut], tags=["books"])
async def get_books(limit:int = 10, db: Session = Depends(get_db)):
    return crud.get_books(db, limit)


@app.post("/api/authors/", response_model=schemas.AuthorSchemaOut, tags=["authors"])
async def add_author(author: schemas.AuthorSchema, db: Session = Depends(get_db)):
    author = crud.insert_author(db, author)
    return author


@app.get(
    "/api/authors/{author_id}", response_model=schemas.AuthorSchemaOut, tags=["authors"]
)
async def get_author(author_id: UUID, db: Session = Depends(get_db)):
    author = crud.get_author_by_id(db, author_id)
    if author is None:
        raise HTTPException(
            status_code=404, detail=f"Author with id {author_id} not found"
        )
    return author


@app.get(
    "/api/authors/", response_model=List[schemas.AuthorSchemaOut], tags=["authors"]
)
async def get_authors(limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_authors(db, limit)


@app.delete("/api/authors/{author_id}", tags=["authors"])
async def delete_author(author_id: UUID, db: Session = Depends(get_db)):
    author = crud.get_author_by_id(db, author_id)
    if author is None:
        raise HTTPException(
            status_code=404, detail=f"Author with id {author_id} not found"
        )
    crud.delete_author(db, author)
    return {"deleted": True}


@app.delete("/api/books/{book_id}", tags=["books"])
async def delete_book(book_id: UUID, db: Session = Depends(get_db)):
    book = crud.get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    crud.delete_book(db, book)
    return {"deleted": True}


@app.put("/api/books/{book_id}", response_model=schemas.BookSchemaOut, tags=["books"])
async def update_book(
    book_id: UUID, new_book: schemas.BookSchema, db: Session = Depends(get_db)
):
    db_book = crud.get_book_by_id(db, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book with id {book_id} not found")
    update_book = crud.update_book(db, book_id, new_book)
    return update_book


@app.put(
    "/api/authors/{author_id}", response_model=schemas.AuthorSchemaOut, tags=["authors"]
)
async def update_author(
    author_id: UUID, new_author: schemas.AuthorSchema, db: Session = Depends(get_db)
):
    db_author = crud.get_author_by_id(db, author_id)
    if not db_author:
        raise HTTPException(
            status_code=404, detail="Author with id {author_id} not found"
        )
    update_author = crud.update_author(db, author_id, new_author)
    return update_author


log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, log_config=log_config)
