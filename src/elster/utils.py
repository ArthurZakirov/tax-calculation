import pandas as pd
from typing import Dict
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
    return round_abs_sum_item(
        df[df[filter_column].str.contains(category)][value_column]
    )


def sum_of_dict_children(d: Dict[str, Dict[str, float]]) -> float:
    return sum(sum(d[kategorie].values()) for kategorie in d.keys())
