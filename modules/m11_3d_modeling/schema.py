"""模块 m11_3d_modeling · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TdModelingInput(BaseModel):
    """混元3D建模 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class TdModelingOutput(BaseModel):
    """混元3D建模 输出（占位）"""
    status: str
    module: str = "m11_3d_modeling"
    data: Optional[dict] = None
