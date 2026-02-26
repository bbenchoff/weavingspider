#!/usr/bin/env python3
"""
Build the static site into docs/.
Exports bohemian_grove.db → docs/data.json
Run this whenever the database changes, then commit docs/.
"""
import sqlite3
import json
import os

DB = 'bohemian_grove.db'
OUT_DIR = 'docs'

os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
rows = conn.execute('''
    SELECT name, camp,
           employer,
           employer_title  AS title,
           employer_source AS source,
           political_donations AS donations,
           opensecrets_url     AS opensecrets,
           ngos, notes
    FROM members ORDER BY camp, name
''').fetchall()
conn.close()

members = [
    {k: (row[k] or '') for k in row.keys()}
    for row in rows
]

out_path = os.path.join(OUT_DIR, 'data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(members, f, ensure_ascii=False)

print(f'Wrote {len(members)} members to {out_path}')
