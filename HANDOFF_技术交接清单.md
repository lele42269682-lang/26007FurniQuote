# FurniQuote AI · 外包团队技术交接清单

> 交付时间：2026-04-25
> 适用对象：接手开发的外包团队（前端 / 后端 / AI 工程师 / 测试）
> 阅读顺序建议：第一章（项目定位）→ 第二章（已完成工作）→ 第七章（外包待办清单）→ 其余按需查阅

---

## 第一章 项目定位与铁律

### 1.1 项目一句话

法式古典家具出口企业的 **AI 辅助报价中枢**——客户随手发一张图，24 小时内输出专业三语报价单。

### 1.2 三个不可妥协的原则（**外包团队必须遵守**）

| 原则 | 含义 | 落地约束 |
|---|---|---|
| **定价权完全在公司** | AI 只输出建议，最终价格由人决定 | M-10 报价引擎只产出 `suggested_price`，前端不直接呈现给客户 |
| **核心数据绝不外泄** | 服务器+数据库部署在国内自家服务器 | 不允许使用境外云数据库 / 境外日志服务 |
| **客户看不到任何定价逻辑** | 五维系数全程对客户隐藏 | M-18 客户门户的 API 响应不允许出现 `breakdown` 字段 |

### 1.3 商业敏感约束

- 客户专有产品（`is_proprietary=true`）**禁止上云**——M-11/M-12 在调用前必须先检查此字段，违反此约束直接拒收交付。
- 所有密钥仅通过 **macOS Keychain** 注入，**严禁**写入代码、`.env` 不得入库（已在 `.gitignore` 强制）。

---

## 第二章 已完成工作清单（截至 2026-04-25）

### 2.1 工程基础设施（100% 完成）

| 类目 | 完成项 | 验证方式 |
|---|---|---|
| 总控入口 | `master.py` 281 行（13 项启动检查 + 配置加载 + 密钥注入 + FastAPI 工厂） | `python3 master.py` |
| 统一配置 | `config.yaml` 173 行（含五维定价系数 + 21 模块开关 + Bug + Testing） | `pytest tests/auto/test_smoke.py::test_config_yaml_loadable` |
| API 网关 | `api_gateway.py` 单点容错路由注册，提供 `/api/system/*` 系统级路由 | `curl http://localhost:8000/api/system/health` |
| 统一日志 | `utils/logger.py` 强制格式 `[YYYY-MM-DD HH:MM:SS] [MODULE] msg`，错误自动补 `Error: ` 前缀 | `tail logs/master.log` |
| Keychain 密钥 | `utils/secrets.py` 提供 `load_from_keychain` / `mask_secret` | `./start.sh` |
| 启动脚本 | `start.sh` 从 Keychain 注入密钥后启动 master.py | `./start.sh` |

### 2.2 「分与合」隔离层（100% 完成）

| 文件 | 作用 | 关键 API |
|---|---|---|
| `utils/isolation.py` | 模块异常隔离 + 自动 Bug 上报联动 | `@isolated(module_id)` / `safe_import_module()` / `call_module(id, payload, fallback)` |
| `modules/registry.py` | 21 模块元数据中心 + 健康检查 | `MODULES` / `list_modules()` / `health_check_all()` |
| `api_gateway.py` | 单模块路由注册失败仅记 Error 不阻塞启动 | `register_all(app, config)` |

**核心契约**：任何业务模块的 `run()` 入口都必须用 `@isolated(module_id="mXX_xxx")` 装饰；模块间禁止直接 `from modules.mXX import ...`，必须走 `call_module()`。

### 2.3 全局 Schema（100% 完成）

定义在 `schemas/` 目录，使用 Pydantic 2.x：

- `schemas/common.py` — `CustomerTier` (L1-L5) / `PriceAcceptance` (A/B/C) / `RegionCode` (10 国) / `ProductCategory` (5 类)
- `schemas/customer.py` — `Customer` / `CustomerCreate`
- `schemas/product.py` — `Product` / `ProductLifecycleStage` (8 阶段)
- `schemas/pricing.py` — `PricingRequest` / `PricingResponse` / `PricingBreakdown` / `HistoricalReference`
- `schemas/quote.py` — `Quote` / `QuoteVersion` / `QuoteStatus` (7 态)
- `schemas/bug.py` — `Bug` / `BugReportInput` / `BugSeverity` / `BugStatus` / `BugSource`

### 2.4 21 个模块占位（100% 骨架，0% 业务实现）

每个模块统一目录结构：
```
modules/mXX_xxx/
├── __init__.py
├── main.py        ← @isolated 装饰的 run() 占位入口
├── schema.py      ← 引用 schemas/ 全局类型 + 模块本地输入输出
├── README.md      ← 模块自检清单
└── test_data/
    ├── sample_input.json
    └── expected_output.json
```

所有 21 个模块的 `run()` 占位均已通过烟囱测试与隔离测试。

### 2.5 三层测试体系（100% 完成）

| 层 | 路径 | 状态 |
|---|---|---|
| 自动化测试 | `tests/auto/test_smoke.py` (25 项) + `test_isolation.py` (31 项) | **56/56 通过** |
| 手工测试 | `tests/manual/README.md` 总指引 | 模板就绪 |
| 测试 Dashboard | `tests/test_ui/index.html` 21 模块卡片 + 实时日志 | 可访问 `/test` |

### 2.6 CI/CD 与质量门槛（100% 完成）

- `.github/workflows/test.yml` — Python 3.11/3.12 矩阵 + 覆盖率门槛 70%
- `.pre-commit-config.yaml` — pytest-smoke + pytest-isolation + 密钥扫描
- `.gitignore` — 强制屏蔽 `.env` / 密钥文件 / 日志
- `.env.example` — 列出 9 个密钥变量名（不含值）

### 2.7 Git 提交记录

| Commit | 内容 |
|---|---|
| `cb39ec6` | init: 项目骨架按 CLAUDE.md v1.2 规范搭建（19 模块占位 + 总控 + 三层测试） |
| `7d1e245` | feat: 新增 M-20/M-21 Bug 模块 + 模块隔离热拔插体系 + CI/pre-commit |

---

## 第三章 项目目录架构（全量）

```
26007FurniQuote/
├── 📄 README.md                           项目总览（中文）
├── 📄 CLAUDE.md                           项目级工程规范
├── 📄 AGENTS.md                           Codex Agent 工程规范
├── 📄 HANDOFF_技术交接清单.md             ← 本文档
├── 📄 PM_产品规划书.md                    ← 配套产品经理视角文档
├── 📄 家具报价系统_需求分析文档_v5.0_最终版.md   业务规则真相源（58 题）
├── 📄 FurniQuote_编码就绪规划书_v6.0.md   19 模块拆分 + Schema + 优先级
│
├── ⚙️ master.py                           总控入口（启动检查 + FastAPI）
├── ⚙️ config.yaml                         统一配置（含五维定价系数）
├── ⚙️ api_gateway.py                      前后台接口统一层
├── ⚙️ start.sh                            Keychain 注入 + 启动
├── ⚙️ requirements.txt                    Python 依赖
│
├── 🛡️ .gitignore                          密钥/日志/缓存屏蔽
├── 🛡️ .env.example                        密钥变量名模板
├── 🛡️ .pre-commit-config.yaml             提交前钩子
├── 🛡️ .github/workflows/test.yml          GitHub Actions CI
│
├── schemas/                               ← 全局 I/O Schema（Pydantic 2.x）
│   ├── __init__.py
│   ├── common.py                          通用枚举（5 个）
│   ├── customer.py                        客户档案
│   ├── product.py                         产品档案 + 生命周期
│   ├── pricing.py                         报价请求/响应/明细
│   ├── quote.py                           报价单 + 版本
│   └── bug.py                             Bug + 上报输入
│
├── modules/                               ← 21 个热拔插模块
│   ├── registry.py                        模块元数据中心 + 健康检查
│   ├── m01_auth/                          P1 · 认证（占位）
│   ├── m02_folder/                        P1 · 文件夹管理（占位）
│   ├── m03_ai_recognize/                  P1 · AI 视觉识别（占位）
│   ├── m04_annotation/                    P1 · 标注（工具A已有）
│   ├── m05_expert/                        P1 · 专家审核（占位）
│   ├── m06_material/                      🔴 P0 · 材质库（占位）
│   ├── m07_dict/                          P1 · 词典（占位）
│   ├── m08_stats/                         P1 · 统计/RAG（占位）
│   ├── m09_prompt/                        P1 · Prompt 管理（占位）
│   ├── m10_pricing/                       🔴 P0 · 报价引擎（占位）
│   ├── m11_3d_modeling/                   🔴 P0 · 混元 3D（占位）
│   ├── m12_3d_material/                   🔴 P0 · Seedream 材质（占位）
│   ├── m13_3d_viewer/                     🔴 P0 · Three.js 查看器（占位）
│   ├── m14_quote_doc/                     P1 · 报价单生成（占位）
│   ├── m15_customer/                      🔴 P0 · 客户档案（占位）
│   ├── m16_workflow/                      P1 · 业务流程引擎（占位）
│   ├── m17_dingtalk/                      P1 · 钉钉集成（占位）
│   ├── m18_portal/                        P2 · 客户门户（占位）
│   ├── m19_security/                      P1 · 安全防泄露（占位）
│   ├── m20_bug_tracking/                  🐞 P1 · Bug 记录（占位，开发期启用）
│   └── m21_bug_report/                    🐞 P1 · Bug 上报（占位，开发期启用）
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                          统一日志工具
│   ├── secrets.py                         Keychain 读取 + 脱敏
│   └── isolation.py                       @isolated / safe_import / call_module
│
├── tests/
│   ├── README.md                          测试体系说明
│   ├── auto/
│   │   ├── test_smoke.py                  25 项烟囱测试
│   │   └── test_isolation.py              31 项隔离测试
│   ├── manual/README.md                   手工测试模板
│   └── test_ui/index.html                 21 卡片 Dashboard
│
└── logs/                                  日志输出（gitignore）
```

---

## 第四章 关键 API 与函数签名（外包必读）

### 4.1 总控层（master.py）

```python
# 启动检查（13 项）
def run_startup_checks() -> list[tuple[str, bool, str]]:
    """返回 [(检查项名, 是否通过, 详情)]"""

# 配置加载
def load_config() -> dict[str, Any]:
    """读取 config.yaml"""

# 密钥注入
def inject_secrets(config: dict[str, Any]) -> None:
    """从 Keychain 加载 config.secrets.required + optional 列出的密钥到 env"""

# FastAPI 应用工厂
def create_app() -> FastAPI:
    """构建并注册所有启用模块的路由"""

# 程序入口
def main() -> None:
    """启动检查 → 加载配置 → 注入密钥 → uvicorn run"""
```

### 4.2 隔离层（utils/isolation.py）— **每个模块必须使用**

```python
# 装饰器 — 每个模块的 run() 必须套
@isolated(module_id: str) -> Callable
# 失败时返回 {"status":"error","module":<id>,"error":<msg>,"isolated":true}
# 自动调用 m21_bug_report 建 Bug

# 安全导入
def safe_import_module(dotted_path: str) -> Any | None:
    """import 失败返回 None，不阻塞调用方"""

# 跨模块调用（业务模块间通讯唯一入口）
def call_module(module_id: str, payload: dict, fallback: dict | None = None) -> dict:
    """目标模块未启用/不存在/抛异常时返回 fallback"""
```

### 4.3 注册中心（modules/registry.py）

```python
@dataclass
class ModuleMeta:
    id: str
    name: str
    priority: str            # "P0" / "P1" / "P2"
    description: str
    depends_on: list[str]    # 硬依赖（缺失则报错）
    soft_depends: list[str]  # 软依赖（缺失则降级）

MODULES: dict[str, ModuleMeta]   # 21 个模块的全量元数据
def list_modules() -> list[ModuleMeta]
def get_meta(module_id: str) -> ModuleMeta | None
def health_check(module_id: str) -> dict
def health_check_all() -> list[dict]
```

### 4.4 日志层（utils/logger.py）

```python
def get_module_logger(module_name: str, level: str = "INFO") -> logging.Logger:
    """单例，自动配置 console + RotatingFileHandler(10MB×5)"""

def log_input(logger, data) -> None:    # logs "INPUT: {data}"
def log_output(logger, data) -> None:   # logs "OUTPUT: {data}"
def log_error(logger, message) -> None: # 自动补 "Error: " 前缀
```

### 4.5 系统级路由（api_gateway.py，已实现）

| 路由 | 方法 | 返回 |
|---|---|---|
| `/api/system/health` | GET | `{"status":"ok","app":"FurniQuote AI"}` |
| `/api/system/modules` | GET | 21 模块清单（id/name/priority/enabled/depends_on/soft_depends） |
| `/api/system/modules/health` | GET | 逐模块健康检查 `{ok_count, total, details}` |
| `/api/system/config` | GET | 脱敏配置（剥离 secrets） |

### 4.6 业务模块统一入口约定

每个 `modules/mXX_xxx/main.py` 必须导出：

```python
@isolated(module_id="mXX_xxx")
def run(payload: dict) -> dict:
    """模块统一入口
    输入：dict（开发时用 schema.py 中本地 Schema 验证）
    输出：dict（成功时含 status/data，失败时由 @isolated 标准化）
    """

# 可选：FastAPI 路由
router = APIRouter()  # api_gateway 自动挂载到 /api/{mid}/*
```

---

## 第五章 21 模块详细规划

### 5.1 模块依赖关系图（"分与合"）

```
P0 核心链路（3D 配置器小组先做这条）：
  m15_customer ────┐
                   ├──> m10_pricing ──> m14_quote_doc
  m08_stats(RAG)──┘
  m11_3d_modeling ──> m12_3d_material ──> m13_3d_viewer ──> m18_portal
                              │
                              └──> m06_material（材质来源）

P1 配套：
  m01_auth ─→ 全部需登录的接口
  m03_ai_recognize ←─ m05_expert（人工校正）
  m09_prompt ─→ m03_ai_recognize（模板）
  m07_dict ─→ m03_ai_recognize / m14_quote_doc（术语翻译）
  m16_workflow（14 步状态机）─→ m17_dingtalk（通知 + 审批）

P1 横切（开发期就要用）：
  m20_bug_tracking ←─ m21_bug_report ←─ utils.isolation 自动联动

P1/P2 防护：
  m19_security（水印 + OTP + 设备指纹）─→ m18_portal
  m04_annotation（工具A已有，待迁移）
```

**约束**：所有依赖关系**只在 `modules/registry.py` 声明**，源码层禁止 `from modules.mXX import ...`，运行时一律用 `call_module()`。

### 5.2 模块清单与 I/O 摘要

> **完整 I/O 字段**请查阅 `schemas/*.py` 与各模块 `schema.py`。下表为外包估算工作量用的速览。

| ID | 名称 | 优先级 | 关键 I/O Schema | 主要外部依赖 | 估算人天（外包） |
|---|---|---|---|---|---|
| **m10_pricing** | 报价引擎 | 🔴 P0 | `PricingRequest` → `PricingResponse` | `config.pricing` 五维系数 + ChromaDB（RAG） | 8 |
| **m11_3d_modeling** | 混元 3D | 🔴 P0 | `{image_url, is_proprietary}` → `{glb_url, model_id}` | 腾讯混元3D API | 6 |
| **m12_3d_material** | Seedream 材质 | 🔴 P0 | `{model_id, material_id}` → `{rendered_image_url}` | Seedream 4.0 Edit API | 5 |
| **m13_3d_viewer** | Three.js 查看器 | 🔴 P0 | 前端模块，加载 GLB + 材质切换 | three.js / 浏览器 | 7 |
| **m15_customer** | 客户档案 | 🔴 P0 | `CustomerCreate` → `Customer` | SQLite/PostgreSQL | 4 |
| **m06_material** | 材质库 | 🔴 P0 | `{category}` → 材质列表 | 静态资源 + 数据库 | 3 |
| m01_auth | 认证 | P1 | 登录 → JWT | bcrypt + JWT | 3 |
| m02_folder | 文件夹管理 | P1 | 树状结构 CRUD | 文件系统 | 2 |
| m03_ai_recognize | AI 视觉识别 | P1 | `{image_url}` → `{features}` | 百炼 qwen3-vl-plus | 5 |
| m04_annotation | 标注 | P1 | （工具A已有，迁移） | — | 4（迁移） |
| m05_expert | 专家审核 | P1 | AI结果 + 修正 → 校正后特征 | — | 3 |
| m07_dict | 词典 | P1 | 行业术语中英印尼对照 | — | 2 |
| m08_stats | 统计/RAG | P1 | 历史报价向量化 + 相似检索 | ChromaDB + Embedding | 6 |
| m09_prompt | Prompt 管理 | P1 | Prompt 模板 CRUD + 版本 | — | 3 |
| m14_quote_doc | 报价单生成 | P1 | `Quote` → PDF/Excel(中英印) | reportlab / openpyxl | 6 |
| m16_workflow | 业务流程引擎 | P1 | 14 步状态机 | — | 5 |
| m17_dingtalk | 钉钉集成 | P1 | 通知 + 审批 + H5 | 钉钉 OpenAPI | 5 |
| m18_portal | 客户门户 | P2 | 海外客户自助 | M-13 + M-19 | 8 |
| m19_security | 安全防泄露 | P1 | 水印 + OTP + 设备指纹 | — | 5 |
| m20_bug_tracking | Bug 记录 | P1 | `Bug` CRUD + 列表 | 数据库 | 3 |
| m21_bug_report | Bug 上报 | P1 | `BugReportInput` → `Bug` | 联动 m20 + m17 | 2 |

**P0 总估算**：33 人天（核心链路，3D 配置器 + 报价引擎 + 客户档案 + 材质库）
**P1 总估算**：54 人天
**P2 总估算**：8 人天
**全部 21 模块**：约 95 人天（不含联调测试 + 回归 + 上线）

---

## 第六章 五维定价模型（核心业务规则，外包必读）

> **重要**：定价公式是产品核心壁垒，**禁止**修改 `config.yaml > pricing` 节点的系数；所有调整必须由产品经理书面授权。

### 6.1 公式

```
suggested_price_cny = base_price
                    × customer_tier_coef        # L1=1.0 / L2=1.2 / L3=1.55 / L4=1.0 / L5=锁价
                    × quantity_coef             # 1-2件×1.0 / 3-9×0.92 / 10-49×0.82 / 50-99×0.75 / 100+×0.68
                    × price_acceptance_coef     # A=1.15 / B=1.0 / C=0.925
                    × region_coef               # US/AE/SA=1.3 / AU=1.2 / RU/AM=1.1 / 其余=1.0
                    × exchange_rate_factor      # ±3% 阈值，超过自动预警
```

### 6.2 base_price 来源

通过 RAG（M-08）从历史报价库检索相似产品，取相似度 >= 0.8 的报价中位数作为锚点。

### 6.3 三种语言报价

- 中文版：CNY
- 英文版：USD（自动汇率换算）
- 印尼文版：USD（同英文版，不用 IDR 标价）

### 6.4 强制约束

- L5 客户：锁价协议，**禁止**自动调价，命中 L5 时返回 `confidence: "low"` + `warnings: ["L5 客户需人工询价"]`
- 汇率波动 > 3%：在 `PricingResponse.warnings` 加 `"exchange_rate_alert"` 并发送钉钉通知
- 报价仅给业务员看，**不允许**通过任何 API 把 `breakdown` 字段返回给客户门户

---

## 第七章 外包待办清单（按交付顺序）

### Sprint 1（建议第 1-2 周）：核心数据层

| 任务 | 文件 | 验收标准 |
|---|---|---|
| 1.1 实现 m15_customer CRUD | `modules/m15_customer/main.py` | API 通过 + 自动测试 + Customer Schema 验证 |
| 1.2 客户编号生成器 `C-{region}-{seq:03d}` | 同上 | 同一地区序号递增，多并发不冲突 |
| 1.3 SQLite 表结构 + 迁移脚本 | `data/schema.sql`（新建） | `master.py --strict` 启动通过 |
| 1.4 m06_material 材质 5 类基础 CRUD | `modules/m06_material/main.py` | 材质库 GET/POST/PUT 通过 |

### Sprint 2（建议第 3-4 周）：3D 配置器小组

| 任务 | 文件 | 验收标准 |
|---|---|---|
| 2.1 接入腾讯混元 3D | `modules/m11_3d_modeling/main.py` | 客户图片 → GLB 模型成功率 ≥ 80% |
| 2.2 客户专有产品检查闸门 | 同上 | `is_proprietary=true` 时拒绝调用云 API |
| 2.3 接入 Seedream 4.0 Edit | `modules/m12_3d_material/main.py` | 材质换图 3-5 秒/组 |
| 2.4 Three.js 配置器前端 | `modules/m13_3d_viewer/`（含前端目录） | 桌面 + 移动端旋转流畅，材质切换毫秒级 |
| 2.5 联调测试 | `tests/auto/test_3d_pipeline.py`（新建） | 客户图片 → GLB → 材质渲染 → 浏览器查看完整链路通过 |

### Sprint 3（建议第 5-6 周）：报价引擎

| 任务 | 文件 | 验收标准 |
|---|---|---|
| 3.1 五维系数计算 | `modules/m10_pricing/main.py` | 给定输入精确匹配预期输出（误差 ≤ 0.01 元） |
| 3.2 RAG 历史检索（ChromaDB） | `modules/m08_stats/main.py` | 100+ 历史报价导入 + 检索召回率 ≥ 90% |
| 3.3 汇率自动更新 + 预警 | `modules/m10_pricing/main.py` | ±3% 阈值触发钉钉告警 |
| 3.4 三语报价单生成 | `modules/m14_quote_doc/main.py` | 中/英/印尼三个 PDF 输出，水印生效 |

### Sprint 4（建议第 7-8 周）：业务流程 + 集成

| 任务 | 文件 | 验收标准 |
|---|---|---|
| 4.1 14 步状态机 | `modules/m16_workflow/main.py` | 状态流转图与需求 v5.0 § 5.5 一致 |
| 4.2 钉钉通知 + 审批 | `modules/m17_dingtalk/main.py` | 业务员/总经理 H5 微应用可用 |
| 4.3 m01_auth + JWT | `modules/m01_auth/main.py` | 登录、Token 刷新、权限分级 |
| 4.4 m03_ai_recognize 接入百炼 | `modules/m03_ai_recognize/main.py` | 100 张图测试集识别准确率 ≥ 85% |

### Sprint 5（建议第 9-10 周）：客户门户 + 安全

| 任务 | 文件 | 验收标准 |
|---|---|---|
| 5.1 m18_portal 海外客户自助 | `modules/m18_portal/` | 6 国家访问延迟 < 2s |
| 5.2 m19_security 水印 + OTP + 设备指纹 | `modules/m19_security/main.py` | 报价单溯源水印唯一，OTP 5 分钟过期 |
| 5.3 IP 异常告警 | 同上 | 单设备指纹切换 IP 频率超阈值触发钉钉告警 |

### Sprint 6（建议第 11-12 周）：收尾

| 任务 | 验收标准 |
|---|---|
| 6.1 m20/m21 Bug 全流程上线 | 自动化测试失败 → 自动建 Bug → 钉钉通知到位 |
| 6.2 性能压测 | 100 并发报价请求，P95 延迟 < 3s |
| 6.3 安全扫描 | OWASP Top 10 通过；无硬编码密钥；权限最小化 |
| 6.4 部署文档 | Docker Compose 一键部署到内网服务器 |

---

## 第八章 外包团队工作规范（强制）

### 8.1 编码规范

- **语言**：所有注释、错误信息、日志使用中文（与 CLAUDE.md RULE 0 一致）
- **不允许 `print()`**：必须用 `logger.info/error`
- **不允许硬编码密钥**：违反者 commit 直接被 pre-commit 钩子拦截
- **不允许跨模块直接 import**：违反 `tests/auto/test_isolation.py::test_no_cross_module_imports`

### 8.2 模块开发自检清单

每个新模块开发完成时：

```
□ schema.py 完整定义 I/O（引用 schemas/ 全局类型，不重复造轮子）
□ main.py 的 run() 用 @isolated(module_id="...") 装饰
□ README.md 有完整说明（输入/输出/依赖/接口）
□ test_data/sample_input.json 有真实样本
□ test_data/expected_output.json 有预期输出
□ tests/auto/test_{mid}.py 有自动化测试（单元 + 集成）
□ utils/logger.py 已接入（错误日志含 "Error: " 前缀）
□ 没有 print() 没有硬编码密钥
□ config.yaml 已注册新配置项（如有）
□ master.py / api_gateway.py 已注册新模块路由（如有 router）
□ pytest tests/auto/ -v 全绿
```

### 8.3 提交流程

```bash
# 1. 创建 feature 分支
git checkout -b feature/m10-pricing-impl

# 2. 开发 + 自测
pytest tests/auto/ -v
python -m modules.m10_pricing.main   # 模块独立可运行验证

# 3. 安装 pre-commit 钩子（首次）
pip install pre-commit
pre-commit install

# 4. 提交（pre-commit 会自动跑烟囱+隔离+密钥扫描）
git add .
git commit -m "feat(m10): 实现五维定价计算 + 汇率预警"

# 5. push 后开 PR；CI 必须绿
git push -u origin feature/m10-pricing-impl
```

### 8.4 Bug 上报流程（开发期）

任意自动化测试失败时，`utils/isolation.py` 会自动通过 `m21_bug_report` 建 Bug，并联动钉钉通知（M-17 上线后）。**不允许**关闭 `config.yaml > testing.failure_handling.create_bug_on_fail`。

---

## 第九章 密钥与服务清单

### 9.1 macOS Keychain 注入项

| Service Name | Account | 用途 | 必需/可选 |
|---|---|---|---|
| `DASHSCOPE_API_KEY` | leslie | 阿里百炼 qwen3-vl-plus / qwen3-max | 必需 |
| `HUNYUAN3D_API_KEY` | leslie | 腾讯混元 3D | 必需 |
| `SEEDREAM_API_KEY` | leslie | 字节 Seedream 4.0 Edit | 必需 |
| `ANTHROPIC_API_KEY` | leslie | Claude（备选视觉） | 可选 |
| `DEEPSEEK_API_KEY` | leslie | DeepSeek-V3（备选文本） | 可选 |
| `DINGTALK_APP_KEY` | leslie | 钉钉 H5 微应用 | 可选 |
| `DINGTALK_APP_SECRET` | leslie | 钉钉 H5 微应用 | 可选 |

### 9.2 Keychain 设置命令

```bash
security add-generic-password -a "leslie" -s "DASHSCOPE_API_KEY" -w "<密钥值>"
# ... 其余密钥同上
```

### 9.3 第三方服务

| 服务 | 用途 | 文档 |
|---|---|---|
| 阿里百炼 dashscope | qwen3-vl-plus 视觉 / qwen3-max 文本 | https://dashscope.aliyun.com/ |
| 腾讯混元 3D | 图片 → GLB 模型 | （企业 API） |
| 字节 Seedream 4.0 Edit | 图像编辑（材质换图） | （企业 API） |
| 钉钉开放平台 | H5 微应用 + 通知 + 审批 | https://open.dingtalk.com/ |

---

## 第十章 常见问题（FAQ）

### Q1：模块开发时如何调用其他模块？

**禁止**：`from modules.m15_customer.main import run`
**正确**：
```python
from utils.isolation import call_module

customer = call_module("m15_customer", {"action": "get", "customer_id": "C-US-001"})
if customer.get("status") == "fallback":
    # m15 未启用或异常，走降级逻辑
    ...
```

### Q2：模块自身 import 应该写在哪里？

可以自由 `from utils.* import ...` 和 `from schemas.* import ...`，但**禁止** `from modules.mXX import ...`（被自动化测试拦截）。

### Q3：模块抛异常会不会污染整个系统？

不会。`@isolated` 装饰器把所有异常转成标准错误响应：
```json
{"status": "error", "module": "m10_pricing", "error": "...", "isolated": true}
```
并自动通过 `m21_bug_report` 建 Bug，调用方收到响应正常往下走。

### Q4：如何让我的模块只在指定环境启用？

修改 `config.yaml > modules.{mid}.enabled` 即可，**禁止**在代码中写环境判断。

### Q5：如何添加新模块（M-22）？

1. 在 `modules/registry.py > MODULES` 注册元数据
2. 在 `tests/auto/test_smoke.py > MODULE_IDS` 追加
3. 在 `tests/auto/test_isolation.py > ALL_MODULE_IDS` 追加
4. 在 `tests/test_ui/index.html > MODULES` 数组追加卡片
5. 创建 `modules/m22_xxx/` 目录（含 5 个标准文件）
6. 跑 `pytest tests/auto/ -v` 必须 60+ 通过

---

## 第十一章 联系人与权限

| 角色 | 联系方式 | 权限 |
|---|---|---|
| 业主 | 项目所有者 | 全部权限 + 定价系数最终决策 |
| 产品经理 | 待外包指派 | 优先级调整 / 验收 / 需求澄清 |
| 技术负责人 | 待外包指派 | Critical Bug 默认 assignee |
| 模块负责人 | 各模块开发员 | High Bug 默认 assignee |

---

## 第十二章 验收交付清单（对外包的最终验收标准）

| 类别 | 验收项 | 验证方式 |
|---|---|---|
| 功能 | 21 模块业务实现完整 | `pytest tests/auto/ -v` 全绿 + 手工测试 Dashboard 全勾 |
| 性能 | 100 并发报价 P95 < 3s | 压测报告 |
| 安全 | OWASP Top 10 通过 | 安全扫描报告 + 无硬编码密钥 |
| 数据 | 客户专有产品不上云 | 单元测试覆盖 `is_proprietary` 闸门 |
| 部署 | 内网 Docker Compose 一键起 | `docker-compose up -d` 后所有服务健康 |
| 文档 | 每模块 README + API 文档 | `/docs` 路径 OpenAPI 完整 |
| 监控 | 钉钉通知正常 | 模拟 critical Bug 触发，30s 内钉钉群收到 |

---

*FurniQuote AI · 技术交接清单 v1.0 · 2026-04-25*
*配套阅读：[PM_产品规划书.md](PM_产品规划书.md)*
