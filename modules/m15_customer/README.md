# 模块 m15_customer · 客户档案

**优先级**：P0
**说明**：🔴 客户分级/承价/地区/锁价协议管理

---

## 模块职责

> 详见根目录 `FurniQuote_编码就绪规划书_v6.0.md` 第四部分对应章节。

## 输入 / 输出

```python
from modules.m15_customer.schema import CustomerInput, CustomerOutput
```

## 依赖

- `utils.logger` — 统一日志
- `schemas.*` — 全局类型
- TBD（开发时补全）

## 测试

```bash
# 自动化测试
pytest tests/auto/test_m15_customer.py

# 模块自测（热拔插）
python -m modules.m15_customer.main
```

## 开发自检清单

```
□ schema.py 完整定义 I/O
□ main.py 实现业务逻辑
□ test_data/sample_input.json 有真实样本
□ test_data/expected_output.json 有预期输出
□ tests/auto/test_m15_customer.py 通过
□ utils/logger 已接入
□ config.yaml 已注册新配置项（如有）
□ api_gateway.py 已挂载路由（如有）
```
