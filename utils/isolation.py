"""
模块隔离工具 — 保证"一个模块出问题不会牵连其他模块"

核心设计：
  - @isolated 装饰器：捕获模块内部异常，转换为标准错误响应，绝不向上抛出
  - safe_import_module(): 模块导入失败时只记 Error 并返回 None，不阻塞调用方
  - call_module(): 通过模块注册中心调用其他模块，失败时返回降级结果

使用范例（在每个模块的 main.py 中）：

    from utils.isolation import isolated

    @isolated(module_id="m10_pricing")
    def run(payload: dict) -> dict:
        ...
"""
from __future__ import annotations

import functools
import importlib
import traceback
from typing import Any, Callable

from utils.logger import get_module_logger, log_error

_iso_logger = get_module_logger("ISOLATION")


def isolated(module_id: str) -> Callable:
    """模块入口装饰器：把模块内部异常转换成标准错误响应。

    返回的字典结构：
      正常: 模块原返回值
      异常: {"status": "error", "module": <id>, "error": <message>, "isolated": true}
    """
    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        logger = get_module_logger(module_id.upper())

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                tb = traceback.format_exc()
                log_error(logger, f"模块 {module_id} 执行异常: {exc}")
                logger.debug("Traceback:\n%s", tb)
                # 失败上报联动（避免循环依赖：仅记录意图，由 m21 实际处理）
                _signal_bug_report(module_id, str(exc), tb)
                return {
                    "status": "error",
                    "module": module_id,
                    "error": str(exc),
                    "isolated": True,
                }
        wrapper.__isolated__ = True  # type: ignore[attr-defined]
        return wrapper
    return deco


def _signal_bug_report(module_id: str, error: str, traceback_text: str) -> None:
    """异常时尝试调用 m21_bug_report 自动建 Bug。

    采用懒加载 + try/except 防止 m21 自身异常或未启用时阻塞主调用方。
    """
    try:
        m21 = importlib.import_module("modules.m21_bug_report.main")
        if hasattr(m21, "run"):
            m21.run({
                "title": f"[自动上报] {module_id} 运行异常",
                "description": error,
                "severity": "high",
                "source": "auto_test",
                "reporter_id": "isolation_layer",
                "module": module_id,
                "console_logs": traceback_text.split("\n")[-20:],
            })
    except Exception as inner:  # noqa: BLE001  保护层不抛
        _iso_logger.debug("自动上报 Bug 失败（忽略，不影响主调用）: %s", inner)


def safe_import_module(dotted_path: str) -> Any | None:
    """安全导入模块。失败时只记录错误并返回 None。"""
    try:
        return importlib.import_module(dotted_path)
    except Exception as exc:  # noqa: BLE001  导入层必须捕获所有异常
        log_error(_iso_logger, f"导入模块失败 {dotted_path}: {exc}")
        return None


def call_module(module_id: str, payload: dict, fallback: dict | None = None) -> dict:
    """通过模块注册中心调用其他模块，提供降级保护。

    使用方式：
        result = call_module("m10_pricing", {"customer_id": "C-US-001", ...})

    若目标模块未启用、不存在或抛异常，返回 fallback（默认空降级）。
    """
    fallback = fallback or {"status": "fallback", "module": module_id, "available": False}
    module = safe_import_module(f"modules.{module_id}.main")
    if module is None or not hasattr(module, "run"):
        log_error(_iso_logger, f"模块 {module_id} 不可用，返回降级")
        return fallback
    try:
        return module.run(payload)
    except Exception as exc:  # noqa: BLE001  调用层兜底
        log_error(_iso_logger, f"调用模块 {module_id} 异常: {exc}")
        return fallback
