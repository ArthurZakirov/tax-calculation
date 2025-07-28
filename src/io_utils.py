import json
from typing import Any, Dict, Tuple
import pandas as pd


import os


def load_processed_transactions():
    return pd.read_csv(os.getenv("PROCESSED_TRANSACTIONS"))


def print_json(data):
    """Prints JSON data in a formatted way."""
    print(json.dumps(data, indent=4, ensure_ascii=False))


def log_results(results_dict, title):
    """Logs the results in a formatted way."""
    print(f"\n{title}:")
    print_json(results_dict)
    print("\n")


def load_elster_schema(schema_path="elster_schema.json"):
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_results_to_json(euer_output_path, results):
    with open(euer_output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)


def unflatten_dict(flat: Dict[Tuple[Any, ...], float]) -> Dict[str, Any]:
    """
    Reconstruct a nested dictionary from a flat dict with tuple keys.

    Args:
        flat: A dict mapping tuple of keys to float values.

    Returns:
        A nested dictionary where each level is a dict, leaves are floats.

    Example:
        flat = {('a', 'x', 'i'): 1.0, ('a', 'y', 'k'): 3.0, ('b', 'z', 'l'): 4.0}
        nested = unflatten_dict(flat)
        # nested == {
        #   'a': {'x': {'i': 1.0}, 'y': {'k': 3.0}},
        #   'b': {'z': {'l': 4.0}}
        # }
    """
    nested: Dict[str, Any] = {}
    for key_tuple, value in flat.items():
        current = nested
        for part in key_tuple[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]  # type: ignore
        current[key_tuple[-1]] = value  # type: ignore
    return nested
