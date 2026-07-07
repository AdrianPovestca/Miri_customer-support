"""
feedback.py
-----------
Phase 5: Advanced Features — user feedback loop.

Lets customers rate whether a response was helpful. Each generated response
gets a unique ID; feedback is recorded against that ID, so we can later see
which knowledge base entries or phrasing tend to get negative feedback and
improve them.

Like analytics.py, this is in-memory and resets on restart — good enough
for a portfolio project; a real production system would persist this to a
database.
"""

import time
import uuid
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FeedbackStore:
    def __init__(self, max_responses: int = 1000):
        self.max_responses = max_responses
        # response_id -> {"query": str, "response": str, "timestamp": float}
        self._responses: Dict[str, dict] = {}
        # response_id -> {"rating": "positive"/"negative", "comment": str|None, "timestamp": float}
        self._ratings: Dict[str, dict] = {}

    def register_response(self, query: str, response_text: str) -> str:
        """Call this right after generating a response, to get an ID for feedback."""
        response_id = str(uuid.uuid4())
        self._responses[response_id] = {
            "query": query,
            "response": response_text,
            "timestamp": time.time(),
        }

        if len(self._responses) > self.max_responses:
            oldest_id = next(iter(self._responses))
            self._responses.pop(oldest_id, None)
            self._ratings.pop(oldest_id, None)

        return response_id

    def record_feedback(self, response_id: str, rating: str, comment: Optional[str] = None) -> bool:
        """Returns False if response_id isn't recognized (e.g. expired or invalid)."""
        if response_id not in self._responses:
            return False

        self._ratings[response_id] = {
            "rating": rating,
            "comment": comment,
            "timestamp": time.time(),
        }
        return True

    def summary(self) -> Dict:
        total = len(self._ratings)
        positive = sum(1 for r in self._ratings.values() if r["rating"] == "positive")
        negative = total - positive
        satisfaction_rate = (positive / total * 100) if total else 0.0

        recent_negative: List[Dict] = []
        for response_id, rating in list(self._ratings.items())[::-1]:
            if rating["rating"] == "negative" and len(recent_negative) < 5:
                original = self._responses.get(response_id, {})
                recent_negative.append({
                    "query": original.get("query", ""),
                    "comment": rating.get("comment"),
                })

        return {
            "total_feedback": total,
            "positive": positive,
            "negative": negative,
            "satisfaction_rate_pct": round(satisfaction_rate, 1),
            "recent_negative_feedback": recent_negative,
        }


# Single shared instance used by the API and CLI
feedback_store = FeedbackStore()