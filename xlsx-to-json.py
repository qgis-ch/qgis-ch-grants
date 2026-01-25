import pandas as pd
import json

# Excel laden
df = pd.read_excel('projekte.xlsx')  # oder .csv

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
    "titel": "QGIS-CH Project Funding Votation 2026",
    "budget_limit": 65000,
    "waehrung": "CHF",
    "admin_password": "admin-2026",
    "projekte": projekte
}

with open('projekte.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
