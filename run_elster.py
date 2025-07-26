from src.elster.utils import load_elster_schema, load_processed_transactions
from src.elster.einnahme_ueberschuss_rechnung import calculate_eur

df = load_processed_transactions()
elster_schema = load_elster_schema()
results = calculate_eur(df=df, schema=elster_schema)

print(results)