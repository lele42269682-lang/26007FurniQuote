"""
api_gateway.py — 前后台接口统一层

所有模块的 FastAPI 路由必须通过此处注册，禁止前端直接 fetch 模块内部地址。
当前为骨架阶段，仅提供基础健康检查与模块发现接口；各模块开发完成后在此处挂载。
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI

from utils.logger import get_module_logger

logger = get_module_logger("API_GATEWAY")

# 各模块路由占位（开发后逐个 import 并 include_router）
MODULE_ROUTERS: dict[str, str] = {
    # 模块ID -> dotted path（待开发，目前注释保留）
    # "m10_pricing":  "modules.m10_pricing.main:router",
    # "m11_3d_modeling": "modules.m11_3d_modeling.main:router",
    # "m13_3d_viewer": "modules.m13_3d_viewer.main:router",
    # "m15_customer": "modules.m15_customer.main:router",
}


def _build_system_router(config: dict[str, Any]) -> APIRouter:
    """系统级路由：健康检查、模块清单、配置查看（脱敏）"""
    router = APIRouter(prefix="/api/system", tags=["system"])

    @router.get("/health")
    def health() -> dict:
        return {"status": "ok", "app": config.get("app", {}).get("name")}

    @router.get("/modules")
    def list_modules() -> dict:
        modules_cfg = config.get("modules", {})
        return {
            "total": len(modules_cfg),
            "modules": [
                {"id": k, "enabled": v.get("enabled"), "priority": v.get("priority")}
                for k, v in modules_cfg.items()
            ],
        }

    @router.get("/config")
    def show_config() -> dict:
        cfg = dict(config)
        cfg.pop("secrets", None)
        return cfg

    return router


def register_all(app: FastAPI, config: dict[str, Any]) -> None:
    """主入口：把系统路由 + 启用的业务模块路由挂到 FastAPI app 上。"""
    app.include_router(_build_system_router(config))
    logger.info("已注册系统路由 /api/system/*")

    enabled = [
        mid for mid, cfg in config.get("modules", {}).items() if cfg.get("enabled")
    ]
    if not enabled:
        logger.info("当前无启用的业务模块（骨架阶段，正常）")
        return

    for mid in enabled:
        dotted = MODULE_ROUTERS.get(mid)
        if not dotted:
            logger.warning(
                "模块 %s 在 config 中已启用，但 MODULE_ROUTERS 未登记路由，跳过", mid
            )
            continue
        # 待各模块开发完成后启用：
        # module_path, attr = dotted.split(":")
        # module = importlib.import_module(module_path)
        # app.include_router(getattr(module, attr))
        # logger.info("已注册模块路由 %s", mid)
