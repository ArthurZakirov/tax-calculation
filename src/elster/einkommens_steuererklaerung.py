"""Calculations for the Einkommensteuererklärung."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

import pandas as pd

from src.elster.utils import sum_of_category_abs

KV_BASISSATZ = 0.14
KV_BKK_ZUSATZ = 0.0299
KV_SATZ = KV_BASISSATZ + KV_BKK_ZUSATZ
PV_SATZ = 0.034


def calculate_est(
    df: pd.DataFrame, schema: Dict[str, Any], gewinn: float
) -> Dict[str, Any]:
    """Populate the ESt section of the schema.

    Parameters
    ----------
    df:
        Processed transactions.
    schema:
        Base ELSTER schema.
    gewinn:
        Profit computed from the EÜR.

    Returns
    -------
    Dict[str, Any]
        Updated copy of the schema containing the calculated ESt values.
    """

    results = deepcopy(schema)

    kv_und_pv = sum_of_category_abs(
        df[df["Letztes Jahr verwendet"] == "Nein"], "Krankenversicherungen"
    )
    results["ESt"]["Gewinn als Einzelunternehmer"] = gewinn
    results["ESt"]["Beiträge anderer Personen"]["Krankenversicherungen"] = (
        kv_und_pv * KV_SATZ / (KV_SATZ + PV_SATZ)
    )
    results["ESt"]["Beiträge anderer Personen"]["Pflegeversicherungen"] = (
        kv_und_pv * PV_SATZ / (KV_SATZ + PV_SATZ)
    )

    return results
