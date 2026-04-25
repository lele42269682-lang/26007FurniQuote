"""FurniQuote AI · 全局 I/O Schema

所有跨模块数据传递必须使用此处定义的类型，禁止传裸 dict。
"""
from schemas.common import CustomerTier, PriceAcceptance, RegionCode, ProductCategory
from schemas.customer import Customer, CustomerCreate
from schemas.product import Product, ProductLifecycleStage
from schemas.pricing import PricingRequest, PricingResponse, PricingBreakdown
from schemas.quote import Quote, QuoteVersion, QuoteStatus

__all__ = [
    "CustomerTier",
    "PriceAcceptance",
    "RegionCode",
    "ProductCategory",
    "Customer",
    "CustomerCreate",
    "Product",
    "ProductLifecycleStage",
    "PricingRequest",
    "PricingResponse",
    "PricingBreakdown",
    "Quote",
    "QuoteVersion",
    "QuoteStatus",
]
