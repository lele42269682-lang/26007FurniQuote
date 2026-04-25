"""模块 m18_portal · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PortalInput(BaseModel):
    """客户门户 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class PortalOutput(BaseModel):
    """客户门户 输出（占位）"""
    status: str
    module: str = "m18_portal"
    data: Optional[dict] = None
