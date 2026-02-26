#!/usr/bin/env python3
"""
Load employer research JSON results and update the SQLite database.
Usage: python3 update_employers.py results1.json results2.json ...
"""

import json
import sqlite3
import sys
import re


def normalize_name(name):
    """Lowercase and strip for fuzzy matching."""
    return re.sub(r'\s+', ' ', name.lower().strip())


def update_db(db_path, results):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Build a lookup: normalized_name -> [row ids]
    cur.execute("SELECT id, name FROM members")
    rows = cur.fetchall()
    name_map = {}
    for row_id, name in rows:
        key = normalize_name(name)
        name_map.setdefault(key, []).append(row_id)

    updated = 0
    skipped = 0

    for entry in results:
        raw_name = entry.get("name", "")
        employer = entry.get("employer") or None
        title = entry.get("title") or None
        source = entry.get("source") or entry.get("employer_source") or None
        notes = entry.get("notes") or None
        ngos = entry.get("ngos") or None
        political_donations = entry.get("political_donations") or None
        opensecrets_url = entry.get("opensecrets_url") or None

        # Skip entries with no useful data at all
        if not any([employer, notes, ngos, political_donations, opensecrets_url]):
            continue

        key = normalize_name(raw_name)
        ids = name_map.get(key)

        if not ids:
            # Try partial match
            found = []
            for db_key, db_ids in name_map.items():
                if key in db_key or db_key in key:
                    found.extend(db_ids)
            if found:
                ids = found[:1]

        if ids:
            for row_id in ids:
                cur.execute("""
                    UPDATE members
                    SET employer = COALESCE(employer, ?),
                        employer_title = COALESCE(employer_title, ?),
                        employer_source = COALESCE(employer_source, ?),
                        notes = COALESCE(notes, ?),
                        ngos = COALESCE(ngos, ?),
                        political_donations = COALESCE(political_donations, ?),
                        opensecrets_url = COALESCE(opensecrets_url, ?)
                    WHERE id = ?
                """, (employer, title, source, notes, ngos, political_donations, opensecrets_url, row_id))
                if cur.rowcount:
                    updated += 1
        else:
            print(f"  NOT FOUND: {raw_name}")
            skipped += 1

    conn.commit()
    conn.close()
    print(f"Updated: {updated}, Skipped (not found): {skipped}")


def main():
    db_path = "bohemian_grove.db"
    all_results = []

    for path in sys.argv[1:]:
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            # Extract JSON array from content (agents may include extra text)
            m = re.search(r'\[.*\]', content, re.DOTALL)
            if m:
                data = json.loads(m.group(0))
                all_results.extend(data)
                print(f"Loaded {len(data)} entries from {path}")
            else:
                print(f"No JSON array found in {path}")
        except Exception as e:
            print(f"Error reading {path}: {e}")

    if all_results:
        update_db(db_path, all_results)
    else:
        print("No results to process.")


if __name__ == "__main__":
    main()
