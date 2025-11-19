"""FastAPI router exposing catalog endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..domain.catalog import Catalog
from ..domain.services import CatalogService
from ..domain.undo_manager import UndoManager
from ..infrastructure.factories.format_factory import FormatFactory
from .dto import (
    BookDTO,
    BookUpdateDTO,
    ExportRequestDTO,
    ExportResponseDTO,
    ImportRequestDTO,
    UndoResponseDTO,
)

router = APIRouter(prefix="/catalog", tags=["catalog"])

_service = CatalogService(Catalog(), UndoManager(), FormatFactory())


def get_service() -> CatalogService:
    """Provide a singleton service instance to the routes."""

    return _service


@router.get("/books", response_model=list[BookDTO])
def list_books(service: CatalogService = Depends(get_service)) -> list[BookDTO]:
    """Return all books."""

    return [BookDTO(**book) for book in service.list_books()]


@router.get("/books/{isbn}", response_model=BookDTO)
def get_book(isbn: str, service: CatalogService = Depends(get_service)) -> BookDTO:
    """Return a single book or raise 404 when missing."""

    try:
        return BookDTO(**service.get_book(isbn))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/books", response_model=BookDTO, status_code=status.HTTP_201_CREATED)
def add_book(payload: BookDTO, service: CatalogService = Depends(get_service)) -> BookDTO:
    """Insert a book using the facade."""

    try:
        created = service.add_book(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return BookDTO(**created)


@router.put("/books/{isbn}", response_model=BookDTO)
def update_book(
    isbn: str,
    payload: BookUpdateDTO,
    service: CatalogService = Depends(get_service),
) -> BookDTO:
    """Update a book."""

    try:
        updated = service.update_book(isbn, payload.model_dump())
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return BookDTO(**updated)


@router.delete("/books/{isbn}", status_code=status.HTTP_200_OK)
def delete_book(isbn: str, service: CatalogService = Depends(get_service)) -> dict:
    """Remove a book."""

    try:
        service.remove_book(isbn)
        return {"status": "deleted"}
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/import")
def import_catalog(payload: ImportRequestDTO, service: CatalogService = Depends(get_service)) -> dict:
    """Import the catalog from a serialized document."""

    try:
        count = service.import_catalog(payload.content, payload.format)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"count": count}


@router.post("/export", response_model=ExportResponseDTO)
def export_catalog(payload: ExportRequestDTO, service: CatalogService = Depends(get_service)) -> ExportResponseDTO:
    """Export the catalog to the selected format."""

    try:
        content = service.export_catalog(payload.format)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ExportResponseDTO(content=content)


@router.post("/undo", response_model=UndoResponseDTO)
def undo(service: CatalogService = Depends(get_service)) -> UndoResponseDTO:
    """Undo the most recent change and expose undo metadata."""

    try:
        payload = service.undo()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return UndoResponseDTO(
        books=[BookDTO(**book) for book in payload["books"]],
        remaining_undos=payload["remaining_undos"],
    )
