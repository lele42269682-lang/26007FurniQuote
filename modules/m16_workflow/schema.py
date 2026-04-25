"""模块 m16_workflow · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class WorkflowInput(BaseModel):
    """业务流程引擎 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class WorkflowOutput(BaseModel):
    """业务流程引擎 输出（占位）"""
    status: str
    module: str = "m16_workflow"
    data: Optional[dict] = None
