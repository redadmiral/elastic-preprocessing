from typing import Dict, List
import elasticsearch as es
import warnings

def filterKeys(document: Dict[str, str], keys: List[str]):
    return {key: document[key] for key in keys}

def doc_generator(df, index_name: str, keys:List[str], type:str ="_doc"):
    df_iter = df.iterrows()
    for index, document in df_iter:
        yield {
                "_index": index_name,
                "_type": type,
                "_id" : f"{document['wd_url']}",
                "_source": filterKeys(document, keys),
            }

def check_and_delete(index_name: str, es_client: es.Elasticsearch):
    if es_client.indices.exists(index_name):
        es_client.indices.delete(index_name)
        warnings.warn("Existing elasticSearch index " + index_name + " deleted.")

def linecount(linecount: int):
        linecount = linecount + 1
        if linecount % 50000 == 0:
            print("Loading Line" + str(linecount) +".\n")