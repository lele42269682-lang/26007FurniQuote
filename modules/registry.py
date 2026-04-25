"""
模块注册中心 — 21 个模块的元数据中心

用途：
  - 列出全部模块（id / 名称 / 优先级 / 依赖图）
  - 检查模块状态（已启用 / 可加载 / 健康）
  - 提供按需加载入口（避免顶层全量 import 造成单点失败牵连）

模块间通讯原则（"分与合"）：
  ❌ 禁止：modules.m10_pricing 直接 from modules.m15_customer import ...
  ✅ 推荐：通过 utils.isolation.call_module("m15_customer", payload) 调用
  ✅ 推荐：通过 schemas/ 共享数据契约，不直接共享代码
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from utils.isolation import safe_import_module
from utils.logger import get_module_logger

_logger = get_module_logger("REGISTRY")


@dataclass
class ModuleMeta:
    """单个模块的注册元数据"""
    id: str
    name: str
    priority: str            # P0 / P1 / P2
    description: str
    depends_on: list[str] = field(default_factory=list)   # 依赖的其他模块ID
    soft_depends: list[str] = field(default_factory=list) # 软依赖（缺失时降级而非阻塞）


# 21 个模块的元数据快照（"分与合"关系图）
# 注意：依赖只声明数据/逻辑层依赖，不在代码顶层 import；运行时通过 call_module() 调用
MODULES: dict[str, ModuleMeta] = {
    "m01_auth":          ModuleMeta("m01_auth",          "认证",            "P1", "用户登录/Token/权限"),
    "m02_folder":        ModuleMeta("m02_folder",        "文件夹管理",      "P1", "图片资料组织"),
    "m03_ai_recognize":  ModuleMeta("m03_ai_recognize",  "AI视觉识别",      "P1", "qwen3-vl-plus 识别家具", soft_depends=["m09_prompt"]),
    "m04_annotation":    ModuleMeta("m04_annotation",    "标注",            "P1", "标注训练数据"),
    "m05_expert":        ModuleMeta("m05_expert",        "专家审核",        "P1", "AI识别人工校正", soft_depends=["m03_ai_recognize"]),
    "m06_material":      ModuleMeta("m06_material",      "材质库",          "P0", "5类样板材质库"),
    "m07_dict":          ModuleMeta("m07_dict",          "词典",            "P1", "行业术语词典"),
    "m08_stats":         ModuleMeta("m08_stats",         "统计与RAG",       "P1", "ChromaDB 历史检索"),
    "m09_prompt":        ModuleMeta("m09_prompt",        "Prompt管理",      "P1", "AI 模板管理"),
    "m10_pricing":       ModuleMeta(
        "m10_pricing",       "报价引擎",        "P0", "🔴 五维定价矩阵",
        depends_on=[],   # 无硬依赖
        soft_depends=["m15_customer", "m08_stats"],  # 缺失时用默认参数降级
    ),
    "m11_3d_modeling":   ModuleMeta("m11_3d_modeling",   "混元3D",          "P0", "🔴 图片→GLB"),
    "m12_3d_material":   ModuleMeta(
        "m12_3d_material",   "Seedream材质换图","P0", "🔴 材质高清渲染",
        soft_depends=["m11_3d_modeling", "m06_material"],
    ),
    "m13_3d_viewer":     ModuleMeta(
        "m13_3d_viewer",     "Three.js查看器",  "P0", "🔴 浏览器3D",
        soft_depends=["m11_3d_modeling", "m12_3d_material"],
    ),
    "m14_quote_doc":     ModuleMeta(
        "m14_quote_doc",     "报价单生成",      "P1", "PDF/Excel三语",
        soft_depends=["m10_pricing", "m12_3d_material"],
    ),
    "m15_customer":      ModuleMeta("m15_customer",      "客户档案",        "P0", "🔴 客户分级管理"),
    "m16_workflow":      ModuleMeta(
        "m16_workflow",      "业务流程引擎",    "P1", "14步状态机",
        soft_depends=["m10_pricing", "m14_quote_doc", "m17_dingtalk"],
    ),
    "m17_dingtalk":      ModuleMeta("m17_dingtalk",      "钉钉集成",        "P1", "通知+审批"),
    "m18_portal":        ModuleMeta(
        "m18_portal",        "客户门户",        "P2", "海外客户自助",
        soft_depends=["m13_3d_viewer", "m19_security", "m15_customer"],
    ),
    "m19_security":      ModuleMeta("m19_security",      "安全防泄露",      "P1", "水印+OTP"),
    "m20_bug_tracking":  ModuleMeta("m20_bug_tracking",  "Bug记录管理",     "P1", "🐞 全生命周期"),
    "m21_bug_report":    ModuleMeta(
        "m21_bug_report",    "Bug上报系统",     "P1", "🐞 一键上报",
        soft_depends=["m20_bug_tracking", "m17_dingtalk"],
    ),
}


def list_modules() -> list[ModuleMeta]:
    """返回全部模块元数据。"""
    return list(MODULES.values())


def get_meta(module_id: str) -> ModuleMeta | None:
    """获取单个模块元数据。"""
    return MODULES.get(module_id)


def health_check(module_id: str) -> dict[str, Any]:
    """检查单个模块是否可加载且具备 run() 入口（不实际执行业务）。"""
    meta = MODULES.get(module_id)
    if not meta:
        return {"id": module_id, "ok": False, "error": "模块未注册"}
    module = safe_import_module(f"modules.{module_id}.main")
    if module is None:
        return {"id": module_id, "ok": False, "error": "import 失败"}
    if not hasattr(module, "run"):
        return {"id": module_id, "ok": False, "error": "缺少 run() 入口"}
    return {"id": module_id, "ok": True, "name": meta.name, "priority": meta.priority}


def health_check_all() -> list[dict[str, Any]]:
    """对全部 21 个模块做健康检查。单个失败不影响其他模块。"""
    return [health_check(mid) for mid in MODULES]
