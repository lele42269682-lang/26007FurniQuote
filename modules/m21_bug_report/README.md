# 模块 m21_bug_report · Bug上报系统

**优先级**：P1
**说明**：🐞 客户/业务员/自动测试一键上报入口（自动收集上下文+联动钉钉）

---

## 模块职责


- 一键上报入口（HTTP API + 前端 SDK 嵌入业务页面）
- 自动收集上下文：当前页面 URL、User-Agent、Console 错误、最近网络请求 ID、截图
- 三个上报源：客户门户（M-18）、内部业务员、自动化测试失败（CI 触发）
- 防滥用：上报频率限制（速率限制）+ 内容过滤
- 调用 M-20 创建 Bug 记录，并返回追踪号给上报人
- 严重度阈值触发钉钉 / 邮件通知（M-17）


## 输入 / 输出

```python
from modules.m21_bug_report.schema import *
```

## 依赖

- `utils.logger` — 统一日志
- `schemas.bug` — Bug 全局 Schema
- `modules.m17_dingtalk`（远期）— 上报后通知协作群
- `modules.m01_auth` — 鉴权与权限校验

## 测试

```bash
pytest tests/auto/test_m21_bug_report.py
python -m modules.m21_bug_report.main
```
