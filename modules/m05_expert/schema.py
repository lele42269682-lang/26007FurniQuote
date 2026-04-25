"""模块 m05_expert · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ExpertInput(BaseModel):
    """专家审核 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class ExpertOutput(BaseModel):
    """专家审核 输出（占位）"""
    status: str
    module: str = "m05_expert"
    data: Optional[dict] = None
