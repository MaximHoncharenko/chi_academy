from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.article import Article
from app.models.user import User, UserRole
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/articles", tags=["articles"])


def _get_article_or_404(article_id: int, db: Session) -> Article:
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


@router.get("/", response_model=List[ArticleOut])
def list_articles(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(Article).offset(offset).limit(limit).all()


@router.get("/search", response_model=List[ArticleOut])
def search_articles(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    pattern = f"%{q}%"
    return (
        db.query(Article)
        .filter(Article.title.ilike(pattern) | Article.content.ilike(pattern))
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return _get_article_or_404(article_id, db)


@router.post("/", response_model=ArticleOut, status_code=status.HTTP_201_CREATED)
def create_article(
    payload: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = Article(**payload.model_dump(), author_id=current_user.id)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.put("/{article_id}", response_model=ArticleOut)
def update_article(
    article_id: int,
    payload: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = _get_article_or_404(article_id, db)

    if current_user.role == UserRole.user and article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your article",
        )

    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(article, key, val)

    db.commit()
    db.refresh(article)
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = _get_article_or_404(article_id, db)

    if current_user.role == UserRole.editor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editors cannot delete articles",
        )
    if current_user.role == UserRole.user and article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your article",
        )

    db.delete(article)
    db.commit()
