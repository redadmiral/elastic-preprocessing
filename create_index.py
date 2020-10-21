import config
import json
import pandas as pd
import elasticsearch as es
from elasticsearch import helpers as eshelp
import helpers
import gzip
import io
from typing import List
import time
elastic = es.Elasticsearch([{"host" : config.ELASTIC_URL, "port": config.ELASTIC_PORT}])

starttime = time.time()
print("Load NECKar dataset...", flush=True)
with open(config.NECKAR_PATH) as f:
    lines=f.read().splitlines()

print("Load as pandas df", flush=True)
df_inter = pd.DataFrame(lines)
df_inter.columns = ['json_element']

df_inter['json_element'].apply(json.loads)

neckar = pd.json_normalize(df_inter['json_element'].apply(json.loads))
neckar = neckar[['neClass', 'dbpedia_URL', 'WP_id_URL',
       'WD_id', 'label']]

neckar['WD_id'] = 'http://www.wikidata.org/entity/' + neckar['WD_id'].astype(str)

neckar.columns = ["class", "dbp_url", "wp_url", "wd_url", "label"]
neckar.to_csv(config.NECKAR_FILTERED_PATH)

endtime = time.time()
print("NECKar evaluation time: " + str(endtime-starttime))


print("Create neckar_index...", flush=True)

helpers.check_and_delete(config.NECKAR_INDEX_NAME, elastic)

eshelp.bulk(elastic, helpers.doc_generator(neckar, config.NECKAR_INDEX_NAME, config.NECKAR_KEYS))

legit_ids: set = set(neckar["wd_url"])
#print(legit_ids)

#res = elastic.get(index="neckar_index", id = "Q100")
#print(res["_source"])

print("Load PageRank data...", flush=True)

starttime = time.time()
with open(config.RANK_PATH) as f:
    pr = pd.read_csv(f)

pr.columns = ["wd_url", "pr"]

print("Delete everything that's not PER, LOC or ORG...", flush=True)
pr = pr[pr["wd_url"].isin(legit_ids)]

print("Write PageRank index as CSV...", flush=True)
pr.to_csv(config.RANK_FILTERED_PATH)

endtime = time.time()
print("PR evaluation time: " + str(endtime-starttime))


print("Create PR index...", flush=True)
helpers.check_and_delete(config.PR_INDEX_NAME, elastic)
eshelp.bulk(elastic, helpers.doc_generator(pr, config.PR_INDEX_NAME, config.PR_KEYS))

print("Load Altlabel data...", flush=True)
starttime = time.time()
with open(config.ALTLABELS_PATH) as f:
    labels = pd.read_csv(f)

labels.columns = ["wd_url", "altlabel"]

print("Delete everything that's not PER, LOC or ORG...", flush=True)
labels = labels[labels["wd_url"].isin(legit_ids)]

print("Write AltLabels index as CSV...", flush=True)
labels.to_csv(config.ALTLABELS_FILTERED_PATH)

endtime = time.time()
print("Altlabels evaluation time: " + str(endtime-starttime))


print("Create AltLabel index...", flush=True)
helpers.check_and_delete(config.ALTLABELS_INDEX_NAME, elastic)
eshelp.bulk(elastic, helpers.doc_generator(labels, config.ALTLABELS_INDEX_NAME, config.ALTLABELS_KEYS))


print("Load Embeddings...", flush=True)
embeddings = pd.DataFrame()
starttime = time.time()
with io.TextIOWrapper(io.BufferedReader(gzip.open(config.EMBEDDINGS_PATH))) as file:
    for line in file:
        line_parts: List[str] = line.split("\t")
        wd_url: str = line_parts[0][1:-1]
        if wd_url in legit_ids:
            print(wd_url)
            embedding: List[float] = [float(i) for i in line_parts[1:]]
            embeddings = embeddings.append([[wd_url, embedding]])

embeddings.columns = ["wd_url", "embedding"]

endtime = time.time()
print("Embeddings evaluation time: " + str(endtime-starttime))


print("Create embedding index...", flush=True)

helpers.check_and_delete(config.EMBEDDING_INDEX_NAME, elastic)
eshelp.bulk(elastic, helpers.doc_generator(embeddings, config.EMBEDDING_INDEX_NAME, config.EMBEDDINGS_KEYS))

print("Indices created successfully.", flush=True)