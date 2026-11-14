"""Isolated SQLite tests: the delivered application still defaults to PostgreSQL."""
import os
os.environ['DATABASE_URL'] = 'sqlite://'
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from scripts.generate_data import generate
from scripts.seed import load_jobs, load_candidates

@pytest.fixture
def db():
    engine = create_engine('sqlite://', connect_args={'check_same_thread':False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        generate()
        load_jobs(session)
        load_candidates(session)
        yield session
    engine.dispose()

@pytest.fixture
def client(db):
    def get_test_db():
        yield db
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
