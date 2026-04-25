"""模块 m17_dingtalk · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class DingtalkInput(BaseModel):
    """钉钉集成 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class DingtalkOutput(BaseModel):
    """钉钉集成 输出（占位）"""
    status: str
    module: str = "m17_dingtalk"
    data: Optional[dict] = None
