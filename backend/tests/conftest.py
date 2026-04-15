import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base, get_db
from src.models.user import User
from src.models.virtual_machine import VirtualMachine
from src.services.auth_service import AuthService


# Тестовая БД SQLite (для быстрых тестов)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Очищаем БД перед каждым тестом"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def _get_test_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = _get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    auth_service = AuthService(db)
    result = auth_service.register("test@example.com", "test123")
    
    user = db.query(User).filter(User.email == "test@example.com").first()
    return user, result["access_token"]


@pytest.fixture
def test_vm(db):
    vm = VirtualMachine(
        name="Test Proxy",
        host="test.proxy.com",
        port=1080,
        protocol="SOCKS5",
        is_active=True
    )
    db.add(vm)
    db.commit()
    db.refresh(vm)
    return vm