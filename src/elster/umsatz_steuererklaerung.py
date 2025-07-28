"""Helpers to calculate the Umsatzsteuererklärung values."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional

import pandas as pd
from filter import is_expense, is_brutto, is_eu, is_usa, is_netto

UST_SATZ = 0.19
BRUTTO_TO_NETTO = round(1 / (1 + UST_SATZ), 2)
BRUTTO_TO_UST = round(UST_SATZ * BRUTTO_TO_NETTO, 2)

def amount_sum(df: pd.DataFrame) -> float:
    return round(abs(df["Amount (EUR)"].sum().item()), 2)

def calculate_ust(
    df: pd.DataFrame, schema: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Calculate VAT related values.

    Parameters
    ----------
    df:
        DataFrame containing the processed transactions.
    schema:
        Optional ELSTER schema. When provided, the returned dictionary contains a
        copy of the schema with the calculated values filled in.

    Returns
    -------
    Dict[str, Any]
        Dictionary with the calculated VAT values. If ``schema`` was provided it
        will be available under the key ``"schema"`` in the returned
        dictionary.
    """
    legit_rc = amount_sum(df[(is_usa(df) | is_eu(df)) & is_netto(df) & is_expense(df)])
    double_rc = amount_sum(df[(is_usa(df) | is_eu(df)) & is_brutto(df) & is_expense(df)])
    reverse_charge_soll = legit_rc + double_rc

    result = {
        "legit_rc": legit_rc,
        "double_rc": double_rc,
        "reverse_charge_soll": reverse_charge_soll,
    }

    if schema is not None:
        schema_copy = deepcopy(schema)
        ust = schema_copy.setdefault("USt", {})
        ust["9 - H. Leistungsempfänger als Steuerschuldner (§ 13b UStG)"] = (
            reverse_charge_soll
        )
        result["schema"] = schema_copy

    return result
