"""产品档案与生命周期 Schema"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from schemas.common import ProductCategory


class ProductLifecycleStage(str, Enum):
    """产品生命周期阶段（与 M-16 业务流程引擎对齐）"""
    INQUIRY = "inquiry"             # 询价
    QUOTING = "quoting"             # 报价中
    NEGOTIATING = "negotiating"     # 还价中
    DEPOSIT_PAID = "deposit_paid"   # 定金到账
    DRAWING = "drawing"             # 出图
    PRODUCTION = "production"       # 投产
    COMPLETED = "completed"         # 完工
    ARCHIVED = "archived"           # 存档


class Product(BaseModel):
    """产品基础档案。

    一个 product_id 从询价到存档全程贯穿，不分阶段重编。
    """
    product_id: str = Field(..., description="{category}-{year}-{seq:03d}，如 SF-2024-001")
    name: str
    category: ProductCategory
    series: Optional[str] = Field(None, description="产品系列，如 凡尔赛系列（不强制）")

    # 规格尺寸（毫米）
    width_mm: Optional[int] = None
    depth_mm: Optional[int] = None
    height_mm: Optional[int] = None

    # 工艺特征（AI 识别 + 人工校正）
    features: dict = Field(default_factory=dict, description="材质/雕花/面料/工艺等")

    # 资产路径
    reference_images: list[str] = Field(default_factory=list)
    glb_model_path: Optional[str] = None
    cnc_files: list[str] = Field(default_factory=list, description="STL/STEP 雕花文件")

    is_proprietary: bool = Field(False, description="客户专有产品，不上云")

    current_stage: ProductLifecycleStage = ProductLifecycleStage.INQUIRY

    created_at: datetime
    updated_at: datetime
