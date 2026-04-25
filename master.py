"""
master.py — FurniQuote AI 总控入口

职责（按 CLAUDE.md RULE 5）：
  1. 启动检查清单（RULE 8 + RULE 10.5 共 13 项）
  2. 加载 config.yaml 统一配置
  3. 从 macOS Keychain 注入密钥
  4. 注册所有启用模块的路由
  5. 启动 FastAPI / uvicorn 服务

直接运行：python master.py
推荐运行：./start.sh （会先从 Keychain 注入密钥）
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent

# 把项目根加入 PYTHONPATH 以便 from utils / from schemas / from modules 导入
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.logger import get_module_logger, log_error, log_input, log_output  # noqa: E402
from utils.secrets import load_from_keychain, mask_secret  # noqa: E402

logger = get_module_logger("MASTER")
CONFIG_PATH = ROOT / "config.yaml"


# ============================================================
# 启动检查清单（RULE 8 + RULE 10.5）
# ============================================================
def run_startup_checks() -> list[tuple[str, bool, str]]:
    """运行 13 项启动检查。返回 [(检查项, 是否通过, 详情)]。"""
    checks: list[tuple[str, bool, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok, detail))

    # RULE 8 - 1: master.py 存在
    add("总控模块 master.py", (ROOT / "master.py").exists())

    # RULE 8 - 2: config.yaml 存在
    add("配置文件 config.yaml", CONFIG_PATH.exists())

    # RULE 8 - 3: schemas 存在
    add("全局 Schema 目录", (ROOT / "schemas" / "__init__.py").exists())

    # RULE 8 - 4: tests/ 存在
    add("测试目录 tests/", (ROOT / "tests").exists())

    # RULE 8 - 5: 各模块 test_data
    modules_dir = ROOT / "modules"
    if modules_dir.exists():
        module_dirs = [
            p for p in modules_dir.iterdir()
            if p.is_dir() and p.name.startswith("m") and not p.name.startswith("__")
        ]
        missing = [p.name for p in module_dirs if not (p / "test_data").exists()]
        add(
            "各模块 test_data/",
            not missing,
            f"缺失: {missing}" if missing else f"全部 {len(module_dirs)} 个模块就绪",
        )
    else:
        add("各模块 test_data/", False, "modules/ 目录不存在")

    # RULE 8 - 6: logs/ 存在
    add("日志目录 logs/", (ROOT / "logs").exists())

    # RULE 8 - 7: utils/logger.py 存在
    add("统一日志 utils/logger.py", (ROOT / "utils" / "logger.py").exists())

    # RULE 8 - 8: 测试 Dashboard
    add("测试 Dashboard", (ROOT / "tests" / "test_ui" / "index.html").exists())

    # RULE 10.5 - 9: .gitignore 存在
    add(".gitignore", (ROOT / ".gitignore").exists())

    # RULE 10.5 - 10: .gitignore 含 .env
    gi = ROOT / ".gitignore"
    if gi.exists():
        gi_text = gi.read_text(encoding="utf-8")
        add(".gitignore 含 .env", ".env" in gi_text)
    else:
        add(".gitignore 含 .env", False, ".gitignore 不存在")

    # RULE 10.5 - 11: .env.example 存在
    add(".env.example 模板", (ROOT / ".env.example").exists())

    # RULE 10.5 - 12: 代码无明显硬编码密钥（粗扫）
    suspicious = _scan_hardcoded_secrets()
    add("代码无硬编码密钥", not suspicious, f"可疑位置: {suspicious[:3]}" if suspicious else "")

    # RULE 10.5 - 13: .env 未被 git 追踪
    add(
        ".env 未被 git 追踪",
        not (ROOT / ".env").exists() or _is_gitignored(".env"),
    )

    return checks


def _scan_hardcoded_secrets() -> list[str]:
    """粗略扫描代码中的疑似密钥字符串（以 sk- 开头 + 长度>=20）。"""
    import re

    pattern = re.compile(r"sk-[a-zA-Z0-9_\-]{20,}")
    matches: list[str] = []
    skip_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", "logs"}
    skip_files = {".env.example", "master.py"}  # master.py 自身定义此正则会误报

    for path in ROOT.rglob("*.py"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.name in skip_files:
            continue
        try:
            text = path.read_text(encoding="utf-8")
            if pattern.search(text):
                matches.append(str(path.relative_to(ROOT)))
        except (UnicodeDecodeError, OSError):
            continue
    return matches


def _is_gitignored(path: str) -> bool:
    """检查路径是否被 .gitignore 覆盖。"""
    import subprocess
    try:
        subprocess.check_output(
            ["git", "check-ignore", path],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def print_check_report(checks: list[tuple[str, bool, str]]) -> int:
    """打印检查报告，返回失败数。"""
    logger.info("=" * 60)
    logger.info("启动检查清单（CLAUDE.md RULE 8 + RULE 10.5）")
    logger.info("=" * 60)
    failed = 0
    for idx, (name, ok, detail) in enumerate(checks, start=1):
        mark = "✓" if ok else "✗"
        line = f"  [{mark}] {idx:2d}. {name}"
        if detail:
            line += f"  — {detail}"
        if ok:
            logger.info(line)
        else:
            log_error(logger, line)
            failed += 1
    logger.info("=" * 60)
    if failed:
        log_error(logger, f"启动检查发现 {failed} 项问题，请修正")
    else:
        logger.info("✓ 全部 %d 项启动检查通过", len(checks))
    return failed


# ============================================================
# 配置加载
# ============================================================
def load_config() -> dict[str, Any]:
    """读取 config.yaml。"""
    if not CONFIG_PATH.exists():
        log_error(logger, f"配置文件不存在: {CONFIG_PATH}")
        sys.exit(1)
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# ============================================================
# 密钥注入
# ============================================================
def inject_secrets(config: dict[str, Any]) -> None:
    """从 Keychain 加载 config.secrets 列出的密钥到环境变量。"""
    required = config.get("secrets", {}).get("required", []) or []
    optional = config.get("secrets", {}).get("optional", []) or []
    all_keys = required + optional

    if not all_keys:
        logger.info("config.secrets 未列出密钥，跳过 Keychain 注入")
        return

    log_input(logger, {"action": "load_keychain", "keys": all_keys})
    result = load_from_keychain(all_keys)

    missing_required = [k for k in required if not result.get(k) and not os.environ.get(k)]
    if missing_required:
        log_error(
            logger,
            f"必需密钥未配置: {missing_required}，"
            f"请运行 security add-generic-password 或在 .env 中设置",
        )
    log_output(logger, {k: mask_secret(os.environ.get(k)) for k in all_keys if os.environ.get(k)})


# ============================================================
# FastAPI 应用工厂
# ============================================================
def create_app() -> "FastAPI":  # type: ignore[name-defined]
    """构建 FastAPI 应用并注册所有模块。"""
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles

    config = load_config()

    app = FastAPI(
        title=config.get("app", {}).get("name", "FurniQuote AI"),
        version=config.get("app", {}).get("version", "0.1.0"),
        debug=config.get("app", {}).get("debug", False),
    )

    # 注册所有模块路由
    from api_gateway import register_all
    register_all(app, config)

    # 静态测试 Dashboard
    test_ui_dir = ROOT / "tests" / "test_ui"
    if test_ui_dir.exists():
        app.mount("/test", StaticFiles(directory=str(test_ui_dir), html=True), name="test_ui")
        logger.info("测试 Dashboard 已挂载: /test")

    return app


# ============================================================
# 入口
# ============================================================
def main() -> None:
    logger.info("FurniQuote AI 启动中...")

    # 1. 启动检查
    checks = run_startup_checks()
    failed = print_check_report(checks)
    if failed and "--strict" in sys.argv:
        log_error(logger, "--strict 模式下检查未通过，拒绝启动")
        sys.exit(1)

    # 2. 加载配置
    config = load_config()
    logger.info("配置已加载: %s v%s (env=%s)",
                config.get("app", {}).get("name"),
                config.get("app", {}).get("version"),
                config.get("app", {}).get("env"))

    # 3. 注入密钥
    inject_secrets(config)

    # 4. 构建并启动 FastAPI
    app = create_app()
    host = config.get("app", {}).get("host", "0.0.0.0")
    port = config.get("app", {}).get("port", 8000)

    try:
        import uvicorn
    except ImportError:
        log_error(logger, "未安装 uvicorn，运行 pip install -r requirements.txt")
        sys.exit(1)

    logger.info("启动 uvicorn 服务: http://%s:%d", host, port)
    logger.info("API 文档: http://localhost:%d/docs", port)
    logger.info("测试 Dashboard: http://localhost:%d/test", port)
    uvicorn.run(app, host=host, port=port, log_config=None)


if __name__ == "__main__":
    main()
