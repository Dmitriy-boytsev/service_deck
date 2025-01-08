import pytest
from pydantic import ValidationError
from app.api.v1.shemas.shemas import TicketCreateRequest, UserCreate

def test_valid_user_schema():
    """Тест корректных данных для создания пользователя"""
    data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    user = UserCreate(**data)

    assert user.name == "Test User"
    assert user.email == "test@example.com"

def test_invalid_user_schema():
    """Тест некорректных данных для создания пользователя"""
    data = {
        "name": "",
        "email": "not-an-email"
    }

    with pytest.raises(ValidationError):
        UserCreate(**data)

def test_valid_ticket_schema():
    """Тест корректных данных для создания тикета"""
    data = {
        "title": "Test Ticket",
        "description": "Some description",
        "status": "new",
        "user_id": 1
    }
    ticket = TicketCreateRequest(**data)

    assert ticket.title == "Test Ticket"
    assert ticket.status == "new"

def test_invalid_ticket_schema():
    """Тест некорректных данных для создания тикета"""
    data = {
        "title": "",
        "description": "Some description",
        "status": "invalid_status",
        "user_id": -1
    }

    with pytest.raises(ValidationError):
        TicketCreateRequest(**data)
