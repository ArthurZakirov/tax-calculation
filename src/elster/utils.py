import json
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def round_abs_sum_item(series: pd.Series) -> float:
    return round(abs(series.sum().item()), 2)

def sum_of_category_abs(df: pd.DataFrame, category: str, column: str="ELSTER Kategorie") -> float:
    return round_abs_sum_item(df[df[column].str.contains(category)]["Amount (EUR)"])


def load_processed_transactions():
    return pd.read_csv(os.getenv("PROCESSED_TRANSACTIONS"))


def load_elster_schema(schema_path="elster_schema.json"):
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)