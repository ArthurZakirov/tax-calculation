"""Calculations for the Einkommensteuererklärung."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

import pandas as pd

from src.elster.utils import sum_of_category_abs
from src.filter import count_this_year

KV_BASISSATZ = 0.14
KV_BKK_ZUSATZ = 0.0299
KV_SATZ = KV_BASISSATZ + KV_BKK_ZUSATZ
PV_SATZ = 0.034


def calculate_est(
    df: pd.DataFrame, est_schema: Dict[str, Any], gewinn: float
) -> Dict[str, Any]:

    ESt = deepcopy(est_schema)

    kv_plus_pv = sum_of_category_abs(df[count_this_year(df)], "Krankenversicherungen")
    ESt["Gewinn als Einzelunternehmer"] = gewinn

    kv = kv_plus_pv * KV_SATZ / (KV_SATZ + PV_SATZ)
    pv = kv_plus_pv * PV_SATZ / (KV_SATZ + PV_SATZ)

    ESt["Beiträge anderer Personen"]["Krankenversicherungen"] = kv
    ESt["Beiträge anderer Personen"]["Pflegeversicherungen"] = pv
    return ESt
