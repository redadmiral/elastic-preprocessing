#!/bin/bash

DATAFOLDER="data"
KB_URL="https://vm14.frontend.kinf.wiai.uni-bamberg.de/repositories/wikidata"

URLS=(
  "https://dl.fbaipublicfiles.com/torchbiggraph/wikidata_translation_v1.tsv.gz"
  "https://dumps.wikimedia.org/wikidatawiki/entities/latest-truthy.nt.gz"
  "http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_cbow_200/dbpedia_500_4_cbow_200_v2.kv"
  "http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_cbow_200/dbpedia_500_4_cbow_200_v2.kv.vectors.npy"
  "http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_sg_100/dbpedia_500_4_sg_100_vectors.kv"
  "http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_sg_100/dbpedia_500_4_sg_100_vectors.kv.vectors.npy"
  "http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_sg_200/dbpedia_500_4_sg_200_vectors.kv"
  "http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_sg_200/dbpedia_500_4_sg_200_vectors.kv.vectors.npy"
  "http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_cbow_100/dbpedia_500_4_cbow_100_v2.kv"
  "http://data.dws.informatik.uni-mannheim.de/kgvec2go/iswc/dbpedia_500_4_cbow_100/dbpedia_500_4_cbow_100_v2.kv.vectors.npy"
  "https://downloads.dbpedia.org/repo/dbpedia/generic/interlanguage-links/2016.10.01/interlanguage-links_lang=de.ttl.bz2"
  "http://event.ifi.uni-heidelberg.de/wp-content/uploads/2017/05/WikidataDELODLinks_20170320_NECKAR_1_0.json_.gz"
)

declare -A QUERIES
QUERIES=(
  ["pr"]="select ?item ?rank where {?item rdfs:label ?label. ?item rank:hasRDFRank ?rank.}"
  ["label"]="select ?item ?label where {?item rdfs:label ?label.}"
  ["altlabel"]="select ?item ?altLabel where {?item skos:altLabel ?altLabel.}"
)

PREFIXES=(
  "rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
  "rank: <http://www.ontotext.com/owlim/RDFRank#>"
  "skos: <http://www.w3.org/2004/02/skos/core#>"
)

function download() {
  FILENAME=$(basename $1)
  FILE=$DATAFOLDER/$FILENAME
  if ! test -f "$FILE";
  then
    echo Download $FILENAME
    curl $1 -o $DATAFOLDER/$FILENAME
  else
    echo File $FILE found.
  fi
}

function query() {
  FILENAME=response_$1.csv
  FILE=$DATAFOLDER/$FILENAME
  if ! test -f "$FILE";
  then
    echo Query $1...
    QUERY="query="
    for prefix in "${PREFIXES[@]}"; do
      QUERY="${QUERY} PREFIX ${prefix}"
    done

    QUERY="${QUERY} ${2}"
    curl -v -XPOST -H "accept: text/csv" -d "$QUERY" -o $DATAFOLDER/$FILENAME "$KB_URL"
  else
    echo File $FILE found.
  fi
}

for key in "${!QUERIES[@]}"; do
  query "$key" "${QUERIES[${key}]}"
done

for url in "${URLS[@]}"; do
  download $url
done

echo Handle files:

gzip -d < $DATAFOLDER/WikidataDELODLinks_20170320_NECKAR_1_0.json_.gz > $DATAFOLDER/WikidataDELODLinks_20170320_NECKAR_1_0.json
gzip -d < $DATAFOLDER/wikidata_translation_v1.tsv.gz | grep wikidata | gzip > $DATAFOLDER/wikidata_translation_v1.tsv.gz
gzip -d < $DATAFOLDER/latest-truthy.nt.gz | tee >(grep "@de" > tee >(grep "http://www.w3.org/2000/01/rdf-schema#label" > $DATAFOLDER/de_label.ttl) > (grep "http://www.w3.org/2004/02/skos/core#altLabel" > $DATAFOLDER/de_altlabel.ttl)) >(grep "@en" > tee >(grep "http://www.w3.org/2000/01/rdf-schema#label" > $DATAFOLDER/en_label.ttl) > (grep "http://www.w3.org/2004/02/skos/core#altLabel" > $DATAFOLDER/en_altlabel.ttl))
bunzip2 -c interlanguage-links_lang=de.ttl.bz2 | grep http://dbpedia.org/resource > $DATAFOLDER/interlanguage-links_de_en.ttl