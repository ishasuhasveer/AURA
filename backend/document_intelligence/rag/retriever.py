from sentence_transformers import SentenceTransformer, util
from typing import List, Dict


class ProductRetriever:
    """
    Phase 7: Semantic Retriever for OEM product specifications
    """

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.product_corpus = []
        self.product_embeddings = []

    def load_product_repository(self, products: List[Dict]):
        """
        Load OEM product specifications and build embeddings.
        """
        self.product_corpus = products
        texts = [p["spec_text"] for p in products]
        self.product_embeddings = self.model.encode(texts, convert_to_tensor=True)

    def retrieve(self, query_text: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-K most relevant product specs for an RFP query.
        """
        query_embedding = self.model.encode(query_text, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, self.product_embeddings)[0]

        top_results = scores.topk(k=top_k)

        retrieved = []
        for score, idx in zip(top_results.values, top_results.indices):
            product = self.product_corpus[int(idx)]
            retrieved.append({
                "sku": product["sku"],
                "similarity_score": round(float(score), 3),
                "spec_text": product["spec_text"]
            })

        return retrieved
if __name__ == "__main__":
    retriever = ProductRetriever()

    # Synthetic OEM product specs (allowed by PDF)
    products = [
        {
            "sku": "OEM_CABLE_25C_HDPE",
            "spec_text": "25 core copper cable with HDPE insulation rated for 3 KV"
        },
        {
            "sku": "OEM_CABLE_25C_PVC",
            "spec_text": "25 core PVC insulated copper control cable rated for 2 KV"
        },
        {
            "sku": "OEM_CABLE_12C_HDPE",
            "spec_text": "12 core HDPE insulated copper cable compliant with IS 8130"
        }
    ]

    retriever.load_product_repository(products)

    query = "25 core copper cable HDPE insulation 3 KV"
    results = retriever.retrieve(query)

    for r in results:
        print(r)

