import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


from app.main import app
from app.core.db.session import get_db
from app.api.v1.models.models import Base, User, Operator


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
def test_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_create_user_success(test_client, db_session):
    payload = {"name": "John Doe", "email": "john.doe@example.com"}
    response = test_client.post("/api/v1/tickets/create_user", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]

    query = await db_session.execute(select(User).filter(User.email == payload["email"]))
    user = query.scalars().first()
    assert user is not None
    assert user.email == payload["email"]


@pytest.mark.asyncio
async def test_create_tickets_success(test_client, db_session):
    payload = {"title": "string", "description": "description", "user_id": 1}
    response = test_client.post("/api/v1/tickets/create_ticket", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["user_id"] == payload["user_id"]


@pytest.mark.asyncio
async def test_create_operator_success(test_client, db_session):
    payload = {"name": "John Doe", "email": "john.doe@example.com"}
    response = test_client.post("/api/v1/tickets/create_operator", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]

    query = await db_session.execute(select(Operator).filter(Operator.email == payload["email"]))
    operator = query.scalars().first()
    assert operator is not None
    assert operator.email == payload["email"]
