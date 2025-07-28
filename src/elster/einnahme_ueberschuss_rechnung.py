"""Calculation helpers for the Einnahmen-Überschuss-Rechnung."""

from copy import deepcopy
from typing import Any, Dict
import pandas as pd

from src.elster.utils import (
    sum_of_category_abs,
    sum_of_dict_children,
)
from src.tax.tax import BRUTTO_COL


def calculate_eur(df: pd.DataFrame, euer_schema: Dict[str, Any]):

    results = deepcopy(euer_schema)
    for in_out_dict in results.values():
        for kategorie in in_out_dict.keys():
            for subcategory in in_out_dict[kategorie].keys():
                if subcategory != "Gezahlte Vorsteuerbeträge":
                    val = sum_of_category_abs(
                        df=df,
                        category=subcategory,
                        value_column=BRUTTO_COL,
                    )
                    in_out_dict[kategorie][subcategory] = val
    return results


def calculate_gewinn(results: Dict[str, Any]) -> Dict[str, float]:
    bilanz = {key: sum_of_dict_children(results[key]) for key in results.keys()}
    bilanz["Gewinn"] = (
        bilanz["3 - 1. Betriebseinnahmen"] - bilanz["4 - 2. Betriebsausgaben"]
    )
    return bilanz


def calculate_transfers(df: pd.DataFrame) -> Dict[str, float]:
    return {
        key: sum_of_category_abs(df, category=key)
        for key in ["Privateentnahme", "Privateinlage"]
    }
