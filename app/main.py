"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from .api.routes import router

app = FastAPI(title="Book Catalog Service")
app.include_router(router)


@app.get("/")
def health_check() -> dict[str, str]:
    """Provide a friendly ping endpoint."""

    return {"message": "Book catalog service ready"}
