"""模块 m15_customer · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class CustomerInput(BaseModel):
    """客户档案 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class CustomerOutput(BaseModel):
    """客户档案 输出（占位）"""
    status: str
    module: str = "m15_customer"
    data: Optional[dict] = None
