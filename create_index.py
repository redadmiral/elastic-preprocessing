import dask.dataframe as dd
import config
import json
from typing import Dict
import pandas as pd

ar: pd.DataFrame = pd.DataFrame()

## load neckar
with open(config.NECKAR_PATH) as f:
    for line in f:
        js: Dict = json.loads(line)
        df = [[("").join(["http://www.wikidata.org/entity/", js["WD_id"]]), js["dbpedia_URL"], js["label"]]]
        ar = ar.append(df)

ar.columns = ["wd_id", "dbp_id", "label"]
ar = ar.set_index('wd_id')
ar = ar.drop_duplicates()
print(ar)

## load pr

with open(config.RANK_PATH) as f:
    csv = pd.read_csv(f)

csv = csv.drop(columns="label")
csv.columns = ["wd_id", "pr"]
print(csv)

## merge sets

new_set = pd.merge(ar, csv, on="wd_id")
new_set.to_csv(config.OUTPUT_PATH)