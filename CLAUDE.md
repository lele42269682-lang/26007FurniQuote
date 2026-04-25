# FurniQuote AI · 项目级工程规范

本项目继承全局规范 `~/.claude/CLAUDE.md`（v1.2），下面只列项目特有补充。

---

## 需求真相源（必读）

- `家具报价系统_需求分析文档_v5.0_最终版.md` — 业务规则（58 题确认完成）
- `FurniQuote_编码就绪规划书_v6.0.md` — 19 模块拆分 + Schema 定义 + 优先级排期

修改任何业务逻辑前，先回查上述两份文档，确认与原始需求一致。

---

## 模块命名约定

- 所有功能模块放在 `modules/` 下，前缀 `m01_` ~ `m19_`，与规划书 v6.0 模块编号严格对应
- 模块内必须含：`__init__.py`、`main.py`、`schema.py`、`README.md`、`test_data/`
- 模块间数据传递必须经过 `schemas/` 全局 Schema 验证，不允许传裸 dict

## 五维定价系数

所有定价系数在 `config.yaml > pricing` 节点，**禁止在代码中硬编码**。需要调整时只改 yaml。

## 密钥清单（Keychain Account：`leslie`）

| Service Name | 用途 |
|---|---|
| `DASHSCOPE_API_KEY` | 百炼 qwen3-vl-plus / qwen3-max |
| `ANTHROPIC_API_KEY` | Claude（备选视觉识别） |
| `DEEPSEEK_API_KEY` | DeepSeek-V3（备选文本） |
| `HUNYUAN3D_API_KEY` | 腾讯混元3D |
| `SEEDREAM_API_KEY` | 字节 Seedream 4.0 Edit |
| `DINGTALK_APP_KEY` / `DINGTALK_APP_SECRET` | 钉钉 H5 微应用 |

## 数据规范

- 产品编号：`{品类}-{年份}-{序号}`，如 `SF-2024-001`
- 客户编号：`C-{地区}-{序号}`，如 `C-US-001`
- 文件命名：`{产品编号}_{文件类型}_{日期}_{版本}.{扩展名}`

## 客户专有产品

标记 `is_proprietary=true` 的图片只能本地处理，**不上云**。M-11（混元3D）、M-12（Seedream）调用前必须检查此标记。
