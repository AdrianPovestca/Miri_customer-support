"""
config.py
---------
Central configuration, loaded from environment variables (.env).
"""

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional in minimal environments


@dataclass
class Settings:
    # --- Knowledge base / retrieval ---
    knowledge_base_dir: str = os.getenv("KNOWLEDGE_BASE_DIR", "../knowledge_base")
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "3"))
    score_threshold: float = float(os.getenv("SCORE_THRESHOLD", "0.05"))

    # --- Logging ---
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/app.log")

    # --- LLM / OpenAI (Phase 2) ---
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    openai_max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "400"))

    # Master switch: if False (or no API key present), the bot falls back
    # to the original template-based responses from Phase 1.
    use_ai_generation: bool = os.getenv("USE_AI_GENERATION", "true").lower() == "true"

    @property
    def ai_generation_enabled(self) -> bool:
        """AI generation only runs if it's enabled AND a key is configured."""
        return self.use_ai_generation and bool(self.openai_api_key)


settings = Settings()
