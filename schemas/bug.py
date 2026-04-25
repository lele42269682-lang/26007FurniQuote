"""M-20 / M-21 Bug 记录与上报 Schema"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BugSeverity(str, Enum):
    """Bug 严重程度"""
    CRITICAL = "critical"   # 阻塞核心流程（报价/审核/付款）
    HIGH = "high"           # 影响主要功能但有规避方案
    MEDIUM = "medium"       # 体验问题或非关键功能异常
    LOW = "low"             # 视觉/文案/边缘场景


class BugStatus(str, Enum):
    """Bug 状态"""
    OPEN = "open"               # 已上报，待分配
    TRIAGED = "triaged"         # 已分类，已分配负责人
    IN_PROGRESS = "in_progress" # 修复中
    RESOLVED = "resolved"       # 已修复，待验证
    VERIFIED = "verified"       # 验证通过，可关闭
    CLOSED = "closed"           # 关闭
    REJECTED = "rejected"       # 不予修复（重复/无效）


class BugSource(str, Enum):
    """Bug 来源（M-21 上报渠道）"""
    INTERNAL_USER = "internal_user"   # 业务员/总经理
    CUSTOMER = "customer"             # 海外客户（客户门户上报）
    AUTO_TEST = "auto_test"           # 自动化测试失败自动上报
    DASHBOARD = "dashboard"           # 测试 Dashboard 手动触发
    MONITORING = "monitoring"         # 监控告警自动产生


class BugReportInput(BaseModel):
    """M-21 上报入口的输入（含自动收集的上下文）"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str
    severity: BugSeverity = BugSeverity.MEDIUM
    source: BugSource

    # 上报人
    reporter_id: str = Field(..., description="用户ID或客户ID")
    reporter_name: str = ""

    # 关联模块（19+2 模块编号）
    module: Optional[str] = Field(None, description="如 m10_pricing")

    # 复现信息
    reproduction_steps: list[str] = Field(default_factory=list)

    # 自动收集的上下文
    page_url: Optional[str] = None
    user_agent: Optional[str] = None
    console_logs: list[str] = Field(default_factory=list)
    screenshot_paths: list[str] = Field(default_factory=list)
    request_id: Optional[str] = Field(None, description="后端请求追踪ID")


class Bug(BaseModel):
    """M-20 Bug 记录主体"""
    bug_id: str = Field(..., description="BUG-{年份}-{序号}，如 BUG-2025-0042")
    title: str
    description: str
    severity: BugSeverity
    status: BugStatus = BugStatus.OPEN
    source: BugSource

    reporter_id: str
    reporter_name: str = ""
    assignee: Optional[str] = None

    module: Optional[str] = None
    reproduction_steps: list[str] = Field(default_factory=list)

    # 上下文快照
    page_url: Optional[str] = None
    user_agent: Optional[str] = None
    console_logs: list[str] = Field(default_factory=list)
    screenshot_paths: list[str] = Field(default_factory=list)
    request_id: Optional[str] = None

    # 修复记录
    resolution: Optional[str] = None
    fix_commit_sha: Optional[str] = None
    related_bug_ids: list[str] = Field(default_factory=list)

    # 通知联动
    dingtalk_thread_id: Optional[str] = Field(
        None, description="钉钉协作线程ID（M-17 接入后联动）"
    )

    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
