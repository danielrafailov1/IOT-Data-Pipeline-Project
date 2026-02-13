"""Pytest fixtures."""
import os
import pytest
from fastapi.testclient import TestClient

# Use SQLite for tests
os.environ["TESTING"] = "1"

from app.main import app
from app.core.database import Base, get_db, engine


@pytest.fixture
def client():
    from app.core.database import SessionLocal
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db_session():
    from app.core.database import SessionLocal
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
