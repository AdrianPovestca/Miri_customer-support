"""
analytics.py
------------
Phase 4: Production — lightweight, in-memory monitoring for the API.

Tracks basic usage metrics (request count, response times, AI vs. template
fallback rate) without needing an external monitoring service. This is
intentionally simple: metrics reset when the server restarts. For a real
production deployment, this would be swapped for something like
Prometheus + Grafana, or a hosted APM tool — that's a natural "next step"
to mention if this project comes up in an interview.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List


@dataclass
class RequestLogEntry:
    timestamp: float
    query: str
    duration_ms: float
    used_ai_generation: bool
    result_count: int


class Analytics:
    def __init__(self, max_recent: int = 200):
        self.total_requests = 0
        self.total_duration_ms = 0.0
        self.ai_generation_count = 0
        self.template_fallback_count = 0
        self.no_results_count = 0
        # Keep only the most recent N requests in detail, so memory doesn't grow forever
        self.recent: Deque[RequestLogEntry] = deque(maxlen=max_recent)

    def record(self, query: str, duration_ms: float, used_ai_generation: bool, result_count: int) -> None:
        self.total_requests += 1
        self.total_duration_ms += duration_ms
        if used_ai_generation:
            self.ai_generation_count += 1
        else:
            self.template_fallback_count += 1
        if result_count == 0:
            self.no_results_count += 1

        self.recent.append(RequestLogEntry(
            timestamp=time.time(),
            query=query,
            duration_ms=duration_ms,
            used_ai_generation=used_ai_generation,
            result_count=result_count,
        ))

    def summary(self) -> Dict:
        avg_duration = (self.total_duration_ms / self.total_requests) if self.total_requests else 0.0
        ai_rate = (self.ai_generation_count / self.total_requests * 100) if self.total_requests else 0.0
        no_results_rate = (self.no_results_count / self.total_requests * 100) if self.total_requests else 0.0

        return {
            "total_requests": self.total_requests,
            "avg_response_time_ms": round(avg_duration, 1),
            "ai_generation_used": self.ai_generation_count,
            "template_fallback_used": self.template_fallback_count,
            "ai_generation_rate_pct": round(ai_rate, 1),
            "no_relevant_results_rate_pct": round(no_results_rate, 1),
            "recent_queries": [
                {
                    "query": entry.query,
                    "duration_ms": round(entry.duration_ms, 1),
                    "used_ai_generation": entry.used_ai_generation,
                }
                for entry in list(self.recent)[-10:]  # last 10, most recent last
            ],
        }


# Single shared instance used by the API
analytics = Analytics()