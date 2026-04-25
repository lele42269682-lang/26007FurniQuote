"""模块 m10_pricing · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PricingInput(BaseModel):
    """报价引擎 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class PricingOutput(BaseModel):
    """报价引擎 输出（占位）"""
    status: str
    module: str = "m10_pricing"
    data: Optional[dict] = None
