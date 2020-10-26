import config
import elasticsearch as es
from elasticsearch import helpers as eshelp
import helpers
import decouple
import os

elastic = es.Elasticsearch([{"host" : config.ELASTIC_URL, "port": config.ELASTIC_PORT}])

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
    index_name =  test + file[:-13]
    index_names = index_names.append(index_name)
    print("Create " + index_name + " index.", flush=True)
    helpers.check_and_delete(index_name, elastic)
    eshelp.bulk(elastic, helpers.doc_generator(index_name, index_name, config.NECKAR_KEYS))

response = ["Created the indizes\n"]
for index in index_names:
    response = response.append("  + " + index + "\n")

response = response.append("on elasticsearch instance " + config.ELASTIC_URL + ":" + config.ELASTIC_PORT + ".")
print(response, flush=True)