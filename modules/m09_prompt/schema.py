"""模块 m09_prompt · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PromptInput(BaseModel):
    """Prompt管理 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class PromptOutput(BaseModel):
    """Prompt管理 输出（占位）"""
    status: str
    module: str = "m09_prompt"
    data: Optional[dict] = None
