"""模块 m02_folder · 本地 Schema（引用 schemas/ 全局类型）"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class FolderInput(BaseModel):
    """文件夹管理 输入（占位，开发时补充字段）"""
    payload: dict
    note: Optional[str] = None


class FolderOutput(BaseModel):
    """文件夹管理 输出（占位）"""
    status: str
    module: str = "m02_folder"
    data: Optional[dict] = None
