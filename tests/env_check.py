import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import pdfplumber

print("✅ Basic imports successful")

# Test embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
vec1 = model.encode("Copper conductor cable 1.1kV")
vec2 = model.encode("Aluminium conductor cable 1.1kV")

print("Embedding shape:", vec1.shape)

# Test similarity
sim = cosine_similarity([vec1], [vec2])[0][0]
print("Cosine similarity computed:", sim)

# Test FAISS
index = faiss.IndexFlatL2(vec1.shape[0])
index.add(np.array([vec1, vec2]))
distances, indices = index.search(np.array([vec1]), 2)

print("FAISS search works:", indices)

print("🎉 ALL DEPENDENCIES WORKING CORRECTLY")
