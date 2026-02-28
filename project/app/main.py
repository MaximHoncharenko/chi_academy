from fastapi import FastAPI

from app.routers import auth, users, articles

app = FastAPI(
    title="Articles API",
    version="1.0.0",
    description="REST API with JWT auth and role-based access control",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(articles.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
