from decouple import config, UndefinedValueError
try:
    if config("PRODUCTION") == "True":
        test = ""
    else:
        test: str = "test_"
except UndefinedValueError:
    raise UndefinedValueError("Please define an environment variable 'PRODUCTION' with value True or False. If set to true production indices of elastic search will be overwritten.")

## elastic search credentials
ELASTIC_URL = "141.13.94.164"
ELASTIC_PORT = 9200

# all file paths from this elastic-pp directory

# input files
NECKAR_PATH = "data/WikidataDELODLinks_20170320_NECKAR_1_0.json"
RANK_PATH = "data/response_pr.csv"
EMBEDDINGS_PATH = "data/wikidata_translation_v1.tsv.gz"
LABELS_PATH = "data/response_labels.csv"
ALTLABELS_PATH = "data/response_altlabels.csv"

DBP_PATH = [
    "data/dbpedia_500_4_sg_100_vectors.kv",
    "data/dbpedia_500_4_cbow_200_v2.kv",
    "data/dbpedia_500_4_sg_200_vectors.kv"
]

DBP_LANGLINKS = "data/interlanguage-links_de_en.ttl"

# path to output files
NECKAR_FILTERED_PATH = "data/neckar_filtered.csv"
RANK_FILTERED_PATH = "data/pr_filtered.csv"
EMBEDDINGS_FILTERED_PATH = "data/embeddings_filtered.csv"
ALTLABELS_FILTERED_PATH = "data/altlabels_filtered.csv"
DBP_LANGLINKS_FILTERED = "data/interlanguage-links_de_en_parsed.csv"
