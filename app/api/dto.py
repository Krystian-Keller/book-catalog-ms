"""Pydantic DTOs shared by all API endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BookDTO(BaseModel):
    """Payload used when creating a book."""

    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: str = Field(..., min_length=3)
    publisher: str = Field(..., min_length=1)
    pages: int = Field(..., ge=1)


class BookUpdateDTO(BaseModel):
    """Payload used for updates where ISBN comes from the path."""

    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    publisher: str = Field(..., min_length=1)
    pages: int = Field(..., ge=1)


class ImportRequestDTO(BaseModel):
    """Request body for catalog import operations."""

    format: Literal["json", "xml"]
    content: str


class ExportRequestDTO(BaseModel):
    """Request body for catalog export operations."""

    format: Literal["json", "xml"]


class ExportResponseDTO(BaseModel):
    """Wrapper returned by the export endpoint."""

    content: str


class UndoResponseDTO(BaseModel):
    """Response body containing undo metadata."""

    books: list[BookDTO]
    remaining_undos: int = Field(..., ge=0)
