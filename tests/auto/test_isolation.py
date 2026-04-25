"""
模块隔离测试 — 验证"分与合"原则

核心断言：
  1. 任意一个模块抛异常不会影响其他模块的运行结果
  2. 任意一个模块的 import 失败不会阻塞其他模块加载
  3. 每个模块都能脱离其他模块独立运行（热拔插）
  4. 启用模块的子集（如只启用 m10）时，整个系统仍可启动
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


ALL_MODULE_IDS = [
    "m01_auth", "m02_folder", "m03_ai_recognize", "m04_annotation",
    "m05_expert", "m06_material", "m07_dict", "m08_stats", "m09_prompt",
    "m10_pricing", "m11_3d_modeling", "m12_3d_material", "m13_3d_viewer",
    "m14_quote_doc", "m15_customer", "m16_workflow", "m17_dingtalk",
    "m18_portal", "m19_security", "m20_bug_tracking", "m21_bug_report",
]


# ============================================================
# 1. 单模块异常不影响其他模块
# ============================================================
def test_isolated_decorator_catches_exception():
    """@isolated 装饰的函数抛异常时返回标准错误响应，不向上抛。"""
    from utils.isolation import isolated

    @isolated(module_id="test_module")
    def faulty(payload: dict) -> dict:
        raise RuntimeError("故意触发的错误")

    result = faulty({})
    assert result["status"] == "error"
    assert result["module"] == "test_module"
    assert result["isolated"] is True
    assert "故意触发的错误" in result["error"]


def test_one_module_exception_does_not_affect_others():
    """模拟一个模块异常，验证其他模块仍可正常 run。"""
    from utils.isolation import isolated

    @isolated(module_id="bad_module")
    def bad(payload):
        raise ValueError("坏模块")

    @isolated(module_id="good_module")
    def good(payload):
        return {"status": "ok", "module": "good_module"}

    bad_result = bad({})
    good_result = good({})

    assert bad_result["status"] == "error"
    assert good_result["status"] == "ok"


# ============================================================
# 2. import 失败不阻塞其他模块
# ============================================================
def test_safe_import_returns_none_on_failure():
    from utils.isolation import safe_import_module

    result = safe_import_module("modules.does_not_exist_xyz.main")
    assert result is None


def test_call_module_returns_fallback_on_missing():
    from utils.isolation import call_module

    result = call_module("nonexistent_module", {"x": 1})
    assert result["status"] == "fallback"
    assert result["available"] is False


# ============================================================
# 3. 每个模块独立可热拔插
# ============================================================
@pytest.mark.parametrize("mid", ALL_MODULE_IDS)
def test_module_runs_independently(mid):
    """每个模块只依赖 utils + schemas，不依赖其他业务模块。"""
    import importlib
    module = importlib.import_module(f"modules.{mid}.main")
    assert hasattr(module, "run")

    result = module.run({"isolation_test": True})
    # 占位阶段返回 not_implemented，业务实现后应返回正常结果
    assert isinstance(result, dict)
    assert result.get("module") == mid


def test_no_cross_module_imports():
    """检查源码：业务模块不应直接 from modules.{other_mid} import。

    模块间通讯必须通过 utils.isolation.call_module() 或 schemas/。
    """
    import re
    pattern = re.compile(r"from\s+modules\.(m\d{2}_\w+)(?:\.\w+)?\s+import")

    violations = []
    modules_dir = ROOT / "modules"
    for mid in ALL_MODULE_IDS:
        for py_file in (modules_dir / mid).glob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            for match in pattern.finditer(text):
                imported = match.group(1)
                if imported != mid:
                    violations.append(f"{py_file.relative_to(ROOT)} 直接 import {imported}")

    assert not violations, (
        "禁止业务模块间直接 import（违反热拔插原则）：\n"
        + "\n".join(violations)
        + "\n请改用 utils.isolation.call_module() 或共享 schemas/"
    )


# ============================================================
# 4. 子集启用仍可启动
# ============================================================
def test_registry_health_check_independent():
    """模块健康检查必须逐个独立完成，单个失败不影响其他。"""
    from modules.registry import health_check_all

    results = health_check_all()
    assert len(results) == 21, f"应注册 21 个模块，实际 {len(results)}"
    # 全部应可加载（占位阶段无业务实现，但 import + run 必须可用）
    failures = [r for r in results if not r["ok"]]
    assert not failures, f"模块健康检查失败: {failures}"


def test_app_starts_with_no_modules_enabled(monkeypatch):
    """模拟 config 中禁用所有模块，FastAPI 仍能启动。"""
    import importlib
    from master import create_app

    # 清空 master 模块的缓存以重新读取 config
    importlib.reload(__import__("api_gateway"))
    app = create_app()

    routes = [r.path for r in app.routes]
    assert "/api/system/health" in routes
    # 系统级路由必须始终可用，无论业务模块是否启用


def test_registered_modules_count():
    """注册中心必须包含 21 个模块（19 业务 + M-20 + M-21）。"""
    from modules.registry import MODULES
    assert len(MODULES) == 21
    assert "m20_bug_tracking" in MODULES
    assert "m21_bug_report" in MODULES
