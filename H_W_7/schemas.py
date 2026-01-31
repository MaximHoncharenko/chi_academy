from pydantic import BaseModel, EmailStr


# Базова схема для створення користувача
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True


# Схема для оновлення користувача
class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None


# Схема для відповіді (включає id)
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True  # Для SQLAlchemy моделей (раніше orm_mode)
