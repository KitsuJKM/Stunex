from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.database import get_db

app = FastAPI(title="Stunex API")


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
