# FurniQuote AI · 法式古典家具智能报价系统

> 从客户随手发一张图，到专业报价单送到客户手中——24小时内完成。

---

## 项目定位

法式古典家具出口企业的 **AI 辅助报价中枢系统**，串起从「客户询价」到「工厂生产存档」的全链路数字化平台。

### 三大核心能力

| 能力 | 实现 |
|---|---|
| 看懂图片 | 百炼 qwen3-vl-plus 识别家具特征（雕花/材质/工艺） |
| 算对价格 | 五维定价矩阵（基准价 × 客户级别 × 数量 × 汇率 × 承价 × 地区）+ RAG 历史参考 |
| 出对方案 | 腾讯混元3D + Seedream 4.0 Edit + Three.js 配置器 + 中/英/印尼三语报价单 |

### 三个不可妥协的原则

1. **定价权完全在公司** — AI 只输出建议，最终价格由人决定
2. **核心数据绝不外泄** — 服务器+数据库部署在国内自家服务器
3. **客户看不到任何定价逻辑** — 配置器自由玩，价格由业务员单独发送

---

## 当前阶段

📋 **阶段 1：3D 配置器小模块开发**（4-6 周）
- 已完成：工程骨架按 CLAUDE.md v1.2 规范搭建
- 进行中：M-11 混元3D / M-12 Seedream / M-13 Three.js / M-15 客户档案 / M-10 报价引擎

---

## 快速启动

### 1. 配置密钥到 macOS Keychain（一次性）

```bash
security add-generic-password -a "leslie" -s "DASHSCOPE_API_KEY"   -w "<你的百炼密钥>"
security add-generic-password -a "leslie" -s "HUNYUAN3D_API_KEY"   -w "<你的混元3D密钥>"
security add-generic-password -a "leslie" -s "SEEDREAM_API_KEY"    -w "<你的Seedream密钥>"
# ... 其他密钥参见 .env.example
```

### 2. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 启动总控

```bash
./start.sh
# 或直接运行（跳过 Keychain 注入，开发模式）
python master.py
```

启动后访问：
- API 文档：http://localhost:8000/docs
- 测试 Dashboard：http://localhost:8000/test 或 `tests/test_ui/index.html`

---

## 目录结构

```
26007FurniQuote/
├── master.py              ← 总控入口（启动检查 + 模块注册 + FastAPI）
├── config.yaml            ← 统一配置（含五维定价系数表）
├── api_gateway.py         ← 前后台接口统一层
├── schemas/               ← 全局 I/O Schema
├── modules/               ← 19 个热拔插模块
│   ├── m10_pricing/         🔴 P0 报价引擎
│   ├── m11_3d_modeling/     🔴 P0 混元3D
│   ├── m12_3d_material/     🔴 P0 Seedream 材质
│   ├── m13_3d_viewer/       🔴 P0 Three.js 查看器
│   ├── m15_customer/        🔴 P0 客户档案
│   └── ... 共 19 个
├── utils/                 ← 统一日志 + Keychain 工具
├── tests/
│   ├── auto/                自动化测试（pytest）
│   ├── manual/              手工测试文档
│   └── test_ui/             测试 Dashboard
└── logs/                  ← 日志输出（gitignore）
```

## 21 模块状态

| 模块 | 名称 | 优先级 | 状态 |
|---|---|---|---|
| M-01 | 认证 | P1 | 占位（工具A已有，待迁移） |
| M-02 | 文件夹管理 | P1 | 占位 |
| M-03 | AI 视觉识别 | P1 | 占位（工具A已有） |
| M-04 | 标注 | P1 | 占位（工具A已完成） |
| M-05 | 专家审核 | P1 | 占位 |
| M-06 | 材质库 | P0 | 占位 |
| M-07 | 词典 | P1 | 占位（工具A已有） |
| M-08 | 统计/RAG | P1 | 占位 |
| M-09 | Prompt 管理 | P1 | 占位 |
| **M-10** | **报价引擎** | **P0** | **占位（核心）** |
| **M-11** | **混元3D** | **P0** | **占位** |
| **M-12** | **Seedream 材质** | **P0** | **占位** |
| **M-13** | **Three.js 查看器** | **P0** | **占位** |
| M-14 | 报价单生成 | P1 | 占位 |
| **M-15** | **客户档案** | **P0** | **占位** |
| M-16 | 业务流程引擎 | P1 | 占位 |
| M-17 | 钉钉集成 | P1 | 占位 |
| M-18 | 客户门户 | P2 | 占位 |
| M-19 | 安全防泄露 | P1/P2 | 占位 |
| 🐞 **M-20** | **Bug 记录管理** | P1 | 占位（开发期就启用） |
| 🐞 **M-21** | **Bug 上报系统** | P1 | 占位（含自动测试失败联动） |

---

## 架构原则：分与合（模块隔离 + 热拔插）

**硬约束**：单个模块出问题不能牵连其他模块；任何模块都可独立运行。

工程实现：

| 机制 | 文件 | 作用 |
|---|---|---|
| `@isolated` 装饰器 | [utils/isolation.py](utils/isolation.py) | 模块入口异常自动转换为 `{status:error,isolated:true}`，绝不外抛 |
| `safe_import_module` | 同上 | 模块导入失败仅记 Error 并返回 None，不阻塞调用方 |
| `call_module(id, payload, fallback)` | 同上 | 跨模块调用强制走此入口，目标失效时返回降级 |
| 模块注册中心 | [modules/registry.py](modules/registry.py) | 21 个模块的元数据+依赖图+健康检查，禁止顶层互相 import |
| api_gateway 单点容错 | [api_gateway.py](api_gateway.py) | 单模块路由注册失败仅记 Error，不阻塞 FastAPI 启动 |
| 隔离测试 | [tests/auto/test_isolation.py](tests/auto/test_isolation.py) | 自动校验跨模块 import / 异常隔离 / 热拔插能力 |

**禁止行为**：
- ❌ `from modules.m10_pricing import ...` —— 业务模块间禁止顶层 import（隔离测试会失败）
- ❌ 模块内 `raise` 不被 `@isolated` 包裹 —— 异常会越界
- ❌ 配置/密钥在子模块中直接读 —— 必须经总控层

**推荐行为**：
- ✅ 跨模块通讯：`call_module("m15_customer", payload)`
- ✅ 共享数据契约：从 `schemas/` 引用 Pydantic 模型
- ✅ 模块独立自测：`python -m modules.m10_pricing.main`

---

## 文档

- [家具报价系统_需求分析文档_v5.0_最终版.md](家具报价系统_需求分析文档_v5.0_最终版.md) — 业务规则真相源（58题）
- [FurniQuote_编码就绪规划书_v6.0.md](FurniQuote_编码就绪规划书_v6.0.md) — 19 模块拆分 + Schema + 优先级
- [CLAUDE.md](CLAUDE.md) — 项目级工程规范（继承全局 ~/.claude/CLAUDE.md v1.2）

---

## 开发规范

每个新模块开发完成时必须自检：

```
□ 模块独立可运行（热拔插）
□ schema.py 完整定义 I/O
□ README.md 有完整说明
□ test_data/ 有预置测试数据
□ tests/auto/ 有自动化测试
□ utils/logger.py 已接入（错误日志 "Error: " 前缀）
□ 没有 print() / 没有硬编码密钥
□ config.yaml 已注册新配置项
□ master.py / api_gateway.py 已注册新模块路由
```

---

*FurniQuote AI · v6.0 编码就绪 · 2026年4月*
