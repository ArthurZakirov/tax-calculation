# tax-calculation
📊 Calculation of ELSTER relevant inputs

## Including transaction details

The command ``run_elster.py`` can optionally embed the original transaction
rows in the generated JSON output.  Use the ``--transaction_cols`` argument to
specify which columns should be included for each transaction.

Example:

```bash
python run_elster.py --transaction_cols "Name Zahlungsbeteiligter" "Amount (EUR)"
```

When this option is used, each leaf entry in the result contains a dictionary
with a ``"sum"`` field and a list of ``"transactions"`` with the selected
columns.

