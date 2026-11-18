"""
Vector Store Module.

Provides the VectorStore class responsible for local vector indexing,
chunk persistence, and cosine similarity search over document embeddings.
"""

import os
import pickle
from typing import Any, List, Tuple, Optional
import numpy as np

from .chunker import DocumentChunk
from utils.logger import setup_logger
from utils.exceptions import DocumentException
from config import config

logger = setup_logger("documents.vector_store", config.log_level)


class VectorStore:
    """Local vector index manager supporting cosine similarity search and index persistence."""

    def __init__(self) -> None:
        """Initialize empty VectorStore."""
        self._chunks: List[DocumentChunk] = []
        self._embeddings: Optional[np.ndarray] = None
        self._faiss_index: Optional[Any] = None

    def add_embeddings(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """
        Add document chunks and their corresponding embedding vectors to the index.

        Args:
            chunks (List[DocumentChunk]): Document chunk metadata objects.
            embeddings (List[List[float]]): Corresponding numerical vector embeddings.

        Raises:
            DocumentException: If chunk and embedding counts do not match.
        """
        if len(chunks) != len(embeddings):
            raise DocumentException(f"Mismatch between chunk count ({len(chunks)}) and embedding count ({len(embeddings)}).")

        if not chunks:
            logger.warning("No chunks provided to VectorStore.")
            return

        self._chunks = chunks
        matrix = np.array(embeddings, dtype=np.float32)

        # Normalize vectors for cosine similarity
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._embeddings = matrix / norms

        # Attempt to build FAISS IndexFlatIP if faiss is available
        try:
            import faiss
            dim = self._embeddings.shape[1]
            self._faiss_index = faiss.IndexFlatIP(dim)
            self._faiss_index.add(self._embeddings)
            logger.info("Added %d vectors to FAISS IndexFlatIP (dimension: %d).", len(chunks), dim)
        except Exception as e:
            logger.info("FAISS unavailable (%s). Utilizing NumPy cosine similarity index.", e)
            self._faiss_index = None

        logger.info("VectorStore indexed %d document chunks successfully.", len(self._chunks))

    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """
        Perform top-k similarity search for a query embedding vector.

        Args:
            query_embedding (List[float]): Query vector.
            top_k (int): Number of top matching document chunks to return.

        Returns:
            List[Tuple[DocumentChunk, float]]: List of (DocumentChunk, similarity_score) tuples.

        Raises:
            DocumentException: If index is empty.
        """
        if not self._chunks or self._embeddings is None:
            raise DocumentException("VectorStore index is empty. Build index before searching.")

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        top_k = min(top_k, len(self._chunks))

        # FAISS search
        if self._faiss_index is not None:
            try:
                q_matrix = np.expand_dims(q_vec, axis=0)
                scores, indices = self._faiss_index.search(q_matrix, top_k)
                results: List[Tuple[DocumentChunk, float]] = []
                for score, idx in zip(scores[0], indices[0]):
                    if 0 <= idx < len(self._chunks):
                        results.append((self._chunks[idx], float(score)))
                return results
            except Exception as e:
                logger.warning("FAISS search failed (%s); falling back to NumPy search.", e)

        # NumPy Cosine Similarity fallback
        similarities = np.dot(self._embeddings, q_vec)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            results.append((self._chunks[idx], score))

        logger.debug("VectorStore search returned %d matches for top_k=%d.", len(results), top_k)
        return results

    def save_index(self, dir_path: str) -> None:
        """
        Persist vector index and metadata to disk.

        Args:
            dir_path (str): Storage directory path.
        """
        os.makedirs(dir_path, exist_ok=True)
        chunks_file = os.path.join(dir_path, "vector_chunks.pkl")
        embeddings_file = os.path.join(dir_path, "vector_embeddings.npy")

        with open(chunks_file, "wb") as f:
            pickle.dump(self._chunks, f)

        if self._embeddings is not None:
            np.save(embeddings_file, self._embeddings)

        logger.info("Persisted VectorStore index (%d chunks) to '%s'.", len(self._chunks), dir_path)

    def load_index(self, dir_path: str) -> bool:
        """
        Reload existing vector index and chunk metadata from disk.

        Args:
            dir_path (str): Storage directory path.

        Returns:
            bool: True if index loaded successfully, False otherwise.
        """
        chunks_file = os.path.join(dir_path, "vector_chunks.pkl")
        embeddings_file = os.path.join(dir_path, "vector_embeddings.npy")

        if not os.path.isfile(chunks_file) or not os.path.isfile(embeddings_file):
            return False

        try:
            with open(chunks_file, "rb") as f:
                self._chunks = pickle.load(f)

            self._embeddings = np.load(embeddings_file)

            # Rebuild FAISS index if available
            try:
                import faiss
                dim = self._embeddings.shape[1]
                self._faiss_index = faiss.IndexFlatIP(dim)
                self._faiss_index.add(self._embeddings)
            except Exception:
                self._faiss_index = None

            logger.info("Successfully reloaded VectorStore index (%d chunks) from '%s'.", len(self._chunks), dir_path)
            return True
        except Exception as e:
            logger.warning("Failed to reload vector index from '%s': %s", dir_path, e)
            return False
