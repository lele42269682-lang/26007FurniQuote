"""模块 m08_stats · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class StatsInput(BaseModel):
    """统计与RAG 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class StatsOutput(BaseModel):
    """统计与RAG 输出（占位）"""
    status: str
    module: str = "m08_stats"
    data: Optional[dict] = None
