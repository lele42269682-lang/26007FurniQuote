"""
m21_bug_report · Bug上报系统
优先级：P1
说明：🐞 客户/业务员/自动测试一键上报入口（自动收集上下文+联动钉钉）

骨架阶段——尚未实现业务逻辑。开发时遵循 CLAUDE.md RULE 5/6/7。
"""
from __future__ import annotations

from utils.logger import get_module_logger, log_error, log_input, log_output
from utils.isolation import isolated

logger = get_module_logger("M21_BUG_REPORT")



@isolated(module_id="m21_bug_report")
def run(payload: dict) -> dict:
    """模块入口（占位）。"""
    log_input(logger, payload)
    log_error(logger, "模块 m21_bug_report 尚未实现，仅占位")
    result = {"status": "not_implemented", "module": "m21_bug_report"}
    log_output(logger, result)
    return result


if __name__ == "__main__":
    import json
    sample_path = "modules/m21_bug_report/test_data/sample_input.json"
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            sample = json.load(f)
        out = run(sample)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    except FileNotFoundError:
        logger.warning("未找到测试数据 %s", sample_path)
