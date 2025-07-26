import os
import pandas as pd
from dotenv import load_dotenv
from notion2pandas import Notion2PandasClient
from src.etl.pipelines import process_fn

load_dotenv()
processed_path = os.getenv("PROCESSED_TRANSACTIONS")
BANKS = ["PSD", "N26"]
NOTION_TOKEN = "NOTION"
TOKENS = {key: os.getenv(key) for key in BANKS}

n2p = Notion2PandasClient(auth=os.getenv(NOTION_TOKEN))
dfs = [
    process_fn[bank](n2p.from_notion_DB_to_dataframe(TOKENS[bank])) for bank in BANKS
]
df = pd.concat(dfs, ignore_index=True, axis=0)
df.to_csv(processed_path, index=False)