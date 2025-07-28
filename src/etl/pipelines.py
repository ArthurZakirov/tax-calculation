import pandas as pd
from functools import partial
from src.etl.utils import to_float
from src.filter import count_as_business
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
    "PSD": lambda df: df[is_business_related(df) & count_as_business(df)],
    "STRIPE": lambda df: df,
}

FINAL_COLS = [
    "Name Zahlungsbeteiligter",
    "Amount (EUR)",
    "ELSTER Kategorie",
    "Brutto / Netto",
    "Country",
    "Reverse Charge Remark",
]
FILLNA = {"N26": {}, "PSD": {"Brutto / Netto": "Brutto", }, "STRIPE": {}}


def process_data(df: pd.DataFrame, bank: str) -> pd.DataFrame:
    df = df.copy()
    for format_col in COMMA_COLS[bank]:
        df[format_col] = to_float(df[format_col])
    df = df[SELECTED_COLS[bank]]
    df = df.rename(columns=RENAME_COLS[bank])
    df = FILTER_ROWS[bank](df)
    for bank in COLS.keys():
        drop_cols = set(df.columns) - set(FINAL_COLS)
        df = df.drop(columns=drop_cols, errors='ignore')
    for col, value in FILLNA[bank].items():
        df[col] = value
    return df


process_fn: dict[str, callable] = {
    bank: partial(process_data, bank=bank) for bank in COLS.keys()
}
