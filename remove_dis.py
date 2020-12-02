import pandas as pd
import decouple
from typing import List
import logging

logging.basicConfig(format='%(asctime)s %(message)s', filename="preprocessing.log", level=logging.INFO)

if decouple.config("PRODUCTION") == "True":
    logging.info("Write to production indices.")
    test = ""
else:
    logging.info("Write to test indices.")
    test = "_head"

def ttl2df(path: str, colnames: List[str], keep_pred: bool = False) -> pd.DataFrame:
    if len(colnames) != 3:
        raise KeyError("colnames must be of length 3. Ttl files must contain three cols.")

    ttl = pd.read_csv("data/rdf2vec/disambiguations_lang=de" + test + ".ttl", sep=" ")
    colnames.append("dot")
    ttl.columns = colnames
    ttl = ttl.drop("dot", axis=1)

    if not keep_pred:
        ttl = ttl.drop(colnames[1], axis = 1)

    for col in ttl.columns:
        ttl[col] = ttl[col].str.replace("<", "").str.replace(">", "")

    return ttl

logging.info("Read in index.")
index = pd.read_csv("data/rdf2vec/rdf2vec_index_inner" + test + ".csv")
logging.info("Read in disambiguation links.")
dislinks = ttl2df("data/rdf2vec/disambiguations_lang=de" + test + ".ttl", colnames=["id", "pred", "obj"])
dislinks = dislinks.drop("obj", axis=1)
logging.info("Merge dataframes.")
index_wo_dislinks = index.merge(dislinks, on=["id", "id"], how="outer", indicator=True)
logging.info("Remove disambiguation links from index.")
index_wo_dislinks = index_wo_dislinks[index_wo_dislinks["_merge"] == "left_only"]
index_wo_dislinks = index_wo_dislinks.drop(columns = ["Unnamed: 0", "_merge"])
logging.info("Write new index to disk.")
index_wo_dislinks.to_csv("data/rdf2vec/rdf2vec_index_wodis.csv", index=False)