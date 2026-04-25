"""模块 m07_dict · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class DictInput(BaseModel):
    """词典 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class DictOutput(BaseModel):
    """词典 输出（占位）"""
    status: str
    module: str = "m07_dict"
    data: Optional[dict] = None
