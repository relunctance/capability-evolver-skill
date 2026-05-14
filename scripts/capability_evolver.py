#!/usr/bin/env python3
"""
Capability Evolver — 确定性日志分析引擎
分析运行时日志，检测错误模式，计算健康评分，生成改进建议
纯规则逻辑，无 LLM 调用，无外部依赖
"""

import json
import sys
import argparse
import uuid
from datetime import datetime
from collections import defaultdict
from typing import Any


class CapabilityEvolver:
    """确定性日志分析引擎"""

    def __init__(self):
        self.version = "1.0.0"

    def analyze(self, logs: list[dict]) -> dict:
        """
        分析日志，检测模式，计算健康评分

        Args:
            logs: 日志条目列表，每条包含 timestamp, level, message, context(可选)

        Returns:
            dict: patterns, health_score, recommendations, summary
        """
        if not logs:
            return {
                "patterns": [],
                "health_score": 100,
                "recommendations": ["无日志数据，系统处于空闲状态"],
                "summary": {
                    "total_logs": 0,
                    "error_count": 0,
                    "warn_count": 0,
                    "info_count": 0,
                    "debug_count": 0,
                    "unique_patterns": 0,
                },
            }

        # 标准化日志
        normalized = [self._normalize_log(log) for log in logs]

        # 统计摘要
        summary = self._compute_summary(normalized)

        # 检测模式
        patterns = self._detect_patterns(normalized)

        # 生成建议
        recommendations = self._generate_recommendations(patterns, normalized)

        # 计算健康评分
        health_score = self._compute_health_score(summary, patterns)

        return {
            "patterns": patterns,
            "health_score": health_score,
            "recommendations": recommendations,
            "summary": summary,
        }

    def evolve(self, logs: list[dict], strategy: str = "auto") -> dict:
        """
        生成进化建议

        Args:
            logs: 日志条目列表
            strategy: 进化策略 auto|balanced|innovate|harden|repair-only

        Returns:
            dict: evolution_id, strategy, recommendations, risk_assessment, estimated_improvement
        """
        if strategy == "auto":
            analysis = self.analyze(logs)
            hs = analysis["health_score"]
            if hs >= 80:
                strategy = "innovate"
            elif hs >= 50:
                strategy = "balanced"
            elif hs >= 25:
                strategy = "harden"
            else:
                strategy = "repair-only"

        analysis = self.analyze(logs)
        recommendations = self._prioritize_recommendations(
            analysis["patterns"], strategy
        )

        # 估算改进
        current = analysis["health_score"]
        estimated = self._estimate_improvement(current, strategy, len(recommendations))

        evolution_id = f"ev-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"

        risk = self._assess_risk(strategy, recommendations)

        return {
            "evolution_id": evolution_id,
            "strategy": strategy,
            "recommendations": recommendations,
            "risk_assessment": risk,
            "estimated_improvement": f"{current} → {estimated}",
        }

    def status(self, logs: list[dict]) -> dict:
        """
        获取系统健康状态

        Args:
            logs: 日志条目列表

        Returns:
            dict: health_score, summary, status_level
        """
        if not logs:
            return {
                "health_score": 100,
                "summary": {
                    "total_logs": 0,
                    "error_count": 0,
                    "warn_count": 0,
                    "info_count": 0,
                    "debug_count": 0,
                },
                "status_level": "idle",
                "message": "无日志数据，系统处于空闲状态",
            }

        analysis = self.analyze(logs)
        hs = analysis["health_score"]

        if hs >= 80:
            status_level = "healthy"
            message = "系统运行良好"
        elif hs >= 50:
            status_level = "degraded"
            message = "系统性能下降，建议检查错误模式"
        elif hs >= 25:
            status_level = "unhealthy"
            message = "系统存在严重问题，需要立即关注"
        else:
            status_level = "critical"
            message = "系统处于危机状态，建议立即修复关键问题"

        return {
            "health_score": hs,
            "summary": analysis["summary"],
            "status_level": status_level,
            "message": message,
            "top_patterns": analysis["patterns"][:3] if analysis["patterns"] else [],
        }

    # ─── 内部方法 ───────────────────────────────────────────────

    def _normalize_log(self, log: dict) -> dict:
        """标准化日志条目"""
        return {
            "timestamp": log.get("timestamp", ""),
            "level": (log.get("level") or "info").lower(),
            "message": log.get("message", ""),
            "context": log.get("context") or "unknown",
        }

    def _compute_summary(self, logs: list[dict]) -> dict:
        """计算统计摘要"""
        counts = defaultdict(int)
        for log in logs:
            counts[log["level"]] += 1

        return {
            "total_logs": len(logs),
            "error_count": counts["error"],
            "warn_count": counts["warn"],
            "info_count": counts["info"],
            "debug_count": counts["debug"],
            "unique_patterns": len(set(f"{log['context']}:{log['message']}" for log in logs)),
        }

    def _detect_patterns(self, logs: list[dict]) -> list[dict]:
        """检测错误模式"""
        patterns = []

        # 按 context 分组
        by_context = defaultdict(list)
        for log in logs:
            by_context[log["context"]].append(log)

        # 1. repeated_error: 同一错误在同一 context 重复出现
        error_by_context_msg = defaultdict(list)
        for log in logs:
            if log["level"] == "error":
                key = (log["context"], log["message"])
                error_by_context_msg[key].append(log)

        for (context, message), entries in error_by_context_msg.items():
            if len(entries) >= 2:
                patterns.append({
                    "type": "repeated_error",
                    "severity": "high" if len(entries) >= 3 else "medium",
                    "description": f"{message} 在 {context} 出现 {len(entries)} 次",
                    "affected_contexts": [context],
                    "count": len(entries),
                })

        # 2. error_cascade: 不同模块在短时间内连续错误
        error_times = [(log["context"], log["timestamp"]) for log in logs if log["level"] == "error"]
        if len(error_times) >= 2:
            for i in range(len(error_times) - 1):
                ctx1, ts1 = error_times[i]
                ctx2, ts2 = error_times[i + 1]
                if ctx1 != ctx2:
                    patterns.append({
                        "type": "error_cascade",
                        "severity": "medium",
                        "description": f"{ctx1} 错误后 {ctx2} 也出现错误",
                        "affected_contexts": list(set([ctx1, ctx2])),
                    })

        # 3. regression_signal: 在大量 info/debug 后出现 error
        if len(logs) >= 10:
            first_half = logs[:len(logs)//2]
            second_half = logs[len(logs)//2:]
            first_errors = sum(1 for l in first_half if l["level"] == "error")
            second_errors = sum(1 for l in second_half if l["level"] == "error")
            if first_errors == 0 and second_errors > 0:
                patterns.append({
                    "type": "regression_signal",
                    "severity": "high",
                    "description": "前期无错误，后期出现错误，可能存在回归",
                    "affected_contexts": list(set(l["context"] for l in second_half if l["level"] == "error")),
                })

        # 4. inefficiency: 大量 warn 或重复重试
        warn_count = sum(1 for l in logs if l["level"] == "warn")
        if warn_count > len(logs) * 0.3:
            patterns.append({
                "type": "inefficiency",
                "severity": "medium",
                "description": f"警告日志过多（{warn_count}/{len(logs)}），可能存在性能或配置问题",
                "affected_contexts": list(set(l["context"] for l in logs if l["level"] == "warn")),
            })

        # 去重：合并相同 type + context 的模式
        seen = {}
        deduped = []
        for p in patterns:
            key = (p["type"], tuple(sorted(p["affected_contexts"])))
            if key not in seen:
                seen[key] = p
                deduped.append(p)
            else:
                # 合并 count
                existing = seen[key]
                if "count" in p:
                    existing["count"] = max(existing.get("count", 0), p["count"])

        # 按 severity 排序
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        deduped.sort(key=lambda p: severity_order.get(p["severity"], 3))

        return deduped

    def _generate_recommendations(self, patterns: list[dict], logs: list[dict]) -> list[str]:
        """根据模式生成建议"""
        recs = []

        for p in patterns:
            if p["type"] == "repeated_error":
                ctx = p["affected_contexts"][0]
                recs.append(f"为 {ctx} 添加超时配置和重试逻辑")
                recs.append(f"检查 {ctx} 的外部依赖服务是否稳定")
            elif p["type"] == "error_cascade":
                ctxs = ", ".join(p["affected_contexts"])
                recs.append(f"检查依赖链：{ctxs}，定位根因模块")
            elif p["type"] == "regression_signal":
                recs.append("检查最近部署或配置变更，定位引入回归的变更")
            elif p["type"] == "inefficiency":
                recs.append("优化配置或增加资源，解决性能瓶颈")

        if not recs:
            recs.append("继续保持当前运行状态，定期巡检")

        return list(dict.fromkeys(recs))  # 去重保持顺序

    def _compute_health_score(self, summary: dict, patterns: list[dict]) -> int:
        """计算健康评分 0-100"""
        if summary["total_logs"] == 0:
            return 100

        # 错误率 (40%)
        error_rate = summary["error_count"] / summary["total_logs"]
        error_score = max(0, 100 - error_rate * 100 * 2)  # 50%错误=0分

        # 错误多样性 (20%)：独特错误越多（分散）越健康
        if summary["error_count"] > 0:
            diversity = summary["unique_patterns"] / summary["error_count"]
            diversity_score = min(100, diversity * 50)  # 全部不同=50分满分
        else:
            diversity_score = 100

        # Warn/Error 比 (20%)
        if summary["error_count"] > 0:
            warn_error_ratio = summary["warn_count"] / summary["error_count"]
            ratio_score = min(100, warn_error_ratio * 30)  # 3:1=90分
        else:
            ratio_score = 100

        # 时间分布 (20%)：模式越集中越不健康
        severity_penalty = sum(
            {"critical": 30, "high": 20, "medium": 10, "low": 5}.get(p["severity"], 0)
            for p in patterns
        )

        score = (
            error_score * 0.40 +
            diversity_score * 0.20 +
            ratio_score * 0.20 +
            max(0, 100 - severity_penalty) * 0.20
        )

        return max(0, min(100, int(score)))

    def _prioritize_recommendations(
        self, patterns: list[dict], strategy: str
    ) -> list[dict]:
        """根据策略生成优先级建议"""
        recs = []

        category_map = {
            "repeated_error": "reliability",
            "error_cascade": "architecture",
            "regression_signal": "reliability",
            "inefficiency": "performance",
        }

        for p in patterns:
            category = category_map.get(p["type"], "reliability")
            priority = p["severity"]

            if strategy == "harden" and p["type"] in ("repeated_error", "regression_signal"):
                approach = f"立即修复 {p['affected_contexts']}，添加熔断和超时"
            elif strategy == "innovate":
                approach = f"优化 {p['affected_contexts']}，引入新架构模式"
            elif strategy == "repair-only" and p["severity"] in ("critical", "high"):
                approach = f"紧急修复 {p['affected_contexts']}"
            else:
                approach = f"分析并优化 {p['affected_contexts']}"

            recs.append({
                "priority": priority,
                "category": category,
                "description": p["description"],
                "affected_files": p["affected_contexts"],
                "suggested_approach": approach,
                "estimated_effort": "medium",
            })

        # repair-only 策略只保留 critical/high
        if strategy == "repair-only":
            recs = [r for r in recs if r["priority"] in ("critical", "high")]

        return recs

    def _estimate_improvement(
        self, current: int, strategy: str, rec_count: int
    ) -> int:
        """估算改进后的健康评分"""
        base_improvement = {
            "innovate": 15,
            "balanced": 20,
            "harden": 25,
            "repair-only": 10,
        }.get(strategy, 15)

        # 每条建议额外提升
        extra = min(rec_count * 3, 15)
        estimated = min(100, current + base_improvement + extra)
        return estimated

    def _assess_risk(self, strategy: str, recommendations: list[dict]) -> dict:
        """风险评估"""
        if strategy == "repair-only":
            level = "low"
            factors = ["只修复关键问题", "变更范围最小化"]
        elif strategy == "harden":
            level = "medium"
            factors = ["涉及配置和重试逻辑变更", "需要充分测试"]
        elif strategy == "innovate":
            level = "high"
            factors = ["可能引入新架构", "需要回归测试"]
        else:
            level = "medium"
            factors = ["中等范围变更", "建议分批部署"]

        if len(recommendations) > 5:
            factors.append("建议分批实施，降低风险")

        return {"level": level, "factors": factors}


# ─── CLI 入口 ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Capability Evolver — 确定性日志分析引擎")
    sub = parser.add_subparsers(dest="action", required=True)

    p_analyze = sub.add_parser("analyze", help="分析日志")
    p_analyze.add_argument("--logs-file", required=True, help="日志文件 (JSON Lines)")

    p_evolve = sub.add_parser("evolve", help="生成进化建议")
    p_evolve.add_argument("--logs-file", required=True, help="日志文件 (JSON Lines)")
    p_evolve.add_argument("--strategy", default="auto", choices=["auto", "balanced", "innovate", "harden", "repair-only"])

    p_status = sub.add_parser("status", help="健康状态")
    p_status.add_argument("--logs-file", required=True, help="日志文件 (JSON Lines)")

    args = parser.parse_args()

    # 读取日志
    logs = []
    with open(args.logs_file) as f:
        for line in f:
            line = line.strip()
            if line:
                logs.append(json.loads(line))

    evolver = CapabilityEvolver()

    if args.action == "analyze":
        result = evolver.analyze(logs)
    elif args.action == "evolve":
        result = evolver.evolve(logs, args.strategy)
    elif args.action == "status":
        result = evolver.status(logs)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
