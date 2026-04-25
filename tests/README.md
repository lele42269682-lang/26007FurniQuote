# 自动化测试系统

本项目按 CLAUDE.md RULE 6 嵌入 **三层测试体系** + **CI/CD 自动化** + **隔离验证**。

---

## 三层测试结构

```
tests/
├── auto/              ← 第一层：pytest 自动化测试（CI 自动跑）
│   ├── test_smoke.py        骨架可用性 + 21模块烟囱
│   ├── test_isolation.py    模块隔离 + 热拔插验证
│   └── test_{mid}.py        各业务模块功能测试（开发时补全）
├── manual/            ← 第二层：手工测试文档（人工执行）
│   └── {mid}_manual.md      各模块手工验证步骤
├── test_ui/           ← 第三层：测试 Dashboard（点按式触发）
│   └── index.html
└── ci/                ← CI 辅助脚本与 fixture
    └── conftest.py    （可在此放共享 fixture）
```

## 触发方式

| 触发场景 | 何时执行 | 配置位置 |
|---|---|---|
| 提交前自动跑 | `git commit` 时 | `.pre-commit-config.yaml` |
| 推送/PR 触发 | `git push` / 开 PR | `.github/workflows/test.yml` |
| 手工烟囱 | 开发时 | `pytest tests/auto/test_smoke.py` |
| 手工隔离验证 | 修改隔离层后 | `pytest tests/auto/test_isolation.py` |
| 测试 Dashboard | 浏览器交互 | `http://localhost:8000/test` |
| 模块自测 | 单模块开发 | `python -m modules.{mid}.main` |

## 启用 pre-commit 钩子

```bash
pip install pre-commit
pre-commit install
# 之后 git commit 会自动跑 烟囱+隔离+密钥扫描
```

## CI 工作流（GitHub Actions）

`.github/workflows/test.yml` 在每次 push/PR 时执行：

1. **smoke-tests** — Python 3.11/3.12 矩阵跑全部测试，覆盖率门槛 70%
2. **security-scan** — 扫描硬编码密钥（按 CLAUDE.md RULE 10）

CI 失败默认会被 GitHub 标记 ❌，配合分支保护可阻止合并。

---

## 模块隔离与热拔插测试（test_isolation.py）

四类断言保证"分与合"原则：

1. **@isolated 装饰器** — 单模块异常不向上抛，转换为 `{status:error, isolated:true}`
2. **safe_import / call_module** — 跨模块调用失败时返回降级，不阻塞调用方
3. **每个模块独立可运行** — 21 个模块的 `run()` 单独执行均成功
4. **禁止跨模块直接 import** — 自动扫描 `modules/` 源码，违反时测试失败

新增模块时必须：
- 在 `modules/registry.py` 注册元数据（id/name/priority/depends_on/soft_depends）
- 在 `tests/auto/test_smoke.py` 的模块列表中追加
- 在 `tests/auto/test_isolation.py` 的 `ALL_MODULE_IDS` 中追加

---

## 自动化测试 → Bug 上报联动

`config.yaml > testing.failure_handling.create_bug_on_fail = true` 时，
CI 失败会通过 `m21_bug_report` 自动建 Bug 并联动钉钉（M-17 接入后）。

实现位置：`utils/isolation.py:_signal_bug_report`，每个 `@isolated` 装饰的模块异常都会调用。
