"""
Keyword extraction helper built on NLTK for lightweight NLP processing.
Used by multiple agents to normalize skills and job requirements.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from typing import Iterable, List, Tuple

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# -----------------------------------------
# 🔥 FIX: Auto-download resources for Streamlit Cloud
# -----------------------------------------
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)     # Streamlit Cloud needs this
nltk.download("stopwords", quiet=True)
# -----------------------------------------

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Simple keyword extraction based on tokenization and frequency counts."""

    def __init__(self, language: str = "english") -> None:
        self.language = language
        self._ensure_nltk_resources()
        self.stop_words = set(stopwords.words(language))

    def extract(self, text: str, max_keywords: int = 25) -> List[Tuple[str, int]]:
        """
        Extract ranked keywords from text.

        Args:
            text: Free-form text input.
            max_keywords: Maximum keywords to return.

        Returns:
            List of (keyword, frequency) tuples sorted by frequency.
        """
        if not text:
            return []

        normalized = re.sub(r"[^A-Za-z0-9\s]+", " ", text.lower())

        tokens = [
            token
            for token in word_tokenize(normalized)
            if token and token not in self.stop_words and token.isalnum()
        ]

        frequency = Counter(tokens)
        logger.debug("Extracted %s unique keywords", len(frequency))
        return frequency.most_common(max_keywords)

    def _ensure_nltk_resources(self) -> None:
        """Ensure required NLTK corpora exist, otherwise download."""
        resources: Iterable[str] = ("punkt", "stopwords", "punkt_tab")
        for resource in resources:
            try:
                nltk.data.find(f"tokenizers/{resource}")
            except LookupError:
                logger.info("Downloading NLTK resource: %s", resource)
                nltk.download(resource, quiet=True)
