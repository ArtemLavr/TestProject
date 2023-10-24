from typing import List
from pydantic import BaseModel
from uuid import UUID


class AuthorBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    title: str

    class Config:
        orm_mode = True


class BookMinimal(BookBase):
    id: UUID


class BookSchema(BookBase):
    authors: List[str]


class AuthorSchema(AuthorBase):
    pass


class AuthorMinimal(AuthorBase):
    id: UUID


class BookSchemaOut(BookBase):
    id: UUID
    authors: List[AuthorMinimal]


class AuthorSchemaOut(AuthorBase):
    id: UUID
    books: List[BookMinimal]
