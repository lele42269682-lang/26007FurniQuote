"""模块 m06_material · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class MaterialInput(BaseModel):
    """材质库 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class MaterialOutput(BaseModel):
    """材质库 输出（占位）"""
    status: str
    module: str = "m06_material"
    data: Optional[dict] = None
