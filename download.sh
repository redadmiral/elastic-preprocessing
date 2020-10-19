#! /bin/bash

echo Download embeddings...
curl https://dl.fbaipublicfiles.com/torchbiggraph/wikidata_translation_v1.tsv.gz | gunzip - | grep wikidata | gzip > wikidata_translation_v1.tsv.gz

echo Download NECKar dump...
curl -L http://event.ifi.uni-heidelberg.de/wp-content/uploads/2017/05/WikidataDELODLinks_20170320_NECKAR_1_0.json_.gz -o neckar.json.gz
echo Download PageRank...
curl -v -XPOST -H "accept: application/json" -d 'query=PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>PREFIX skos: <http://www.w3.org/2004/02/skos/core#>select ?item ?rank        where { 	?item rdfs:label ?label.    ?item rank:hasRDFRank ?rank.} ' -o response_pr.json
echo Download altLabels:
curl -v -XPOST -H "accept: application/json" -d 'query=PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>PREFIX skos: <http://www.w3.org/2004/02/skos/core#>select ?item ?label (GROUP_CONCAT(?altLabel; SEPARATOR="\t") AS ?altLabels)         where { 	?item rdfs:label ?label.    ?item skos:altLabel ?altLabel.} GROUP BY ?item ?label' -o response_altlabels.json

echo Create folder structure
mkdir data
cp wikidata_translation_v1.json data/
cp neckar.json.gz data/

echo Finished. Please continue by executing python create_index.py.
