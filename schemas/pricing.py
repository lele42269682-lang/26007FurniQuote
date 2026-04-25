"""M-10 报价引擎 I/O Schema"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from schemas.common import PriceAcceptance


class PricingRequest(BaseModel):
    """报价计算输入"""
    product_features: dict = Field(..., description="AI识别+人工校正的产品特征")
    customer_id: str
    quantity: int = Field(..., ge=1)
    custom_acceptance: Optional[PriceAcceptance] = Field(
        None, description="本次询价临时调整承价等级，覆盖客户档案默认值"
    )
    note: Optional[str] = None


class PricingBreakdown(BaseModel):
    """五维系数明细（仅业务员可见，对客户隐藏）"""
    base_price_cny: float = Field(..., description="基准价（历史相似产品中位数）")
    customer_tier_coef: float
    quantity_coef: float
    exchange_rate_usd: float
    exchange_rate_idr: float
    price_acceptance_coef: float
    region_coef: float


class HistoricalReference(BaseModel):
    """RAG 检索的相似历史报价"""
    quote_id: str
    product_id: str
    similarity: float
    final_price_cny: float
    customer_tier: str
    quoted_at: str


class PricingResponse(BaseModel):
    """报价计算输出"""
    suggested_price_cny: float
    suggested_price_usd: float
    suggested_price_idr: float
    breakdown: PricingBreakdown
    historical_references: list[HistoricalReference] = Field(default_factory=list)
    confidence: str = Field(..., pattern="^(high|medium|low)$")
    warnings: list[str] = Field(default_factory=list)
