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

vectors = gensim.models.KeyedVectors.load("data/dbpedia_500_4_sg_200_vectors.kv")
url = vectors.index2word
vector = list(vectors.vectors)


vectors = pd.DataFrame(url, vector)
vectors.columns = ["url", "embedding"]
labels = labels.merge(vectors)

labels.to_csv("gerbil_index.csv")