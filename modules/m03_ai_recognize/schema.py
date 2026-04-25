"""模块 m03_ai_recognize · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class AiRecognizeInput(BaseModel):
    """AI视觉识别 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class AiRecognizeOutput(BaseModel):
    """AI视觉识别 输出（占位）"""
    status: str
    module: str = "m03_ai_recognize"
    data: Optional[dict] = None
