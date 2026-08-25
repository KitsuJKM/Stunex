from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from auth.router import router as auth_router
from core.database import get_db
from profile.router import router as profile_router

app = FastAPI(title="Stunex API")

app.include_router(auth_router)
app.include_router(profile_router)


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
