# 模块 m03_ai_recognize · AI视觉识别

**优先级**：P1
**说明**：百炼 qwen3-vl-plus 识别家具雕花/材质/工艺

---

## 模块职责

> 详见根目录 `FurniQuote_编码就绪规划书_v6.0.md` 第四部分对应章节。

## 输入 / 输出

```python
from modules.m03_ai_recognize.schema import AiRecognizeInput, AiRecognizeOutput
```

## 依赖

- `utils.logger` — 统一日志
- `schemas.*` — 全局类型
- TBD（开发时补全）

## 测试

```bash
# 自动化测试
pytest tests/auto/test_m03_ai_recognize.py

# 模块自测（热拔插）
python -m modules.m03_ai_recognize.main
```

## 开发自检清单

```
□ schema.py 完整定义 I/O
□ main.py 实现业务逻辑
□ test_data/sample_input.json 有真实样本
□ test_data/expected_output.json 有预期输出
□ tests/auto/test_m03_ai_recognize.py 通过
□ utils/logger 已接入
□ config.yaml 已注册新配置项（如有）
□ api_gateway.py 已挂载路由（如有）
```
