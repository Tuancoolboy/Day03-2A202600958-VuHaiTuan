import os
import re
import time
from typing import Dict, Any, List
from src.telemetry.logger import logger

class PerformanceTracker:
    """
    Tracking industry-standard metrics for LLMs.
    """
    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        """
        Logs a single request metric to our telemetry.
        """
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate_usd": self._calculate_cost(model, usage),
            "pricing_note": "Set MODEL_PROMPT_USD_PER_1K and MODEL_COMPLETION_USD_PER_1K env vars for exact pricing.",
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """
        Estimate request cost from configurable per-1K token prices.
        """
        model_key = re.sub(r"[^A-Z0-9]+", "_", model.upper()).strip("_")
        prompt_rate = self._env_float(f"{model_key}_PROMPT_USD_PER_1K", "0")
        completion_rate = self._env_float(f"{model_key}_COMPLETION_USD_PER_1K", "0")

        prompt_cost = (usage.get("prompt_tokens", 0) / 1000) * prompt_rate
        completion_cost = (usage.get("completion_tokens", 0) / 1000) * completion_rate
        return round(prompt_cost + completion_cost, 6)

    def _env_float(self, name: str, default: str) -> float:
        try:
            return float(os.getenv(name, default))
        except ValueError:
            return float(default)

# Global tracker instance
tracker = PerformanceTracker()
