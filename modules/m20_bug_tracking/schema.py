"""m20_bug_tracking · 模块本地 Schema（引用 schemas.bug 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from schemas.bug import Bug, BugSeverity, BugStatus  # noqa: F401  对外暴露


class BugQueryFilter(BaseModel):
    """Bug 列表查询过滤器"""
    status: Optional[BugStatus] = None
    severity: Optional[BugSeverity] = None
    module: Optional[str] = None
    assignee: Optional[str] = None
    page: int = 1
    page_size: int = 20


class BugUpdatePayload(BaseModel):
    """Bug 状态更新载荷"""
    bug_id: str
    status: Optional[BugStatus] = None
    assignee: Optional[str] = None
    resolution: Optional[str] = None
    fix_commit_sha: Optional[str] = None
