from argparse import ArgumentParser
import os
from src.elster.einkommens_steuererklaerung import calculate_est
from src.io_utils import load_processed_transactions
from src.io_utils import load_elster_schema
from src.elster.einnahme_ueberschuss_rechnung import (
    calculate_gewinn,
    calculate_eur,
    calculate_transfers,
)
from src.io_utils import write_results_to_json
from src.io_utils import log_results
from src.tax.tax import aggregate_tax_obligations


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
        default="output/euer_output.json",
        help="Path to save EÜR output.",
    )
    parser.add_argument(
        "--transaction_cols",
        nargs="+",
        default=None,
        help="Columns to include for transaction details.",
    )
    return parser.parse_args()


def run_elster_calculation(processed_path, euer_output_path, transaction_cols=None):
    """Run the EÜR calculation and save the results."""
    # load
    df = load_processed_transactions()
    elster_schema = load_elster_schema()

    results = {}
    results["EÜR"] = calculate_eur(
        df=df,
        euer_schema=elster_schema["EÜR"],
        transaction_cols=transaction_cols,
    )
    results["Bilanz"] = calculate_gewinn(results["EÜR"])
    results["Transfers"] = calculate_transfers(df, transaction_cols=transaction_cols)
    results["Taxes"] = aggregate_tax_obligations(df, pay_for_incorrect_rc=False)

    results["ESt"] = calculate_est(
        df=df,
        est_schema=elster_schema["ESt"],
        gewinn=results["Bilanz"]["Gewinn"],
        transaction_cols=transaction_cols,
    )

    for title, result_dict in results.items():
        log_results(result_dict, title)


if __name__ == "__main__":
    args = parse_args()
    run_elster_calculation(
        args.processed_path,
        args.euer_output_path,
        transaction_cols=args.transaction_cols,
    )
