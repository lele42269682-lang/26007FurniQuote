# 模块 m20_bug_tracking · Bug记录管理

**优先级**：P1
**说明**：🐞 内部 Bug 全生命周期管理（创建/分配/修复/验证/关闭/统计）

---

## 模块职责


- Bug 全生命周期：创建 → 分类 → 分配 → 修复 → 验证 → 关闭
- 状态流转：OPEN → TRIAGED → IN_PROGRESS → RESOLVED → VERIFIED → CLOSED（或 REJECTED）
- 提供查询/过滤/分页接口（按状态/严重程度/模块/负责人）
- 统计仪表盘：未关闭数、按模块分布、平均修复时长、回归率
- 与 M-21 上报模块解耦：M-21 创建 Bug 后调用 M-20 入库
- 与 M-17 钉钉联动：高严重度 Bug 自动推送审批/协作群


## 输入 / 输出

```python
from modules.m20_bug_tracking.schema import *
```

## 依赖

- `utils.logger` — 统一日志
- `schemas.bug` — Bug 全局 Schema
- `modules.m17_dingtalk`（远期）— 上报后通知协作群
- `modules.m01_auth` — 鉴权与权限校验

## 测试

```bash
pytest tests/auto/test_m20_bug_tracking.py
python -m modules.m20_bug_tracking.main
```
