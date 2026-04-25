"""M-15 客户档案 Schema"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from schemas.common import CustomerTier, PriceAcceptance, RegionCode


class CustomerCreate(BaseModel):
    """新建客户输入"""
    company_name: str
    contact_person: str
    phone: str = Field(..., description="国际手机号，含国家区号")
    email: Optional[str] = None
    region: RegionCode
    tier: CustomerTier = CustomerTier.L1
    tier_reason: str = ""
    price_acceptance: PriceAcceptance = PriceAcceptance.B
    industry: str = "未分类"
    is_long_term: bool = False
    locked_price_agreement: Optional[str] = None


class Customer(CustomerCreate):
    """完整客户档案（含系统生成字段）"""
    customer_id: str = Field(..., description="C-{region}-{seq:03d}")

    # 客户门户字段
    is_portal_user: bool = False
    portal_approved_by: Optional[str] = None
    portal_device_fingerprints: list[str] = Field(default_factory=list)

    # 关联记录
    inquiries: list[str] = Field(default_factory=list)
    quotes: list[str] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime
