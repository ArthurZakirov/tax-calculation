import pandas as pd
from functools import partial
from src.etl.utils import to_float
from src.filter import count_as_business, is_kv
from src.filter import is_business_related

COLS = {
    "N26": {
        "Native": ["Name", "Amount (EUR)"],
        "Custom": [
            "ELSTER Kategorie",
            "Brutto / Netto",
            "Country",
            "Reverse Charge Remark",
        ],
    },
    "PSD": {
        "Native": ["Name Zahlungsbeteiligter", "Betrag"],
        "Custom": [
            "Count as Business",
            "Business Related",
            "ELSTER Kategorie",
            "Letztes Jahr verwendet",
            "Country",
        ],
    },
    "STRIPE": {
        "Native": ["Name", "Amount", "Fee", "Net"],
    },
}

SELECTED_COLS = {
    "N26": COLS["N26"]["Native"] + COLS["N26"]["Custom"],
    "PSD": COLS["PSD"]["Native"] + COLS["PSD"]["Custom"],
    "STRIPE": COLS["STRIPE"]["Native"],
}
COMMA_COLS = {"N26": [], "PSD": ["Betrag"], "STRIPE": ["Amount", "Fee", "Net"]}
RENAME_COLS = {
    "N26": {"Name": "Name Zahlungsbeteiligter"},
    "PSD": {"Betrag": "Amount (EUR)"},
    "STRIPE": {"Amount": "Amount (EUR)", "Fee": "Fee (EUR)", "Net": "Net (EUR)"},
}

FILTER_ROWS = {
    "N26": lambda df: df,
    "PSD": lambda df: df[(is_business_related(df) & count_as_business(df)) | is_kv(df)],
    "STRIPE": lambda df: df,
}

FINAL_COLS = [
    "Name Zahlungsbeteiligter",
    "Amount (EUR)",
    "ELSTER Kategorie",
    "Brutto / Netto",
    "Country",
    "Reverse Charge Remark",
    "Letztes Jahr verwendet",
    "Business Related",
    "Count as Business",
]
FILLNA = {
    "N26": {},
    "PSD": {
        "Brutto / Netto": "Brutto",
    },
    "STRIPE": {},
}


def process_stripe_extra(df: pd.DataFrame) -> pd.DataFrame:
    fees_as_seperate_transactions = df[df["Type"] == "charge"].copy()
    fees_as_seperate_transactions["Amount (EUR)"] = -fees_as_seperate_transactions[
        "Fee (EUR)"
    ]
    fees_as_seperate_transactions["ELSTER Kategorie"] = "Gebühren"
    fees_as_seperate_transactions["Country"] = "EU"
    fees_as_seperate_transactions["Name Zahlungsbeteiligter"] = "Stripe Fee"
    df = pd.concat([df, fees_as_seperate_transactions], ignore_index=True)
    return df


def process_data(df: pd.DataFrame, bank: str) -> pd.DataFrame:
    df = df.copy()
    for format_col in COMMA_COLS[bank]:
        df[format_col] = to_float(df[format_col])
    df = df[SELECTED_COLS[bank]]
    df = df.rename(columns=RENAME_COLS[bank])
    df = FILTER_ROWS[bank](df)

    if bank == "STRIPE":
        df = process_stripe_extra(df)

    drop_cols = set(df.columns) - set(FINAL_COLS)
    df = df.drop(columns=drop_cols, errors="ignore")

    for col, value in FILLNA[bank].items():
        df[col] = value
    return df


process_fn: dict[str, callable] = {
    bank: partial(process_data, bank=bank) for bank in COLS.keys()
}
