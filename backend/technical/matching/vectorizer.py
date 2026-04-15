from sentence_transformers import SentenceTransformer
import numpy as np


class SpecVectorizer:
    """
    Converts RFP specs and SKU specs into embedding vectors
    for similarity search.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def _spec_to_text(self, spec: dict) -> str:
        """
        Convert a spec dictionary into a normalized natural language string.
        """

        if not spec:
            return "unknown cable specification"

        parts = []

        # Core fields (make them natural language)
        mapping = {
            "voltage": "Voltage rating",
            "conductor": "Conductor material",
            "insulation": "Insulation type",
            "standard": "Standard"
        }

        for key, label in mapping.items():
            value = spec.get(key)
            if value:
                parts.append(f"{label} is {value}")

        # Additional attributes
        attrs = spec.get("attributes", {})
        for key, value in attrs.items():
            if value:
                parts.append(f"{key} is {value}")

        # Fallback safety
        if not parts:
            return "general cable specification"

        return ". ".join(parts)

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        """
        Normalize vectors for cosine similarity.
        """
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / (norms + 1e-10)

    def vectorize_spec(self, spec: dict) -> np.ndarray:
        """
        Convert a single spec into a normalized embedding vector.
        """

        text = self._spec_to_text(spec)

        vector = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=False
        )

        vector = self._normalize(vector.reshape(1, -1))[0]

        return vector

    def vectorize_many(self, specs: list) -> np.ndarray:
        """
        Convert multiple specs into normalized embedding vectors.
        """

        texts = [self._spec_to_text(spec) for spec in specs]

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=False
        )

        vectors = self._normalize(vectors)

        return vectors