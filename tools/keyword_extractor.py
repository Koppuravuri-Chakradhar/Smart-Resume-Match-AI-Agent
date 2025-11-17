"""
Keyword extraction helper built on NLTK for lightweight NLP processing.
Used by multiple agents to normalize skills and job requirements.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from typing import Iterable, List, Tuple

# -----------------------------------------
# 🔥 STREAMLIT FIX — custom NLTK directory
# -----------------------------------------
import nltk
import os

NLTK_DIR = "/tmp/nltk_data"
os.makedirs(NLTK_DIR, exist_ok=True)
nltk.data.path.append(NLTK_DIR)

# Download only REQUIRED resources (punkt + stopwords)
nltk.download("punkt", download_dir=NLTK_DIR, quiet=True)
nltk.download("stopwords", download_dir=NLTK_DIR, quiet=True)
# -----------------------------------------

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Simple keyword extraction based on tokenization and frequency counts."""

    def __init__(self, language: str = "english") -> None:
        self.language = language
        self._ensure_nltk_resources()
        self.stop_words = set(stopwords.words(language))

    def extract(self, text: str, max_keywords: int = 25) -> List[Tuple[str, int]]:
        """Extract ranked keywords."""
        if not text:
            return []

        normalized = re.sub(r"[^A-Za-z0-9\s]+", " ", text.lower())

        tokens = [
            token
            for token in word_tokenize(normalized)
            if token and token not in self.stop_words and token.isalnum()
        ]

        frequency = Counter(tokens)
        return frequency.most_common(max_keywords)

    def _ensure_nltk_resources(self) -> None:
        """Ensure NLTK corpora exist."""
        resources: Iterable[str] = ("punkt", "stopwords")
        for resource in resources:
            try:
                nltk.data.find(f"*/*/{resource}")
            except LookupError:
                nltk.download(resource, download_dir=NLTK_DIR, quiet=True)
