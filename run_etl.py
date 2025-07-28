import os
import pandas as pd
from argparse import ArgumentParser
from dotenv import load_dotenv
from notion2pandas import Notion2PandasClient
from src.etl.pipelines import process_fn
from src.tax.tax import determine_tax_obligations

load_dotenv()
NOTION_TOKEN = "NOTION"


def parse_args():
    parser = ArgumentParser(description="Run ETL pipeline for tax calculation.")
    parser.add_argument(
        "--processed_path",
        type=str,
        default=os.getenv("PROCESSED_TRANSACTIONS"),
        help="Path to save processed transactions.",
    )
    parser.add_argument(
        "--banks",
        type=str,
        nargs="+",
        default=["PSD", "N26", "STRIPE"],
        help="List of banks to process.",
    )
    return parser.parse_args()


def run_pipeline(banks, processed_path):
    TOKENS = {key: os.getenv(key) for key in banks}

    n2p = Notion2PandasClient(auth=os.getenv(NOTION_TOKEN))
    dfs = [
        process_fn[bank](n2p.from_notion_DB_to_dataframe(TOKENS[bank]))
        for bank in banks
    ]
    df = pd.concat(dfs, ignore_index=True, axis=0)
    df = determine_tax_obligations(df)
    print(df)
    df.to_csv(processed_path, index=False)


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.banks, args.processed_path)
