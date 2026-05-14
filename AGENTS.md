# capability-evolver-skill

> 确定性日志分析引擎 — 无 LLM 调用，无外部依赖，完全本地运行

## 触发条件

当用户说：
- 分析这些日志
- 系统健康检查
- 什么在失败
- 改进我的 agent
- 生成进化建议
- 诊断错误
- 健康评分

## 使用

```bash
# 分析日志
python scripts/capability_evolver.py analyze --logs-file logs.jsonl

# 生成进化建议
python scripts/capability_evolver.py evolve --logs-file logs.jsonl --strategy harden
```

## 关键路径

- 脚本：`~/repos/capability-evolver-skill/scripts/capability_evolver.py`
