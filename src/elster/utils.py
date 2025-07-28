import pandas as pd
from typing import Any, Dict, Iterable, List
from dotenv import load_dotenv

load_dotenv()


def round_abs_sum_item(series: pd.Series) -> float:
    return round(abs(series.sum().item()), 2)


def sum_of_category_abs(
    df: pd.DataFrame,
    category: str,
    filter_column: str = "ELSTER Kategorie",
    value_column: str = "Amount (EUR)",
) -> float:
    """Return the absolute sum of ``value_column`` for rows matching ``category``."""
    return round_abs_sum_item(
        df[df[filter_column].str.contains(category)][value_column]
    )


def transactions_of_category(
    df: pd.DataFrame,
    category: str,
    columns: Iterable[str],
    filter_column: str = "ELSTER Kategorie",
) -> List[Dict[str, Any]]:
    """Return a list of transaction dictionaries for ``category``.

    Parameters
    ----------
    df:
        DataFrame containing all transactions.
    category:
        ELSTER category to filter for.
    columns:
        Columns to include in the resulting dictionaries.
    filter_column:
        Column containing the ELSTER category labels.
    """
    filtered = df[df[filter_column].str.contains(category)]
    if columns:
        filtered = filtered[list(columns)]
    return filtered.to_dict(orient="records")


def sum_of_dict_children(d: Dict[str, Dict[str, Any]]) -> float:
    """Return the sum of children values of a nested dict.

    This helper is aware of dictionaries produced when transaction details are
    attached to the leaves. In that case each leaf is expected to be a
    ``{"sum": float, "transactions": [...]}`` mapping.
    """

    total = 0.0
    for kategorie in d.keys():
        for value in d[kategorie].values():
            if isinstance(value, dict) and "sum" in value:
                total += float(value.get("sum", 0))
            else:
                total += float(value)
    return total
