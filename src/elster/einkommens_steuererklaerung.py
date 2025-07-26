from src.elster.utils import (
    load_elster_schema,
    load_processed_transactions,
    sum_of_category_abs,
)
from dotenv import load_dotenv

load_dotenv()

KV_BASISSATZ = 0.14
KV_BKK_ZUSATZ = 0.0299
KV_SATZ = KV_BASISSATZ + KV_BKK_ZUSATZ
PV_SATZ = 0.034

ESt = load_elster_schema()
df = load_processed_transactions()

# TODO: nehme "gewinn" aus EÜR


kv_und_pv = sum_of_category_abs(
    df[df["Letztes Jahr verwendet"] == "Nein"], "Krankenversicherungen"
)
ESt["Gewinn als Einzelunternehmer"] = gewinn
ESt["Beiträge anderer Personen"]["Krankenversicherungen"] = (
    kv_und_pv * KV_SATZ / (KV_SATZ + PV_SATZ)
)
ESt["Beiträge anderer Personen"]["Pflegeversicherungen"] = (
    kv_und_pv * PV_SATZ / (KV_SATZ + PV_SATZ)
)
