import pandas as pd


def to_float(col: pd.Series) -> pd.Series:
    col = col.str.replace(r"\.", "", regex=True)  
    col = col.str.replace(",", ".", regex=False)  
    return col.astype(float)
