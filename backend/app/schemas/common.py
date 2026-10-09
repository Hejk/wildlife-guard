"""通用响应与分页模型。"""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应结构。"""
    code: int = 0
    message: str = "success"
    data: T | None = None


class PageResult(BaseModel, Generic[T]):
    """分页结果。"""
    total: int
    page: int
    page_size: int
    items: list[T]
