from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from  database import Base
from  api import app, get_db


SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:password@postgres/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_add_book():
    response_1 = client.post(
        "/api/books/", json={"title": "Book1_name", "authors": ["Author1_name"]}
    )
    assert response_1.status_code == 200
    data_1 = response_1.json()
    assert data_1['title'] == "Book1_name"
    assert data_1["authors"][0]["name"] == "Author1_name"
    book_id = data_1["id"]
    response_2 = client.get(f"/api/books/{book_id}")
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2['title'] == "Book1_name"
    assert data_2["authors"][0]["name"] ==  "Author1_name"


def test_get_books():
    response_1 = client.post(
        "/api/books/", json={"title": "Book2_name", "authors": ["Author2_name"]}
    )
    assert response_1.status_code == 200
    response_2 = client.get(
        "/api/books/"
    )
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2[0]["title"] == "Book1_name"
    assert data_2[1]["title"] == "Book2_name"


def test_change_book():
    response_1 = client.get(
        "/api/books/"
    )
    data_1 = response_1.json()
    book_id = data_1[0]["id"]
    new_title = "new_title"
    new_authors = "New_author"
    client.put(
        f"/api/books/{book_id}", json={"title": new_title, "authors": [new_authors]}
               )
    response_2 = client.get(f"/api/books/{book_id}")
    data_2 = response_2.json()
    print(data_2)
    assert data_2["title"] == new_title
    assert data_2["authors"][0]["name"] == new_authors


def test_delet_book():
    response_1 = client.get(
        "/api/books/"
    )
    data_1 = response_1.json()
    ids = [x["id"] for x in data_1]
    for book_id in ids:
        response = client.delete(f"/api/books/{book_id}")
        assert response.status_code == 200
        assert response.json() == {'deleted': True}


def test_delet_author():
    response_1 = client.get(
        "/api/authors/"
    )
    data_1 = response_1.json()
    ids = [x["id"] for x in data_1]
    for author_id in ids:
        response = client.delete(f"/api/authors/{author_id}")
        assert response.status_code == 200
        assert response.json() == {'deleted': True}


def test_add_author():
    response_1 = client.post(
        "/api/authors/", json={"name": "Author3_name"}
    )
    assert response_1.status_code == 200
    data_1 = response_1.json()
    assert data_1['name'] == "Author3_name"
    author_id = data_1["id"]
    response_2 = client.get(f"/api/authors/{author_id}")
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2['name'] == "Author3_name"


def test_get_authors():
    response_1 = client.post(
        "/api/authors/", json={"name": "Author4_name"}
    )
    assert response_1.status_code == 200
    response_2 = client.get(
        "/api/authors/"
    )
    assert response_2.status_code == 200
    data_2 = response_2.json()
    assert data_2[0]["name"] == "Author3_name"
    assert data_2[1]["name"] == "Author4_name"


def test_change_author():
    response_1 = client.get(
        "/api/authors/"
    )
    data_1 = response_1.json()
    author_id = data_1[0]["id"]
    new_authors = "New_author2"
    client.put(
        f"/api/authors/{author_id}", json={"name": new_authors}
               )
    response_2 = client.get(f"/api/authors/{author_id}")
    data_2 = response_2.json()
    assert data_2["name"] == new_authors
    test_delet_author()

