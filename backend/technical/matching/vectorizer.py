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
        Convert a spec dictionary into a normalized text string.
        This text will be embedded by the model.
        """

        parts = []

        for key in ["voltage", "conductor", "insulation", "standard"]:
            value = spec.get(key)
            if value:
                parts.append(f"{key}:{value}")

        attrs = spec.get("attributes", {})
        for key, value in attrs.items():
            if value:
                parts.append(f"{key}:{value}")

        return " | ".join(parts)

    def vectorize_spec(self, spec: dict) -> np.ndarray:
        """
        Convert a single spec into an embedding vector.
        """

        text = self._spec_to_text(spec)
        vector = self.model.encode(text)

        return vector

    def vectorize_many(self, specs: list) -> np.ndarray:
        """
        Convert multiple specs into embedding vectors.
        """

        texts = [self._spec_to_text(spec) for spec in specs]
        vectors = self.model.encode(texts)

        return vectors