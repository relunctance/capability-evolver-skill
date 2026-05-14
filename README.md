# capability-evolver-skill

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](#)
[![platforms](https://img.shields.io/badge/platforms-claude_code%20%7C%20openclaw%20%7C%20hermes-blue.svg)](#)
[![version](https://img.shields.io/badge/version-1.0.0-green.svg)](#)
[![category](https://img.shields.io/badge/category-DevOps-blue.svg)](#)

确定性日志分析引擎 — 分析 agent 运行时日志，检测错误模式，计算健康评分，生成结构化改进建议。

## 触发条件

- `分析这些日志`
- `系统健康检查`
- `什么在失败`
- `改进我的 agent`
- `生成进化建议`

## Quick Start

```bash
# 分析日志
python scripts/capability_evolver.py analyze --logs-file logs.jsonl

# 生成进化建议
python scripts/capability_evolver.py evolve --logs-file logs.jsonl --strategy harden

# 健康状态
python scripts/capability_evolver.py status --logs-file logs.jsonl
```

## 输出示例

```json
{
  "patterns": [
    {
      "type": "repeated_error",
      "severity": "high",
      "description": "ETIMEDOUT 在 payment-api.ts 出现 3 次",
      "affected_contexts": ["payment-api.ts"]
    }
  ],
  "health_score": 45,
  "recommendations": [
    "为 payment-api.ts 添加超时配置和重试逻辑"
  ]
}
```

## 特性

- **确定性分析** — 无 LLM，结果可复现
- **sub-100ms 处理** — 纯计算，无需 API 调用
- **本地运行** — 日志不离机器，完全隐私
- **三种 action** — analyze / evolve / status

## 许可证

MIT
