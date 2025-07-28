import pandas as pd
from typing import Any, Dict, Iterable, List
from dotenv import load_dotenv

load_dotenv()


def round_abs_sum_item(series: pd.Series) -> float:
    return round(series.sum().item(), 2)


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
    party_column: str = "Name Zahlungsbeteiligter",
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
    party_column:
        Column name to group by for aggregation (default: "Name Zahlungsbeteiligter").
    """
    filtered = df[df[filter_column].str.contains(category)]
    if columns:
        filtered = filtered[list(columns)]

    # Aggregate rows with same party by summing float columns
    if party_column in filtered.columns:
        # Identify float columns for aggregation
        float_cols = filtered.select_dtypes(
            include=["float64", "float32", "int64", "int32"]
        ).columns.tolist()
        non_float_cols = [
            col
            for col in filtered.columns
            if col not in float_cols and col != party_column
        ]

        # Group by party and aggregate
        agg_dict = {}
        for col in float_cols:
            agg_dict[col] = "sum"
        for col in non_float_cols:
            agg_dict[col] = "first"  # Take first non-float value for each group

        filtered = filtered.groupby(party_column).agg(agg_dict).reset_index()

        # Round float columns to 2 decimal places after aggregation
        for col in float_cols:
            if col in filtered.columns:
                filtered[col] = filtered[col].round(2)

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
