"""模块 m13_3d_viewer · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TdViewerInput(BaseModel):
    """Three.js查看器 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class TdViewerOutput(BaseModel):
    """Three.js查看器 输出（占位）"""
    status: str
    module: str = "m13_3d_viewer"
    data: Optional[dict] = None
