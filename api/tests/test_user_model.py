import uuid
import datetime
import pytest
from api.db import Base, get_engine, get_session
from api.models import User

@pytest.fixture
def in_memory_db():
    engine = get_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

def test_user_model_crud(in_memory_db):
    engine = in_memory_db
    session = get_session(engine)
    user_id = uuid.uuid4()
    now = datetime.datetime.utcnow()
    user = User(
        id=user_id,
        email="test@example.com",
        name="Test User",
        last_login=now,
        is_active=True,
        is_admin=False,
    )
    session.add(user)
    session.commit()
    retrieved = session.query(User).filter_by(email="test@example.com").first()
    assert retrieved is not None
    assert retrieved.id == user_id
    assert retrieved.email == "test@example.com"
    assert retrieved.name == "Test User"
    assert retrieved.last_login == now
    assert retrieved.is_active is True
    assert retrieved.is_admin is False
    session.close() 