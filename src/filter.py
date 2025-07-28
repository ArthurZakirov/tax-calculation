import pandas as pd

def has_rc_remark(df: pd.DataFrame) -> pd.Series:
    return df["Reverse Charge Remark"] == "Yes"


def is_expense(df: pd.DataFrame) -> pd.Series:
    return df["Amount (EUR)"] < 0


def is_brutto(df: pd.DataFrame) -> pd.Series:
    return df["Brutto / Netto"] == "Brutto"


def is_netto(df: pd.DataFrame) -> pd.Series:
    return df["Brutto / Netto"] == "Netto"


def is_germany(df: pd.DataFrame) -> pd.Series:
    return df["Country"] == "GER"


def is_eu(df: pd.DataFrame) -> pd.Series:
    return df["Country"].isin(["EU"])


def is_usa(df: pd.DataFrame) -> pd.Series:
    return df["Country"].isin(["USA"])


def is_afa(df: pd.DataFrame) -> pd.Series:
    return df["ELSTER Kategorie"].isin(
        [
            "Absetzung für Abnutzung (AfA)",
            "GWG",
            "Anlage AVEÜR",
            "geringwertige Wirtschaftsgüter",
            "Geringwertige Wirtschaftsgüter",
        ]
    )


def count_as_business(df: pd.DataFrame) -> pd.Series:
    return df["Count as Business"].str.lower() != "personal"


def is_business_related(df: pd.DataFrame) -> pd.Series:
    return df["Business Related"].str.lower() == "business"


def is_kv(df: pd.DataFrame) -> pd.Series:
    return df["ELSTER Kategorie"] == "Krankenversicherungen"


def count_this_year(df: pd.DataFrame) -> pd.Series:
    return df["Letztes Jahr verwendet"] == "Nein"


def is_tax_free_income(df: pd.DataFrame) -> pd.Series:
    return df["ELSTER Kategorie"].str.contains("Kleinunternehmer")
