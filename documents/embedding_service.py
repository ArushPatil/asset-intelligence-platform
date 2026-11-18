"""
Embedding Service Module.

Provides the EmbeddingService class responsible for generating dense vector embeddings
for document chunks and search queries, hiding vectorization details behind a clean API.
"""

from typing import Any, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from utils.logger import setup_logger
from utils.exceptions import DocumentException
from config import config

logger = setup_logger("documents.embedding", config.log_level)


class EmbeddingService:
    """Vector embedding generator for text chunks and natural language queries."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize EmbeddingService with optional transformer model preference.

        Args:
            model_name (str): Transformer model name string.
        """
        self.model_name = model_name
        self._transformer_model: Optional[Any] = None
        self._tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self._is_fitted: bool = False

        # Attempt to load SentenceTransformer if installed
        try:
            from sentence_transformers import SentenceTransformer
            self._transformer_model = SentenceTransformer(model_name)
            logger.info("Initialized SentenceTransformer model '%s'.", model_name)
        except Exception as e:
            logger.info("SentenceTransformers not available (%s). Utilizing high-performance TF-IDF vectorizer fallback.", e)
            self._tfidf_vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=1024,
                stop_words="english",
                sublinear_tf=True
            )

    def fit_corpus(self, texts: List[str]) -> None:
        """
        Fit corpus vocabulary if utilizing local vectorizer fallback.

        Args:
            texts (List[str]): List of text strings from document chunks.
        """
        if self._tfidf_vectorizer is not None:
            if not texts:
                raise DocumentException("Cannot fit embedding vectorizer on empty text corpus.")
            self._tfidf_vectorizer.fit(texts)
            self._is_fitted = True
            logger.info("Fitted TF-IDF embedding vectorizer on %d text chunks.", len(texts))

    def embed_text(self, text: str) -> List[float]:
        """
        Generate numerical vector embedding for a single text query or snippet.

        Args:
            text (str): Input text string.

        Returns:
            List[float]: High-dimensional vector representation.

        Raises:
            DocumentException: If vectorization fails.
        """
        if not text.strip():
            raise DocumentException("Cannot generate vector embedding for empty text string.")

        try:
            if self._transformer_model is not None:
                vec = self._transformer_model.encode(text, convert_to_numpy=True)
                return vec.tolist()

            if self._tfidf_vectorizer is not None:
                if not self._is_fitted:
                    self.fit_corpus([text])
                vec_sparse = self._tfidf_vectorizer.transform([text])
                vec_dense = vec_sparse.toarray()[0]
                # Normalize vector
                norm = np.linalg.norm(vec_dense)
                if norm > 0:
                    vec_dense = vec_dense / norm
                return vec_dense.tolist()

            raise DocumentException("No valid embedding model or vectorizer available.")

        except DocumentException:
            raise
        except Exception as e:
            logger.error("Failed to generate embedding for text snippet: %s", e)
            raise DocumentException(f"Embedding generation failed: {e}") from e

    def embed_chunks(self, texts: List[str]) -> List[List[float]]:
        """
        Generate vector embeddings for a list of document chunk texts.

        Args:
            texts (List[str]): List of chunk text strings.

        Returns:
            List[List[float]]: Matrix of vector embeddings.

        Raises:
            DocumentException: If chunk embedding generation fails.
        """
        if not texts:
            return []

        try:
            if self._transformer_model is not None:
                embeddings = self._transformer_model.encode(texts, convert_to_numpy=True, batch_size=32)
                logger.info("Generated %d embeddings via SentenceTransformer.", len(embeddings))
                return embeddings.tolist()

            if self._tfidf_vectorizer is not None:
                self.fit_corpus(texts)
                matrix_sparse = self._tfidf_vectorizer.transform(texts)
                matrix_dense = matrix_sparse.toarray()
                # Normalize rows
                norms = np.linalg.norm(matrix_dense, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                matrix_normalized = matrix_dense / norms
                logger.info("Generated %d embeddings via TF-IDF vectorizer.", len(matrix_normalized))
                return matrix_normalized.tolist()

            raise DocumentException("No valid embedding model available.")

        except DocumentException:
            raise
        except Exception as e:
            logger.error("Failed to generate embeddings for %d chunks: %s", len(texts), e)
            raise DocumentException(f"Chunk embedding generation failed: {e}") from e
