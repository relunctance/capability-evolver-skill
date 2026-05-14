---
name: capability-evolver-skill
description: 当需要分析日志、诊断错误、系统健康检查、健康评分、改进建议时使用。确定性日志分析引擎，检测错误模式、计算健康评分、生成改进建议，完全本地运行无外部依赖
version: "1.0.0"
author: relunctance
license: MIT
category: devops
tags:
  - 日志分析
  - 健康评分
  - 错误检测
  - 确定性分析
  - capability
  - evolve
metadata:
  hermes:
    platforms:
      claude_code: true
      openclaw: true
      hermes: true
---

# capability-evolver-skill

> 确定性日志分析引擎 — 无 LLM 调用，无外部依赖，完全本地运行

分析 agent 运行时日志，检测错误模式，计算健康评分，生成结构化改进建议。纯规则逻辑，结果可复现，处理速度 sub-100ms。

## 触发条件

用户说：
- `分析这些日志`
- `系统健康检查`
- `什么在失败`
- `改进我的 agent`
- `生成进化建议`
- `诊断错误`
- `健康评分`

## Quick Reference

| 场景 | Action | 输出 |
|------|--------|------|
| Agent 持续失败 | `analyze` | 错误模式 + 健康评分 |
| 同一错误重复出现 | `analyze` | 根因识别 |
| 需要改进计划 | `evolve` | 优先级建议 |
| 系统健康巡检 | `status` | 评分 + 摘要 |
| 部署后回归检测 | `analyze` | 回归信号 |

## 使用方法

### analyze — 日志分析

```bash
python scripts/capability_evolver.py analyze --logs-file logs.jsonl
```

输入格式（JSON Lines）：
```json
{"timestamp": "2025-01-15T10:00:00Z", "level": "error", "message": "ETIMEDOUT", "context": "payment-api.ts"}
{"timestamp": "2025-01-15T10:01:00Z", "level": "error", "message": "ETIMEDOUT", "context": "payment-api.ts"}
{"timestamp": "2025-01-15T10:02:00Z", "level": "error", "message": "ETIMEDOUT", "context": "payment-api.ts"}
```

输出：
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
    "为 payment-api.ts 添加超时配置",
    "实现指数退避重试逻辑",
    "监控 payment API 响应时间"
  ],
  "summary": {
    "total_logs": 100,
    "error_count": 15,
    "warn_count": 23,
    "unique_patterns": 5
  }
}
```

### evolve — 进化策略

```bash
python scripts/capability_evolver.py evolve --logs-file logs.jsonl --strategy harden
```

可选策略：`auto`（默认）| `balanced` | `innovate` | `harden` | `repair-only`

### status — 健康状态

```bash
python scripts/capability_evolver.py status --logs-file logs.jsonl
```

## Python API

```python
from capability_evolver import CapabilityEvolver

evol = CapabilityEvolver()

# 分析
result = evol.analyze([
    {"timestamp": "2025-01-15T10:00:00Z", "level": "error", "message": "ETIMEDOUT", "context": "payment-api.ts"},
    {"timestamp": "2025-01-15T10:01:00Z", "level": "error", "message": "ETIMEDOUT", "context": "payment-api.ts"},
])
print(result["health_score"])  # 45
print(result["patterns"])       # [...]

# 进化
evolution = evol.evolve(logs, strategy="harden")
print(evolution["estimated_improvement"])  # "45 → 75"

# 状态
status = evol.status(logs)
print(status["health_score"])  # 45
```

## 分析引擎原理

### 模式检测

日志按 `context`（文件/模块）和 `level`（error/warn/info/debug）分组，检测：

- **repeated_error**：同一错误信息多次出现 = 系统性问题，非瞬时故障
- **error_cascade**：模块 A 错误后短时间内模块 B 错误 = 依赖链故障
- **regression_signal**：清日志后出现错误 = 最近变更引入回归
- **inefficiency**：大量 warn 或重复重试 = 性能问题

### 健康评分（0-100）

| 因素 | 权重 | 说明 |
|------|------|------|
| 错误率 | 40% | errors / total_logs |
| 错误多样性 | 20% | unique_errors / total_errors |
| Warn/Error 比 | 20% | warn_count / error_count |
| 时间分布 | 20% | 集中爆发 < 分散出现 |

### 进化策略

| 策略 | 侧重点 | 适用场景 |
|------|--------|---------|
| `auto` | 基于健康评分自动选择 | 默认，让引擎决定 |
| `balanced` | 可靠性与功能均衡 | 稳定系统，中等问题 |
| `innovate` | 优先新能力 | 健康系统，准备扩展 |
| `harden` | 优先可靠性和错误减少 | 频繁故障系统 |
| `repair-only` | 只修复关键问题 | 危机中的系统 |

## 输出格式

### analyze 输出

```json
{
  "patterns": [
    {
      "type": "repeated_error | error_cascade | regression_signal | inefficiency",
      "severity": "critical | high | medium | low",
      "description": "具体描述",
      "affected_contexts": ["file.ts"]
    }
  ],
  "health_score": 0-100,
  "recommendations": ["建议1", "建议2"],
  "summary": {
    "total_logs": 100,
    "error_count": 15,
    "warn_count": 23,
    "info_count": 50,
    "debug_count": 12,
    "unique_patterns": 5
  }
}
```

### evolve 输出

```json
{
  "evolution_id": "ev-20250115-001",
  "strategy": "harden",
  "recommendations": [
    {
      "priority": "critical | high | medium | low",
      "category": "reliability | performance | architecture",
      "description": "描述",
      "affected_files": ["file.ts"],
      "suggested_approach": "具体做法",
      "estimated_effort": "low | medium | high"
    }
  ],
  "risk_assessment": {
    "level": "low | medium | high",
    "factors": ["因素1", "因素2"]
  },
  "estimated_improvement": "45 → 75"
}
```

## 确定性 vs LLM 分析

| 特性 | LLM 基于 | 本地引擎 |
|------|---------|---------|
| 处理速度 | 5-30 秒 | sub-100ms |
| 可复现性 | ❌ 每次结果不同 | ✅ 相同日志相同结果 |
| 幻觉风险 | ⚠️ 可能编造模式 | ✅ 只报告真实模式 |
| 语义理解 | ✅ 理解上下文 | ❌ 基于结构模式 |
| 成本 | $0.10-0.50/次 | 免费 |

## 适用场景

✅ 使用本 skill：
- 需要可复现结果用于审计
- sub-second 处理要求
- 构建自动化流水线
- 隐私敏感（日志不离本地）
- 需要 explainable AI

❌ 不使用本 skill：
- 需要语义理解日志消息
- 需要自然语言解释
- 日志包含非结构化文本
- 愿意牺牲速度换取深度

## 安装

```bash
# 克隆仓库
git clone https://github.com/relunctance/capability-evolver-skill.git
cd capability-evolver-skill

# 直接使用 Python 脚本（无需安装）
python scripts/capability_evolver.py analyze --logs-file your_logs.jsonl
```

## 文件结构

```
capability-evolver-skill/
├── SKILL.md                    # 本文件
├── README.md                   # 用户入口文档
├── LICENSE                     # MIT
├── scripts/
│   └── capability_evolver.py   # 核心分析引擎（Python）
```

## 踩坑记录

| 坑 | 说明 | 解决方案 |
|----|------|---------|
| 日志时间戳格式不统一 | 分析失败 | 引擎内部统一处理 ISO 8601 和 Unix timestamp |
| context 为空 | 模式检测跳过该条 | 允许 context 为空，内部用 "unknown" 替代 |
| 空日志数组 | 返回默认健康分 100 | 引擎内部处理，不报错 |
