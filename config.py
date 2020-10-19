NECKAR_PATH = "data/neckar_head.json"
RANK_PATH = "data/test.csv"
RANK_OUTPUT_PATH = "data/pr_index.csv"

EMBEDDINGS_PATH = "data/test.bla.gz"
EMBEDDINGS_OUTPUT_PATH = "data/embeddings_index.csv"

ELASTIC_URL = "141.13.94.164"
ELASTIC_PORT = 9200

# Keys from neckar file, which shall be in the es index
NECKAR_KEYS = ["wd_url", "wp_url", "dbp_id", "label"]
PR_KEYS = ["pr"]
EMBEDDINGS_KEYS = ["embedding"]

# names of indices
EMBEDDING_INDEX_NAME = "embedding_index"
PR_INDEX_NAME = "pr_index"
NECKAR_INDEX_NAME = "neckar_index"