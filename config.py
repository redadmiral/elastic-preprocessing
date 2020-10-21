from decouple import config, UndefinedValueError

test: str = "test_"

try:
    if config("PRODUCTION") == True:
        test = ""
except UndefinedValueError:
    raise UndefinedValueError("Please define an environment variable 'PRODUCTION' with value True or False. If set to true production indices of elastic search will be overwritten.")

## elastic search credentials
ELASTIC_URL = "141.13.94.164"
ELASTIC_PORT = 9200

# check for production env to avoid overwriting es indices

# all file paths from this elastic-pp directory

# input files
NECKAR_PATH = "data/neckar.json"
RANK_PATH = "data/response_pr.csv"
EMBEDDINGS_PATH = "data/wikidata_translation_v1.tsv.gz"
ALTLABELS_PATH = "data/response_altLabels.csv"

# path to output files
NECKAR_FILTERED_PATH = "data/neckar_filtered.csv"
RANK_FILTERED_PATH = "data/pr_filtered.csv"
EMBEDDINGS_FILTERED_PATH = "data/embeddings_filtered.csv"
ALTLABELS_FILTERED_PATH = "data/altlabels_filtered.csv"

# Keys from neckar file, which shall be in the es index
NECKAR_KEYS = ["wd_url", "wp_url", "dbp_url", "label", "class"]
PR_KEYS = ["pr"]
EMBEDDINGS_KEYS = ["embedding"]
ALTLABELS_KEYS = ["altlabel", "wd_url"]

# names of indices
EMBEDDING_INDEX_NAME = test + "embedding_index"
PR_INDEX_NAME = test + "pr_index"
NECKAR_INDEX_NAME = test + "neckar_index"
ALTLABELS_INDEX_NAME = test + "altlabel_index"