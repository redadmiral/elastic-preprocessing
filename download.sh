#! /bin/bash

echo Download wikidata embeddings...
curl https://dl.fbaipublicfiles.com/torchbiggraph/wikidata_translation_v1.tsv.gz | gunzip - | grep wikidata | gzip > wikidata_translation_v1.tsv.gz

echo Download DBPedia embeddings - Depth 4 - 100 dimensions - SkipGram
curl http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_sg_100/dbpedia_500_4_sg_100_vectors.kv -o dbpedia_500_4_sg_100_vectors.kv

echo Download DBPedia embeddings - Depth 4 - 200 dimensions - SkipGram
curl http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_sg_200/dbpedia_500_4_sg_200_vectors.kv -o dbpedia_500_4_sg_200_vectors.kv

echo Download DBPedia embeddings - Depth 4 - 200 dimensions - CBOW
curl http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_cbow_200/dbpedia_500_4_cbow_200_v2.kv -o dbpedia_500_4_cbow_200_v2.kv

echo Download DBPedia interlanguage Links
curl https://downloads.dbpedia.org/repo/dbpedia/generic/interlanguage-links/2016.10.01/interlanguage-links_lang=de.ttl.bz2 -o interlanguage-links_lang=de.ttl.bz2
bunzip2 -c interlanguage-links_lang=de.ttl.bz2 | grep http://dbpedia.org/resource > interlanguage-links_de_en.ttl

echo Download NECKar dump...
curl -L http://event.ifi.uni-heidelberg.de/wp-content/uploads/2017/05/WikidataDELODLinks_20170320_NECKAR_1_0.json_.gz -o neckar.json.gz

echo Download PageRank...
curl -v -XPOST -H "accept: text/csv" -d 'query=PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>PREFIX skos: <http://www.w3.org/2004/02/skos/core#>select ?item ?rank        where { 	?item rdfs:label ?label.    ?item rank:hasRDFRank ?rank.}' -o response_pr.json 'https://vm14.frontend.kinf.wiai.uni-bamberg.de/repositories/wikidata'

echo Download altLabels:
curl -v -XPOST -H "accept: text/csv" -d 'query=PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>PREFIX rank: <http://www.ontotext.com/owlim/RDFRank#>PREFIX skos: <http://www.w3.org/2004/02/skos/core#>select ?item ?altLabel        where { 	?item rdfs:label ?label.    ?item skos:altLabel ?altLabel.}' -o response_altlabels.json 'https://vm14.frontend.kinf.wiai.uni-bamberg.de/repositories/wikidata'


echo Create folder structure
mkdir data
mv wikidata_translation_v1.json data/
mv neckar.json.gz data/
mv response_altlabels.json response_pr.json data/

echo Unpack neckar.json.gz
cd data/ || exit
gzip -d < neckar.json.gz > neckar.json

echo Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip -r install requirements.txt

echo Finished. Please continue by executing python create_index.py.
