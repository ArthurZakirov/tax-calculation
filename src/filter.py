import pandas as pd

def has_rc_remark(df: pd.DataFrame) -> pd.Series:
    """Check if the transaction has a reverse charge remark."""
    return df["Reverse Charge Remark"] == "Yes"

def is_expense(df: pd.DataFrame) -> pd.Series:
    """Determine if the transaction is an expense."""
    return df["Amount (EUR)"] < 0

def is_brutto(df: pd.DataFrame) -> pd.Series:
    """Check if the transaction is in brutto format."""
    return df["Brutto / Netto"] == "Brutto"

def is_netto(df: pd.DataFrame) -> pd.Series:
    """Check if the transaction is in netto format."""
    return df["Brutto / Netto"] == "Netto"

def is_germany(df: pd.DataFrame) -> pd.Series:
    """Check if the transaction is from Germany."""
    return df["Country"] == "GER"

def is_eu(df: pd.DataFrame) -> pd.Series:
    """Check if the transaction is from the EU."""
    return df["Country"].isin(["EU"])

def is_usa(df: pd.DataFrame) -> pd.Series:
    """Check if the transaction is from the USA."""
    return df["Country"].isin(["USA"])

def is_afa(df: pd.DataFrame) -> pd.Series:
    """Check if the transaction is an AfA (Absetzung für Abnutzung)."""
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