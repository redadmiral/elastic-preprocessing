import pandas as pd
import gensim
import numpy as np
import decouple
import time

if decouple.config("PRODUCTION") == "True":
    print("Write to production indices.", flush=True)
    test = ""
else:
    print("Write to test indices.", flush=True)
    test = "_head"

## LABELS
print(time.ctime() + ": Get labels...", flush=True)
labels = pd.read_csv("data/labels_de" + test + ".ttl", sep = " ", skiprows=1)
labels.columns = ["de_url", "pred", "label", "dot"]
labels = labels[["de_url", "label"]]
labels["de_url"] = labels["de_url"].str.replace("<", "")
labels["de_url"] = labels["de_url"].str.replace(">", "")

labels["label"] = labels["label"].str.replace("@de", "")

## GET ALTLABELS
print(time.ctime() + ": Get altlabels...", flush=True)
altlabels = pd.read_csv("data/redirects_de" + test + ".ttl", sep = " ", skiprows=1)
altlabels.columns = ["label", "pred", "de_url", "dot"]
altlabels = altlabels[["de_url", "label"]]
altlabels["de_url"] = altlabels["de_url"].str.replace("<", "").str.replace(">", "")
altlabels["label"] = altlabels["label"].str.split("/").str[-1].str.replace(">", "")
altlabels["label"] = altlabels["label"].str.replace("_", " ")

labels = labels.append(altlabels)
print(time.ctime() + ": Merge language links...", flush=True)
## MERGE WITH LANGUAGE LINKS
langlinks = pd.read_csv("data/interlinks_de" + test + ".ttl", sep = " ", skiprows=1)
langlinks.columns = ["de_url", "pred", "url", "dot"]
langlinks = langlinks[["de_url", "url"]]
langlinks["de_url"] = langlinks["de_url"].str.replace("<", "").str.replace(">", "")
langlinks["url"] = langlinks["url"].str.replace("<", "").str.replace(">", "")
labels = labels.merge(langlinks, how="outer")

print(time.ctime() + ": Load vectors...", flush=True)
## LOAD VECTORS
#keyed_vectors = gensim.models.KeyedVectors.load("data/dbpedia_500_4_sg_200_vectors.kv")
#vectors = keyed_vectors.vectors
#urls = keyed_vectors.index2word

print(time.ctime() + ": Flatten and create DF...", flush=True)
vectors = np.genfromtxt("data/vectorshead.csv", delimiter = ", ")
vectors = list(map(str, vectors.tolist()))
urls = list(pd.read_csv("data/urlshead.csv", header=None)[0])

embeddings = pd.DataFrame(list(zip(urls, vectors)), columns=["url", "embedding"])
embeddings["url"] = embeddings["url"].str.replace("dbr:", "http://dbpedia.org/resource/")

print(time.ctime() + ": Merge embeddings with labels...", flush=True)
labels = labels.merge(embeddings, how="outer")

print(time.ctime() + ": Write to disk...", flush=True)
labels.to_csv("gerbil_index.csv")
