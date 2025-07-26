from src.elster.utils import load_elster_schema, load_processed_transactions
from src.elster.einnahme_ueberschuss_rechnung import calculate_eur
import json

euer_output_path = "euer_output.json"

df = load_processed_transactions()
elster_schema = load_elster_schema()
results = calculate_eur(df=df, schema=elster_schema)

with open(euer_output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)