"""
密钥工具（按 CLAUDE.md RULE 10）

- load_from_keychain: 从 macOS Keychain 读取密钥并注入环境变量
- mask_secret: 输出脱敏字符串（前4位 + ... + 后4位）
"""
from __future__ import annotations

import os
import subprocess
from typing import Iterable

from utils.logger import get_module_logger, log_error

_KEYCHAIN_ACCOUNT_DEFAULT = "leslie"
_logger = get_module_logger("SECRETS")


def mask_secret(value: str | None) -> str:
    """日志脱敏：返回 'sk-a...x123' 格式。空值返回 '***'。"""
    if not value or len(value) < 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def load_from_keychain(
    keys: Iterable[str],
    account: str = _KEYCHAIN_ACCOUNT_DEFAULT,
) -> dict[str, bool]:
    """从 macOS Keychain 读取密钥并 export 到 os.environ。

    返回 {key: 是否成功加载} 的字典，不抛异常，由调用方决定是否阻塞启动。
    """
    result: dict[str, bool] = {}
    for key in keys:
        try:
            value = subprocess.check_output(
                ["security", "find-generic-password", "-a", account, "-s", key, "-w"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
            if value:
                os.environ[key] = value
                _logger.info("已加载密钥 %s = %s", key, mask_secret(value))
                result[key] = True
            else:
                result[key] = False
        except subprocess.CalledProcessError:
            result[key] = False
        except FileNotFoundError:
            log_error(_logger, "未找到 security 命令，仅 macOS 支持 Keychain 注入")
            result[key] = False
            break
    return result
