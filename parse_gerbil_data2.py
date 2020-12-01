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

mergestyle = "inner"

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

## GET PR
pr = pd.read_csv("data/rdf2vec/dbp_pr" + test + ".nt", sep=" ")
pr.columns = ["de_url", "pred", "pr", "dot"]
pr = pr[["de_url", "pr"]]
pr["de_url"] = pr["de_url"].str.replace("<", "").str.replace(">", "")
pr["pr"] = pr["pr"].str[:-42]
labels = labels.merge(pr, how=mergestyle)


print(time.ctime() + ": Load vectors...", flush=True)
## LOAD VECTORS

vectors = np.load("data/rdf2vec/embeddings.npy", allow_pickle=True)
urls = np.load("data/rdf2vec/entities.npy", allow_pickle=True)

print(time.ctime() + ": Flatten and create DF...", flush=True)
vectors = list(map(str, vectors.tolist()))

embeddings = pd.DataFrame(list(zip(urls, vectors)), columns=["de_url", "embedding"])

print(time.ctime() + ": Merge embeddings with labels...", flush=True)
labels = labels.merge(embeddings, how=mergestyle)

print(time.ctime() + ": Write to disk...", flush=True)
labels.columns = ["id", "label", "pr", "embedding"]
labels.to_csv("data/gerbil_index_" + mergestyle + ".csv")
