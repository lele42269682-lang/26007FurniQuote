"""
api_gateway.py — 前后台接口统一层

设计原则（"分与合"隔离）：
  - 注册任何模块路由失败时，仅记 Error 并跳过该模块，绝不让单点失败阻塞整个 FastAPI 启动
  - 所有路由均经过 utils.isolation 装饰，业务异常不外泄给前端
  - 前端禁止直接 fetch 模块内部地址，必须走 /api/{module_id}/* 前缀
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI

from modules.registry import MODULES, health_check_all, list_modules
from utils.isolation import safe_import_module
from utils.logger import get_module_logger, log_error

logger = get_module_logger("API_GATEWAY")


def _build_system_router(config: dict[str, Any]) -> APIRouter:
    """系统级路由：健康检查、模块清单、配置查看（脱敏）、模块隔离健康检查"""
    router = APIRouter(prefix="/api/system", tags=["system"])

    @router.get("/health")
    def health() -> dict:
        return {"status": "ok", "app": config.get("app", {}).get("name")}

    @router.get("/modules")
    def list_all_modules() -> dict:
        modules_cfg = config.get("modules", {})
        rows = []
        for meta in list_modules():
            cfg = modules_cfg.get(meta.id, {})
            rows.append({
                "id": meta.id,
                "name": meta.name,
                "priority": meta.priority,
                "enabled": cfg.get("enabled", False),
                "depends_on": meta.depends_on,
                "soft_depends": meta.soft_depends,
            })
        return {"total": len(rows), "modules": rows}

    @router.get("/modules/health")
    def modules_health() -> dict:
        """逐模块独立健康检查 — 单个失败不影响其他结果。"""
        results = health_check_all()
        ok_count = sum(1 for r in results if r.get("ok"))
        return {"ok_count": ok_count, "total": len(results), "details": results}

    @router.get("/config")
    def show_config() -> dict:
        cfg = dict(config)
        cfg.pop("secrets", None)
        return cfg

    return router


def register_all(app: FastAPI, config: dict[str, Any]) -> None:
    """挂载系统路由 + 各启用业务模块路由。

    任何模块路由注册失败仅记录错误，不影响其他模块或系统启动。
    """
    app.include_router(_build_system_router(config))
    logger.info("已注册系统路由 /api/system/*")

    enabled = [
        mid for mid, cfg in config.get("modules", {}).items() if cfg.get("enabled")
    ]
    if not enabled:
        logger.info("当前无启用的业务模块（骨架阶段，正常）")
        return

    registered = 0
    for mid in enabled:
        try:
            module = safe_import_module(f"modules.{mid}.main")
            if module is None:
                continue
            # 模块若导出 router，统一挂到 /api/{mid}/*
            if hasattr(module, "router"):
                app.include_router(module.router, prefix=f"/api/{mid}", tags=[mid])
                registered += 1
                logger.info("已注册模块路由 %s -> /api/%s/*", mid, mid)
            else:
                logger.info("模块 %s 已启用但无 router（仅函数级模块），跳过路由注册", mid)
        except Exception as exc:  # noqa: BLE001  网关必须兜底
            log_error(logger, f"模块 {mid} 路由注册失败（跳过，不影响其他模块）: {exc}")

    logger.info("路由注册完成: %d/%d 个启用模块", registered, len(enabled))
