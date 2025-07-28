from src.filter import (
    is_afa,
    is_eu,
    is_expense,
    is_brutto,
    is_germany,
    is_netto,
    is_usa,
)

KLEINUNTERNEHMERREGELUNG = True


def is_brutto_expense(df):
    return is_brutto(df) & is_expense(df)


def is_netto_expense(df):
    return is_netto(df) & is_expense(df)


def is_taxfree(df):
    return ~is_brutto_expense(df) & ~is_netto_expense(df)


def is_taxfree_expense(df):
    return is_taxfree(df) & is_expense(df)


def is_eu_netto_expense(df):
    return is_eu(df) & is_netto_expense(df)


def is_eu_brutto_expense(df):
    return is_eu(df) & is_brutto_expense(df)


def is_usa_brutto_expense(df):
    return is_usa(df) & is_brutto_expense(df)


def is_usa_netto_expense(df):
    return is_usa(df) & is_netto_expense(df)


def is_non_ger_netto_expense(df):
    return is_netto_expense(df) & ~is_germany(df)


def is_non_ger_brutto_expense(df):
    return is_brutto_expense(df) & ~is_germany(df)


def is_ger_brutto_expense(df):
    return is_brutto_expense(df) & is_germany(df)


def is_ger_netto_expense(df):
    return is_netto_expense(df) & is_germany(df)


def is_vorsteuer_transaction(df):
    vorsteuer_filter = is_ger_brutto_expense(df) & (
        ~is_afa(df) if KLEINUNTERNEHMERREGELUNG else True
    )

    return vorsteuer_filter
