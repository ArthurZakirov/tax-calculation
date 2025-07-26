import json
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


def sum_of_category_abs(df: pd.DataFrame, category: str) -> float:
    """
    Sums the absolute values of the 'Amount (EUR)' column for a given ELSTER category.
    """
    return abs(df[df["ELSTER Kategorie"].str.contains(category)]["Amount (EUR)"].sum())


def load_processed_transactions():
    return pd.read_csv(os.getenv("PROCESSED_TRANSACTIONS"))


def load_elster_schema(schema_path="elster_schema.json"):
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)