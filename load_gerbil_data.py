import pandas as pd
import gensim

## LABELS

labels = pd.read_csv("data/labels_de.ttl", sep = " ", skiprows=1)
labels.columns = ["de_url", "pred", "label", "dot"]
labels = labels[["de_url", "label"]]
labels["de_url"] = labels["de_url"].str.replace("<", "")
labels["de_url"] = labels["de_url"].str.replace(">", "")

labels["label"] = labels["label"].str.replace("@de", "")

## GET ALTLABELS

altlabels = pd.read_csv("data/redirects_de.ttl", sep = " ", skiprows=1)
altlabels.columns = ["label", "pred", "de_url", "dot"]
altlabels = altlabels[["de_url", "label"]]
altlabels["de_url"] = altlabels["de_url"].str.replace("<", "").str.replace(">", "")
altlabels["label"] = altlabels["label"].str.split("/").str[-1].str.replace(">", "")
altlabels["label"] = altlabels["label"].str.replace("_", " ")

labels = labels.append(altlabels)

## MERGE WITH LANGUAGE LINKS
langlinks = pd.read_csv("data/interlinks_de.ttl", sep = " ", skiprows=1)
langlinks.columns = ["de_url", "pred", "url", "dot"]
langlinks = langlinks[["de_url", "url"]]
langlinks["de_url"] = langlinks["de_url"].str.replace("<", "").str.replace(">", "")
langlinks["url"] = langlinks["url"].str.replace("<", "").str.replace(">", "")
labels = labels.merge(langlinks)

## LOAD VECTORS
def get_vector(url: str, vectors: gensim.models.KeyedVectors):
    try:
        response = vectors.get_vector(url)
    except KeyError:
        response = None
    return response

keyed_vectors = gensim.models.KeyedVectors.load("data/dbpedia_500_4_sg_200_vectors.kv")

result = pd.DataFrame()

for row in labels.iterrows():
    try:
        id = ":".join(["dbr", row[1]["url"].split("/")[-1]])
        embedding = keyed_vectors.get_vector(id)
    except KeyError:
        embedding = None
    result = result.append([[row[1]["url"], row[1]["de_url"], row[1]["label"], embedding]])

result.to_csv("gerbil_index.csv")