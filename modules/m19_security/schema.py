"""模块 m19_security · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SecurityInput(BaseModel):
    """安全防泄露 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class SecurityOutput(BaseModel):
    """安全防泄露 输出（占位）"""
    status: str
    module: str = "m19_security"
    data: Optional[dict] = None
