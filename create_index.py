import config
import json
from typing import Dict
import pandas as pd
import elasticsearch as es
from elasticsearch import helpers as eshelp
import helpers
import gzip
import io
from typing import List

elastic = es.Elasticsearch([{"host" : config.ELASTIC_URL, "port": config.ELASTIC_PORT}])
neckar: pd.DataFrame = pd.DataFrame()

total_lines: int = 1200000
linecount: int = 0
print("Load NECKar dataset...")
with open(config.NECKAR_PATH) as f:
    for line in f:
        if linecount % 10000 == 0:
            print("Loading NECKar dataset line " + str(linecount) + " (" + str(round(linecount/total_lines*100, 2)) + "%).")
        js: Dict = json.loads(line)
        df = [[("").join(["http://www.wikidata.org/entity/", js["WD_id"]]), js["WP_id_URL"], js["dbpedia_URL"], js["label"], js["neClass"]]]
        neckar = neckar.append(df)

print("Remove duplicate entries...")
neckar.columns = ["wd_url", "wp_url", "dbp_id", "label", "neClass"]
neckar.to_csv(config.NECKAR_FILTERED_PATH)

print("Create neckar_index...")

helpers.check_and_delete(config.NECKAR_INDEX_NAME, elastic)

eshelp.bulk(elastic, helpers.doc_generator(neckar, config.NECKAR_INDEX_NAME, config.NECKAR_KEYS))

legit_ids: set = set(neckar["wd_url"])
print(legit_ids)

#res = elastic.get(index="neckar_index", id = "Q100")
#print(res["_source"])

print("Load PageRank data...")
with open(config.RANK_PATH) as f:
    pr = pd.read_csv(f)

pr = pr.drop(columns="label")
pr.columns = ["wd_url", "pr"]

print("Delete everything that's not PER, LOC or ORG...")
pr = pr[pr["wd_url"].isin(legit_ids)]

print("Write PageRank index as CSV...")
pr.to_csv(config.RANK_FILTERED_PATH)


print("Create PR index...")
helpers.check_and_delete(config.PR_INDEX_NAME, elastic)
eshelp.bulk(elastic, helpers.doc_generator(pr, config.PR_INDEX_NAME, config.PR_KEYS))

print("Load Altlabel data...")
with open(config.ALTLABELS_PATH) as f:
    labels = pd.read_csv(f)

labels.columns = ["wd_url", "altlabel"]

print("Delete everything that's not PER, LOC or ORG...")
labels = labels[labels["wd_url"].isin(legit_ids)]

print("Write AltLabels index as CSV...")
labels.to_csv(config.ALTLABELS_FILTERED_PATH)


print("Create AltLabel index...")
helpers.check_and_delete(config.ALTLABELS_INDEX_NAME, elastic)
eshelp.bulk(elastic, helpers.doc_generator(labels, config.ALTLABELS_INDEX_NAME, config.ALTLABELS_INDEX_NAME))


print("Load Embeddings...")
embeddings = pd.DataFrame()

with io.TextIOWrapper(io.BufferedReader(gzip.open(config.EMBEDDINGS_PATH))) as file:
    for line in file:
        line_parts: List[str] = line.split("\t")
        wd_url: str = line_parts[0][1:-1]
        if wd_url in legit_ids:
            print(wd_url)
            embedding: List[float] = [float(i) for i in line_parts[1:]]
            embeddings = embeddings.append([[wd_url, embedding]])
embeddings.columns = ["wd_url", "embedding"]

print("Create embedding index...")

helpers.check_and_delete(config.EMBEDDING_INDEX_NAME, elastic)
eshelp.bulk(elastic, helpers.doc_generator(embeddings, config.EMBEDDING_INDEX_NAME, config.EMBEDDINGS_KEYS))

print("Indices created successfully.")