"""Calculations for the Einkommensteuererklärung."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable

import pandas as pd

from src.elster.utils import sum_of_category_abs, transactions_of_category
from src.filter import count_this_year

KV_BASISSATZ = 0.14
KV_BKK_ZUSATZ = 0.0299
KV_SATZ = KV_BASISSATZ + KV_BKK_ZUSATZ
PV_SATZ = 0.034


def calculate_est(
    df: pd.DataFrame,
    est_schema: Dict[str, Any],
    gewinn: float,
    transaction_cols: Iterable[str] | None = None,
) -> Dict[str, Any]:

    ESt = deepcopy(est_schema)

    df_current_year = df[count_this_year(df)]
    kv_plus_pv = sum_of_category_abs(df_current_year, "Krankenversicherungen")
    if transaction_cols:
        kv_pv_tx = transactions_of_category(
            df_current_year,
            "Krankenversicherungen",
            columns=transaction_cols,
        )
    ESt["Gewinn als Einzelunternehmer"] = gewinn

    kv = kv_plus_pv * KV_SATZ / (KV_SATZ + PV_SATZ)
    pv = kv_plus_pv * PV_SATZ / (KV_SATZ + PV_SATZ)

    if transaction_cols:
        ESt["Beiträge anderer Personen"]["Krankenversicherungen"] = {
            "sum": kv,
            "transactions": kv_pv_tx,
        }
        ESt["Beiträge anderer Personen"]["Pflegeversicherungen"] = {
            "sum": pv,
            "transactions": kv_pv_tx,
        }
    else:
        ESt["Beiträge anderer Personen"]["Krankenversicherungen"] = kv
        ESt["Beiträge anderer Personen"]["Pflegeversicherungen"] = pv
    return ESt
