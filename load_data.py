import config
import elasticsearch as es
from elasticsearch import helpers as eshelp
import helpers
import decouple
import os
import pandas as pd
from typing import List

elastic = es.Elasticsearch([{"host": config.ELASTIC_URL, "port": config.ELASTIC_PORT}])

if decouple.config("PRODUCTION") == "True":
    print("Write to production indices.", flush=True)
    test = ""
else:
    print("Write to test indices.", flush=True)
    test = "test_"

files = os.listdir("data")
filtered_files = ["".join(["data/", s]) for s in files if "filtered" in s]
index_names = []


for file in filtered_files:
    index_name = test + file[5:-13]
    index_names.append(index_name)
    print("Create " + index_name + " index.", flush=True)
    csv = pd.read_csv(file)
    if "embedding" in csv.columns:
        csv["embedding"] = list(csv["embedding"])
        helpers.check_and_delete(index_name, elastic)
    eshelp.bulk(elastic, helpers.doc_generator(csv, index_name))

response: List[str] = ["Created the indices\n"]

for index in index_names:
    response.append("  + " + index + "\n")
response.append("on elasticsearch instance " + config.ELASTIC_URL + ":" + str(config.ELASTIC_PORT) + ".")

print("".join(response), flush=True)