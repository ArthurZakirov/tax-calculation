import json
from argparse import ArgumentParser
import os
from src.elster.utils import load_elster_schema, load_processed_transactions
from src.elster.einnahme_ueberschuss_rechnung import calculate_eur


def parse_args():
    parser = ArgumentParser(description="Run EÜR calculation for ELSTER.")
    parser.add_argument(
        "--processed_path",
        type=str,
        default=os.getenv("PROCESSED_TRANSACTIONS"),
        help="Path to processed transactions.",
    )
    parser.add_argument(
        "--euer_output_path",
        type=str,
        default="euer_output.json",
        help="Path to save EÜR output.",
    )
    return parser.parse_args()


def run_elster_calculation(processed_path, euer_output_path):
    """Run the EÜR calculation and save the results."""
    df = load_processed_transactions(processed_path)
    elster_schema = load_elster_schema()

    results = calculate_eur(df=df, schema=elster_schema)

    with open(euer_output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    args = parse_args()
    run_elster_calculation(args.processed_path, args.euer_output_path)
