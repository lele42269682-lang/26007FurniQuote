"""
烟囱测试 · 项目骨架基本可用性检查

验证：
  - master 可加载、配置可读
  - 全部 19 个模块可 import 且 run() 返回标准占位响应
  - logger 写入文件且格式正确
  - 全部启动检查项通过
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


MODULE_IDS = [
    "m01_auth", "m02_folder", "m03_ai_recognize", "m04_annotation",
    "m05_expert", "m06_material", "m07_dict", "m08_stats", "m09_prompt",
    "m10_pricing", "m11_3d_modeling", "m12_3d_material", "m13_3d_viewer",
    "m14_quote_doc", "m15_customer", "m16_workflow", "m17_dingtalk",
    "m18_portal", "m19_security",
]


def test_config_yaml_loadable():
    import yaml
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    assert cfg["app"]["name"] == "FurniQuote AI"
    assert cfg["pricing"]["region"]["US"] == 1.3
    assert len(cfg["modules"]) == 19


def test_master_importable():
    master = importlib.import_module("master")
    assert hasattr(master, "main")
    assert hasattr(master, "run_startup_checks")
    assert hasattr(master, "create_app")


def test_startup_checks_pass():
    from master import run_startup_checks
    checks = run_startup_checks()
    failed = [(name, detail) for name, ok, detail in checks if not ok]
    assert not failed, f"启动检查失败: {failed}"


def test_schemas_importable():
    from schemas import (
        Customer, Product, Quote, PricingRequest, PricingResponse,
        CustomerTier, RegionCode,
    )
    assert CustomerTier.L1.value == "L1"
    assert RegionCode.US.value == "US"


@pytest.mark.parametrize("mid", MODULE_IDS)
def test_module_runnable(mid):
    """每个模块可 import 且 run() 返回标准占位响应。"""
    module = importlib.import_module(f"modules.{mid}.main")
    assert hasattr(module, "run")
    result = module.run({"test": True})
    assert result["status"] == "not_implemented"
    assert result["module"] == mid


def test_logger_writes_file():
    from utils.logger import get_module_logger, log_error
    logger = get_module_logger("TEST_SMOKE")
    log_error(logger, "测试错误信息")
    log_path = ROOT / "logs" / "test_smoke.log"
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "Error: 测试错误信息" in content
    assert "[TEST_SMOKE]" in content


def test_create_app():
    from master import create_app
    app = create_app()
    routes = [r.path for r in app.routes]
    assert "/api/system/health" in routes
    assert "/api/system/modules" in routes
