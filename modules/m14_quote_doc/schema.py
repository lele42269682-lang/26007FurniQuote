"""模块 m14_quote_doc · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class QuoteDocInput(BaseModel):
    """报价单生成 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class QuoteDocOutput(BaseModel):
    """报价单生成 输出（占位）"""
    status: str
    module: str = "m14_quote_doc"
    data: Optional[dict] = None
