import os
import pandas as pd
import json
import sys

# Excel laden
df = pd.read_excel('data/projekte.xlsx')  # oder .csv

# In JSON-Struktur umwandeln
projekte = []
for _, row in df.iterrows():
    projekte.append({
        "id": f"p{row['id']}",
        "name": row['name'],
        "kosten": int(row['kosten']),
        "beschreibung": row['beschreibung']
    })

output = {
    "titel": f"QGIS-CH Sponsoring Projects {os.environ['GRANTS_YEAR']} Voting",
    "budget_limit": int(os.environ['GRANTS_LIMIT']),
    "waehrung": "CHF",
    "admin_password": os.environ['ADMIN_PASSWORD'],
    "projekte": projekte
}

json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
