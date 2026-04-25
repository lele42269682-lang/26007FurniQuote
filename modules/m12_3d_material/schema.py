"""模块 m12_3d_material · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TdMaterialInput(BaseModel):
    """Seedream材质换图 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class TdMaterialOutput(BaseModel):
    """Seedream材质换图 输出（占位）"""
    status: str
    module: str = "m12_3d_material"
    data: Optional[dict] = None
