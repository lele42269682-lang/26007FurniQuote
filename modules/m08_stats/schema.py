"""模块 m08_stats · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from schemas.pricing import HistoricalReference


class StatsInput(BaseModel):
    """历史报价/统计统一入口输入。"""
    action: Literal[
        "upsert_quote",
        "get_quote",
        "list_quotes",
        "search",
        "import_quote_file",
        "import_quote_folder",
        "import_uploaded_quote_file",
        "analyze_price_factors",
    ]
    quote: Optional["HistoricalQuoteCreate"] = None
    import_request: Optional["QuoteImportRequest"] = None
    folder_request: Optional["QuoteFolderImportRequest"] = None
    upload_request: Optional["UploadedQuoteFileImportRequest"] = None
    quote_id: Optional[str] = None
    query_features: dict = Field(default_factory=dict)
    limit: int = Field(default=5, ge=1, le=50)
    min_support: int = Field(default=1, ge=1, le=100)
    note: Optional[str] = None


class HistoricalQuoteCreate(BaseModel):
    quote_id: str
    product_id: str
    product_name: str = ""
    category: str = ""
    description: str = ""
    features: dict = Field(default_factory=dict)
    customer_tier: str = ""
    region: str = ""
    quantity: int = Field(default=1, ge=1)
    final_price_cny: float = Field(..., gt=0)
    quoted_at: str


class HistoricalQuote(HistoricalQuoteCreate):
    created_at: str
    updated_at: str


class QuoteImportRequest(BaseModel):
    """导入历史报价单文件。"""
    file_path: str
    import_to_db: bool = True
    use_llm: Optional[bool] = None
    llm_provider_id: Optional[str] = None
    llm_model: Optional[str] = None
    usd_to_cny: Optional[float] = Field(default=None, gt=0)
    image_output_dir: Optional[str] = None
    default_customer_tier: str = ""
    default_region: str = ""
    default_currency: Optional[Literal["CNY", "USD"]] = None
    source_label: str = "historical_quote_file"
    limit: int = Field(default=500, ge=1, le=2000)
    note: Optional[str] = None


class UploadedQuoteFileImportRequest(QuoteImportRequest):
    """浏览器上传的历史报价单文件。"""
    file_path: str = ""
    file_name: str
    relative_path: str = ""
    content_base64: str


class QuoteFolderImportRequest(BaseModel):
    """导入本机文件夹下的历史报价单。"""
    folder_path: str
    recursive: bool = True
    import_to_db: bool = True
    use_llm: Optional[bool] = None
    llm_provider_id: Optional[str] = None
    llm_model: Optional[str] = None
    usd_to_cny: Optional[float] = Field(default=None, gt=0)
    image_output_dir: Optional[str] = None
    default_customer_tier: str = ""
    default_region: str = ""
    default_currency: Optional[Literal["CNY", "USD"]] = None
    source_label: str = "historical_quote_folder"
    limit: int = Field(default=500, ge=1, le=2000)
    max_files: int = Field(default=500, ge=1, le=5000)
    note: Optional[str] = None


class QuoteImportImage(BaseModel):
    """从报价单中抽出的图片。"""
    image_id: str
    source_sheet: str = ""
    anchor_row: int = 0
    anchor_col: int = 0
    file_path: str


class QuoteImportResult(BaseModel):
    """历史报价单导入结果。"""
    import_id: str
    source_file: str
    file_type: str
    quote_no: str = ""
    quote_date: str = ""
    customer_name: str = ""
    usd_to_cny: float
    imported_count: int = 0
    recognized_count: int = 0
    preview_count: int = 0
    skipped_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    images: list[QuoteImportImage] = Field(default_factory=list)
    quotes: list[HistoricalQuote] = Field(default_factory=list)
    preview_items: list[dict] = Field(default_factory=list)


class StatsOutput(BaseModel):
    """历史报价/统计统一入口输出。"""
    status: str
    module: str = "m08_stats"
    data: Optional[
        HistoricalQuote |
        list[HistoricalQuote] |
        list[HistoricalReference] |
        QuoteImportResult |
        dict
    ] = None
    error: Optional[str] = None


StatsInput.model_rebuild()
