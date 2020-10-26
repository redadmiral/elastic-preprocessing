import elasticsearch as es
import config

elastic = es.Elasticsearch([{"host" : config.ELASTIC_URL, "port": config.ELASTIC_PORT}])

