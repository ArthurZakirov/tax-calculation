import pandas as pd
from src.elster.utils import load_processed_transactions

UST_SATZ = 0.19
BRUTTO_TO_UST = UST_SATZ / (1 + UST_SATZ)

df = load_processed_transactions()


legit_rc = abs(
    df[(df["Country"].isin(["USA", "EU"])) & (df["Brutto / Netto"] == "Netto")][
        "Amount (EUR)"
    ].sum()
)
double_rc = abs(
    df[(df["Country"].isin(["USA", "EU"])) & (df["Brutto / Netto"] == "Brutto")][
        "Amount (EUR)"
    ].sum()
)
reverse_charge_soll = legit_rc + double_rc