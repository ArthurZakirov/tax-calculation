import pandas as pd
from collections import defaultdict
from dataclasses import dataclass
from src.advanced_filter import (
    is_brutto_expense,
    is_netto_expense,
    is_vorsteuer_transaction,
)
from src.advanced_filter import is_eu_netto_expense
from src.advanced_filter import is_eu_brutto_expense
from src.advanced_filter import is_usa_brutto_expense
from src.advanced_filter import is_usa_netto_expense
from src.elster.utils import round_abs_sum_item

NETTO_TO_UST = 0.19
BRUTTO_TO_NETTO = round(1 / (1 + NETTO_TO_UST), 2)
NETTO_TO_BRUTTO = round(1 / BRUTTO_TO_NETTO, 2)
BRUTTO_TO_UST = round(NETTO_TO_UST * BRUTTO_TO_NETTO, 2)

NETTO_COL = "Netto (EUR)"
BRUTO_COL = "Brutto (EUR)"
STEUER_COL = "Steuer (EUR)"
TAX_ALIAS_COL = "Tax Category"


@dataclass
class TaxAlias:
    VORSTEUER: str = "Gezahlte Vorsteuerbeträge"
    EU_REVERSE_CHARGE: str = "EU Reverse Charge"
    USA_REVERSE_CHARGE: str = "USA Reverse Charge"
    INCORRECT_EU_REVERSE_CHARGE: str = "Incorrect EU Reverse Charge"
    INCORRECT_USA_REVERSE_CHARGE: str = "Incorrect USA Reverse Charge"


def determine_tax_obligations(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df[BRUTO_COL] = 0.0
    df[NETTO_COL] = 0.0
    df[STEUER_COL] = 0.0
    df[TAX_ALIAS_COL] = ""

    conversion = [
        (
            is_netto_expense,
            {NETTO_COL: 1, STEUER_COL: NETTO_TO_UST, BRUTO_COL: NETTO_TO_BRUTTO},
        ),
        (
            is_brutto_expense,
            {NETTO_COL: BRUTTO_TO_NETTO, STEUER_COL: BRUTTO_TO_UST, BRUTO_COL: 1},
        ),
    ]

    for filter_func, conversion_dict in conversion:
        apply_conversion(df=df, mask=filter_func(df), conversion_dict=conversion_dict)

    tax_categories: dict[str, callable] = {
        TaxAlias.VORSTEUER: is_vorsteuer_transaction,
        TaxAlias.EU_REVERSE_CHARGE: is_eu_netto_expense,
        TaxAlias.USA_REVERSE_CHARGE: is_usa_netto_expense,
        TaxAlias.INCORRECT_EU_REVERSE_CHARGE: is_eu_brutto_expense,
        TaxAlias.INCORRECT_USA_REVERSE_CHARGE: is_usa_brutto_expense,
    }

    for category, condition in tax_categories.items():
        df.loc[condition(df), TAX_ALIAS_COL] = category
    return df


def apply_conversion(
    df: pd.DataFrame, mask: pd.Series, conversion_dict: dict
) -> pd.DataFrame:
    for col, factor in conversion_dict.items():
        df.loc[mask, col] = round(df.loc[mask, "Amount (EUR)"] * factor, 2)
    return df


def aggregate_tax_obligations(df: pd.DataFrame):

    addresses: list[tuple[str, tuple[str, ...]]] = [
        (
            TaxAlias.VORSTEUER,
            (
                "EÜR",
                "4 - 2. Betriebsausgaben",
                "Sonstige unbeschränkt abziehbare Betriebsausgaben",
                "Gezahlte Vorsteuerbeträge",
            ),
        ),
        (
            TaxAlias.EU_REVERSE_CHARGE,
            (
                "USt",
                "9 - H. Leistungsempfänger als Steuerschuldner (§ 13b UStG)",
                "im übrigen Gemeinschaftsgebiet ansässigen Unternehmers (§ 13b Absatz 1 UStG)",
            ),
        ),
        (
            TaxAlias.USA_REVERSE_CHARGE,
            (
                "USt",
                "9 - H. Leistungsempfänger als Steuerschuldner (§ 13b UStG)",
                "Andere Leistungen (§ 13b Absatz 2 Nummer 1, 2, 4 bis 12 UStG)",
            ),
        ),
        (
            TaxAlias.INCORRECT_EU_REVERSE_CHARGE,
            (
                "USt",
                "9 - H. Leistungsempfänger als Steuerschuldner (§ 13b UStG)",
                "im übrigen Gemeinschaftsgebiet ansässigen Unternehmers (§ 13b Absatz 1 UStG)",
            ),
        ),
        (
            TaxAlias.INCORRECT_USA_REVERSE_CHARGE,
            (
                "USt",
                "9 - H. Leistungsempfänger als Steuerschuldner (§ 13b UStG)",
                "Andere Leistungen (§ 13b Absatz 2 Nummer 1, 2, 4 bis 12 UStG)",
            ),
        ),
    ]

    mapping = {
        "Bemessungsgrundlage ohne Umsatzsteuer": NETTO_COL,
        "Steuer": STEUER_COL,
    }

    results = defaultdict(float)
    for tax_alias, elster_category in addresses:
        if elster_category[0] == "USt":
            mask = df[TAX_ALIAS_COL] == tax_alias
            for elster_val, col in mapping.items():
                elster_metric_sum = round_abs_sum_item(df.loc[mask, col])
                key = (*elster_category, elster_val)
                results[key] += elster_metric_sum
    
    return dict(results)