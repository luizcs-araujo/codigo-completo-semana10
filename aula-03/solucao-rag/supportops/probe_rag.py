from supportops.rag.embeddings import HashEmbeddings
from supportops.rag.service import RagService, SearchFilters

service = RagService(embeddings=HashEmbeddings())
result = service.search("403 role cache dashboard", SearchFilters("analytics-api", "prod"))
for item in result["evidence"]:
    print(item["citation"], item["version"], item["fusion_score"])
