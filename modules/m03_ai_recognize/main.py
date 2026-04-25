"""
m03_ai_recognize · AI视觉识别
优先级：P1
说明：百炼 qwen3-vl-plus 识别家具雕花/材质/工艺

骨架阶段——尚未实现业务逻辑。开发时遵循 CLAUDE.md RULE 5/6/7：
  - 输入输出经过 schemas/ 全局 Schema 验证
  - 通过 utils.logger 记录 INPUT/OUTPUT/Error
  - 提供 if __name__ 自测入口（热拔插要求）
  - 测试数据放在 test_data/
"""
from __future__ import annotations

from utils.logger import get_module_logger, log_error, log_input, log_output

logger = get_module_logger("M03_AI_RECOGNIZE")


def run(payload: dict) -> dict:
    """模块入口（占位）。开发时替换为实际业务逻辑。"""
    log_input(logger, payload)
    log_error(logger, "模块 m03_ai_recognize 尚未实现，仅占位")
    result = {"status": "not_implemented", "module": "m03_ai_recognize"}
    log_output(logger, result)
    return result


if __name__ == "__main__":
    # 自测入口（热拔插验证）
    import json
    sample_path = "modules/m03_ai_recognize/test_data/sample_input.json"
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            sample = json.load(f)
        out = run(sample)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    except FileNotFoundError:
        logger.warning("未找到测试数据 %s", sample_path)
