import elasticsearch as es
import warnings


def doc_generator(df, index_name: str):
    df_iter = df.iterrows()
    for index, document in df_iter:
        yield {
                "_index": index_name,
                "_id": f"{document['id']}",
                "_source": {key: value for key, value in document.items()},
            }

def check_and_delete(index_name: str, es_client: es.Elasticsearch):
    if es_client.indices.exists(index_name):
        es_client.indices.delete(index_name)
        warnings.warn("Existing elasticSearch index " + index_name + " deleted.")