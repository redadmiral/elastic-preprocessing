import config
import json
import pandas as pd
import gzip
import io
from typing import List
import time
import gensim
import os

###### NECKAR

if not os.path.isfile(config.NECKAR_FILTERED_PATH):
    starttime = time.time()
    print("No filtered NECKAR dataset found.\nParsing NECKar dataset...", flush=True)
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

    neckar.columns = ["class", "dbp_url", "wp_url", "id", "label"]
    neckar.drop("label")
    labels = pd.read_csv(config.LABELS_PATH)
    labels.colums = ["id", "label"]
    neckar.merge(right=labels, on="id")
    neckar.to_csv(config.NECKAR_FILTERED_PATH, index=False)
    endtime = time.time()
    print("NECKar evaluation time: " + str(endtime-starttime))
else:
    print("NECKAR dataset found. Extract IDs for mapping.", flush=True)
    neckar = pd.read_csv(config.NECKAR_FILTERED_PATH)

neckar.columns = ["class", "dbp_url", "wp_url", "wd_url", "label"]
legit_ids: set = set(neckar["wd_url"])
dbp_ids: pd.DataFrame = pd.DataFrame(label.replace("http://de.dbpedia.org/resource/", "dbr:") for label in neckar["dbp_url"])
dbp_ids["wd_url"] = neckar["wd_url"]
dbp_ids.columns = ["dbp_url", "wd_url"]

######### DBP

if not os.path.isfile(config.DBP_LANGLINKS_FILTERED):
    print("filtering dbp language links.")
    langlinks = pd.read_csv(config.DBP_LANGLINKS, sep=" ")
    langlinks.columns = ["dbp_url", "pred", "en", "."]
    langlinks = langlinks.drop(["pred", "."], axis=1)
    langlinks = langlinks.replace(regex={"<http://de.dbpedia.org/resource/": "dbr:","<http://dbpedia.org/resource/" : "dbr:", ">": ""})
    langlinks = langlinks.merge(right=dbp_ids, on="dbp_url")
    langlinks = langlinks.drop_duplicates()
    langlinks.to_csv(config.DBP_LANGLINKS_FILTERED, index = False)
else:
    print(config.DBP_LANGLINKS_FILTERED + " found.")
    langlinks = pd.read_csv(config.DBP_LANGLINKS_FILTERED)
    langlinks.columns = ["dbp_url", "en"]

legit_dbp_ids_orig: pd.DataFrame = langlinks.set_index("en")
legit_dbp_ids = legit_dbp_ids_orig.to_dict()

# this is ridiculously slow. maybe better extract the embeddings and labels,
# put them together, merge them into legits and hope for the best?
print("Load DBPedia embeddings...", flush=True)
for file in config.DBP_PATH:
    filtered_file = "".join([file[:-3], "_filtered.csv"])
    if not os.path.isfile(filtered_file):
        starttime = time.time()
        print("Parse file " + file, flush=True)
        embeddings: pd.DataFrame = pd.DataFrame()
        keyed_vectors = gensim.models.KeyedVectors.load(file)
        for id in legit_dbp_ids["dbp_url"]:
            try:
                embedding = keyed_vectors.get_vector(id).tolist()
                embeddings = embeddings.append([[legit_dbp_ids["dbp_url"][id], legit_dbp_ids["wd_url"][id], embedding]]) # assign the german dbp label
            except KeyError:
                pass
        try:
            embeddings.columns = ["dbp_url", "id", "embedding"]
            embeddings["dbp_url"] = [label.replace("dbr:", "http://de.dbpedia.org/resource/") for label in embeddings["dbp_url"]]
            print("Write as csv...")
            embeddings.to_csv(file[:-3] + "_filtered.csv", index=False)
        except ValueError:
            print(file + "_filtered.csv is empty. Will not write file.")
        endtime = time.time()
        print(file + " evaluation time: " + str(endtime - starttime), flush=True)
    else:
        print(filtered_file + " found.", flush=True)



########## PR

if not os.path.isfile(config.RANK_FILTERED_PATH):
    print("Load PageRank data...", flush=True)
    starttime = time.time()
    with open(config.RANK_PATH) as f:
        pr = pd.read_csv(f)

    pr.columns = ["wd_url", "pr"]

    print("Delete everything that's not PER, LOC or ORG...", flush=True)
    pr = pr[pr["wd_url"].isin(legit_ids)]

    print("Write PageRank index as CSV...", flush=True)
    pr.columns = ["id", "pr"]
    pr.to_csv(config.RANK_FILTERED_PATH, index=False)
    endtime = time.time()
    print("PR evaluation time: " + str(endtime-starttime), flush=True)
else:
    print("PR file found.", flush=True)

##### ALTLABELS

if not os.path.isfile(config.ALTLABELS_FILTERED_PATH):
    print("Load Altlabel data...", flush=True)
    starttime = time.time()
    with open(config.ALTLABELS_PATH) as f:
        labels = pd.read_csv(f)

    labels.columns = ["wd_url", "altlabel"]

    print("Delete everything that's not PER, LOC or ORG...", flush=True)
    labels = labels[labels["wd_url"].isin(legit_ids)]

    print("Write AltLabels index as CSV...", flush=True)
    labels.columns = ["id", "altlabel"]
    labels.to_csv(config.ALTLABELS_FILTERED_PATH, index=False)

    endtime = time.time()
    print("Altlabels evaluation time: " + str(endtime-starttime), flush=True)
else:
    print("Altlabels found.", flush=True)

####### EMBEDDINGS

if not os.path.isfile(config.EMBEDDINGS_FILTERED_PATH):
    print("Load Embeddings...", flush=True)
    embeddings = pd.DataFrame()
    starttime = time.time()

    with io.TextIOWrapper(io.BufferedReader(gzip.open(config.EMBEDDINGS_PATH))) as file:
        for line in file:
            line_parts: List[str] = line.split("\t")
            wd_url: str = line_parts[0][1:-1]
            if wd_url in legit_ids:
                embedding: List[float] = [float(i) for i in line_parts[1:]]
                embeddings = embeddings.append([[wd_url, embedding]])

    embeddings.columns = ["id", "embedding"]

    embeddings.to_csv(config.EMBEDDINGS_FILTERED_PATH, index=False)
    endtime = time.time()
    print("Embeddings evaluation time: " + str(endtime-starttime))
else:
    print(config.EMBEDDINGS_FILTERED_PATH + " found.", flush=True)

print("All files successfully parsed. Please run load_data.py.", flush=True)