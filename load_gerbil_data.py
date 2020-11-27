import config
import elasticsearch as es
from elasticsearch import helpers as eshelp
import helpers
import decouple
import os
import pandas as pd
from typing import List
import time
elastic = es.Elasticsearch([{"host": config.ELASTIC_URL, "port": config.ELASTIC_PORT}])

if decouple.config("PRODUCTION") == "True":
    print("Write to production indices.", flush=True)
    test = ""
else:
    print("Write to test indices.", flush=True)
    test = "test_"

print(time.ctime() + ": Delete rows with NA value in column label.", flush=True)
file = "data/gerbil_index.csv"
index_name = test + "gerbil_dbpsg200"
csv = pd.read_csv(file)
csv = csv[(csv["label"].notna())]

print(time.ctime() + "Create index " + index_name + " on " + config.ELASTIC_URL + ":" + str(config.ELASTIC_PORT), flush=True)
if "embedding" in csv.columns:
    helpers.check_and_delete(index_name, elastic)
    eshelp.bulk(elastic, helpers.doc_generator(csv, index_name))

print("Write to disk...", flush=True)

csv.to_csv(index_name + "noNaN.csv")