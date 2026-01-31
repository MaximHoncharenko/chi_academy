from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

# Створення таблиць у базі даних
models.Base.metadata.create_all(bind=engine)

# Ініціалізація FastAPI
app = FastAPI(
    title="User Management API",
    description="Simple CRUD API для управління користувачами",
    version="1.0.0"
)


@app.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Створити нового користувача
    """
    # Перевірка чи існує користувач з таким email
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email вже зареєстрований"
        )
    
    # Створення нового користувача
    new_user = models.User(
        name=user.name,
        email=user.email,
        is_active=user.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.get("/users", response_model=List[schemas.UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Отримати список всіх користувачів
    
    - **skip**: кількість записів для пропуску (пагінація)
    - **limit**: максимальна кількість записів для повернення
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Отримати одного користувача за ID
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з ID {user_id} не знайдено"
        )
    
    return user


@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    """
    Оновити дані користувача (name, email, is_active)
    """
    # Знайти користувача
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з ID {user_id} не знайдено"
        )
    
    # Перевірка унікальності email, якщо він змінюється
    if user_update.email and user_update.email != db_user.email:
        existing_user = db.query(models.User).filter(models.User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email вже зареєстрований"
            )
    
    # Оновлення полів
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Видалити користувача за ID
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з ID {user_id} не знайдено"
        )
    
    db.delete(db_user)
    db.commit()
    
    return None


@app.get("/")
def root():
    """
    Головна сторінка API
    """
    return {
        "message": "User Management API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
