import pandas as pd
from src.etl.utils import to_float


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
}


def process_stripe(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    df_out["Amount"] = to_float(df_out["Amount"])
    df_out["Fee"] = to_float(df_out["Fee"])
    df_out["Net"] = to_float(df_out["Net"])
    return df_out


def process_psd(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    df_out = df_out[COLS["PSD"]["Native"] + COLS["PSD"]["Custom"]]
    df_out["Betrag"] = to_float(df_out["Betrag"])
    df_out["Brutto / Netto"] = "Brutto"
    df_out = df_out.rename(columns={"Betrag": "Amount (EUR)"})
    df_out = df_out[
        (df_out["Business Related"] == "business")
        & (df_out["Count as Business"] != "Personal")
    ]
    df_out = df_out.drop(columns=["Count as Business", "Business Related"])
    return df_out


def process_n26(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()
    df_out = df_out[COLS["N26"]["Native"] + COLS["N26"]["Custom"]]
    df_out = df_out.rename(columns={"Name": "Name Zahlungsbeteiligter"})
    return df_out


process_fn: dict[str, callable] = {
    "STRIPE": process_stripe,
    "PSD": process_psd,
    "N26": process_n26,
}
