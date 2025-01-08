from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.api.v1.enums.enums import TicketStatusEnum


class TicketCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Название тикета должно быть от 1 до 100 символов")
    description: str = Field(..., min_length=10, description="Описание тикета должно содержать минимум 10 символов")
    user_id: int = Field(..., ge=1, description="ID пользователя должен быть положительным целым числом")
    status: TicketStatusEnum = Field(TicketStatusEnum.NEW, description="Статус тикета, по умолчанию 'new'")

    @field_validator("title")
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Название тикета не должно быть пустым или состоять только из пробелов")
        return value

    @field_validator("description")
    def validate_description(cls, value: str) -> str:
        if len(value.strip()) < 10:
            raise ValueError("Описание тикета должно содержать минимум 10 символов")
        return value


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatusEnum
    created_at: datetime
    updated_at: datetime
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Имя пользователя должно быть от 1 до 50 символов")
    email: EmailStr = Field(..., description="Должен быть корректным email-адресом")

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Имя пользователя не должно быть пустым или состоять только из пробелов")
        return value


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class OperatorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Имя оператора должно быть от 1 до 50 символов")
    email: EmailStr = Field(..., description="Должен быть корректным email-адресом")

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Имя оператора не должно быть пустым или состоять только из пробелов")
        return value


class OperatorResponse(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)
