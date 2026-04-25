"""m21_bug_report · 模块本地 Schema（引用 schemas.bug 全局类型）"""
from __future__ import annotations

from pydantic import BaseModel

from schemas.bug import BugReportInput, BugSource  # noqa: F401  对外暴露


class BugReportResponse(BaseModel):
    """上报后的反馈"""
    bug_id: str
    status: str
    message: str = "已收到上报，团队会尽快处理"
