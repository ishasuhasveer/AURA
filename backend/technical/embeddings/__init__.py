from sentence_transformers import SentenceTransformer
import numpy as np


class SpecEmbedder:
    """
    Converts RFP specifications or SKU specifications
    into embedding vectors using Sentence Transformers.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def spec_to_text(self, spec: dict) -> str:
        """
        Convert structured spec dictionary into
        a normalized text string for embedding.
        """

        parts = []

        # Core specs
        for field in ["voltage", "conductor", "insulation", "standard"]:
            value = spec.get(field)
            if value:
                parts.append(f"{field}:{value}")

        # Attributes
        attrs = spec.get("attributes", {})
        for key, value in attrs.items():
            if value:
                parts.append(f"{key}:{value}")

        return " | ".join(parts)

    def embed_spec(self, spec: dict) -> np.ndarray:
        """
        Generate embedding vector for one spec.
        """

        text = self.spec_to_text(spec)
        vector = self.model.encode(text)

        return vector

    def embed_many(self, specs: list) -> np.ndarray:
        """
        Generate embeddings for multiple specs.
        """

        texts = [self.spec_to_text(spec) for spec in specs]
        vectors = self.model.encode(texts)

        return vectors


if __name__ == "__main__":
    embedder = SpecEmbedder()

    sample_spec = {
        "voltage": "400 kV",
        "conductor": "COPPER",
        "insulation": "XLPE",
        "standard": "IEC 60502",
        "attributes": {
            "cross_section_mm2": 50,
            "armouring": "Armoured",
            "core_count": None
        }
    }

    vector = embedder.embed_spec(sample_spec)

    print("Embedding vector shape:", vector.shape)