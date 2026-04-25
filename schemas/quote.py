"""报价单 Schema（M-14 报价单生成 + M-16 业务流程使用）"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class QuoteStatus(str, Enum):
    """报价单状态（与 14 步业务流程节点对齐）"""
    DRAFTING = "drafting"           # 业务员制作中
    REVIEWING = "reviewing"         # 总经理审核
    SENT = "sent"                   # 已发送给客户
    NEGOTIATING = "negotiating"     # 还价中
    CONFIRMED = "confirmed"         # 价格确认
    EXPIRED = "expired"             # 已过期
    CANCELLED = "cancelled"


class QuoteVersion(BaseModel):
    """报价单单个版本快照（同一询价通常 1-2 个版本）"""
    version_no: int = Field(..., ge=1)
    price_cny: float
    price_usd: float
    price_idr: float
    quantity_breakdown: dict = Field(default_factory=dict, description="阶梯价格表")
    rendered_image_paths: list[str] = Field(default_factory=list)
    note: str = ""
    created_by: str
    created_at: datetime


class Quote(BaseModel):
    """报价单主体"""
    quote_id: str = Field(..., description="Q{年份}{序号}，如 Q2024001")
    product_id: str
    customer_id: str

    status: QuoteStatus = QuoteStatus.DRAFTING
    versions: list[QuoteVersion] = Field(default_factory=list)
    current_version: int = 1

    valid_until: datetime
    is_ex_works: bool = True

    # 防泄露
    watermark_id: str = Field(..., description="唯一溯源水印（含客户ID+时间戳）")
    view_count: int = 0

    # 审核记录
    reviewer: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime
