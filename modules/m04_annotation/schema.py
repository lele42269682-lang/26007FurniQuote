"""模块 m04_annotation · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class AnnotationInput(BaseModel):
    """标注 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class AnnotationOutput(BaseModel):
    """标注 输出（占位）"""
    status: str
    module: str = "m04_annotation"
    data: Optional[dict] = None
