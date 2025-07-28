"""Calculation helpers for the Einnahmen-Überschuss-Rechnung."""

from copy import deepcopy
from typing import Any, Dict, Iterable
import pandas as pd

from src.elster.utils import (
    sum_of_category_abs,
    sum_of_dict_children,
    transactions_of_category,
)
from src.tax.tax import BRUTTO_COL, AMOUNT_COL


def calculate_eur(
    df: pd.DataFrame,
    euer_schema: Dict[str, Any],
    transaction_cols: Iterable[str] | None = None,
) -> Dict[str, Any]:

    results = deepcopy(euer_schema)
    for in_out_dict in results.values():
        for kategorie in in_out_dict.keys():
            for subcategory in in_out_dict[kategorie].keys():
                if subcategory != "Gezahlte Vorsteuerbeträge":
                    val = sum_of_category_abs(
                        df=df,
                        category=subcategory,
                        value_column=AMOUNT_COL,
                    )
                    if transaction_cols:
                        tx = transactions_of_category(
                            df=df,
                            category=subcategory,
                            columns=transaction_cols,
                        )
                        in_out_dict[kategorie][subcategory] = {
                            "sum": val,
                            "transactions": tx,
                        }
                    else:
                        in_out_dict[kategorie][subcategory] = val
    return results


def calculate_gewinn(results: Dict[str, Any]) -> Dict[str, float]:
    bilanz = {key: round(sum_of_dict_children(results[key]), 2) for key in results.keys()}
    bilanz["Gewinn"] = (
        round(bilanz["3 - 1. Betriebseinnahmen"] + bilanz["4 - 2. Betriebsausgaben"], 2)
    )
    return bilanz


def calculate_transfers(
    df: pd.DataFrame, transaction_cols: Iterable[str] | None = None
) -> Dict[str, Any]:
    """Aggregate private transfers and optionally include transaction details."""

    result: Dict[str, Any] = {}
    for key in ["Privateentnahme", "Privateinlage"]:
        val = sum_of_category_abs(df, category=key)
        if transaction_cols:
            tx = transactions_of_category(df, category=key, columns=transaction_cols)
            result[key] = {"sum": val, "transactions": tx}
        else:
            result[key] = val
    return result
