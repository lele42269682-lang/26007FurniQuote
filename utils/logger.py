"""
统一日志工具（按 CLAUDE.md RULE 7）

强制格式：[YYYY-MM-DD HH:MM:SS] [MODULE_NAME] message
错误行自动补 "Error: " 前缀。
每个模块独立日志文件 logs/module_xx.log，总日志 logs/master.log。
"""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_FORMAT = "[%(asctime)s] [%(name)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_loggers: dict[str, logging.Logger] = {}


def get_module_logger(module_name: str, level: str = "INFO") -> logging.Logger:
    """获取模块专属 Logger。

    自动配置控制台输出 + 文件输出（logs/{module_name}.log）。
    重复调用同名模块返回同一实例。
    """
    if module_name in _loggers:
        return _loggers[module_name]

    logger = logging.getLogger(module_name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    formatter = logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    safe_name = module_name.lower().replace(" ", "_")
    file_handler = RotatingFileHandler(
        LOG_DIR / f"{safe_name}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _loggers[module_name] = logger
    return logger


def log_input(logger: logging.Logger, data: Any) -> None:
    """记录模块输入。"""
    logger.info("INPUT: %s", data)


def log_output(logger: logging.Logger, data: Any) -> None:
    """记录模块输出。"""
    logger.info("OUTPUT: %s", data)


def log_error(logger: logging.Logger, message: str) -> None:
    """记录错误（自动补 "Error: " 前缀）。"""
    if not message.startswith("Error:"):
        message = f"Error: {message}"
    logger.error(message)
