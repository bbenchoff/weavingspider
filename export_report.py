#!/usr/bin/env python3
"""
Export the Bohemian Grove database to a readable CSV and HTML report.
"""

import sqlite3
import csv
import json

DB = "bohemian_grove.db"


def export_csv():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT name, camp, employer, employer_title, employer_source, notes
        FROM members ORDER BY camp, name
    """)
    rows = cur.fetchall()
    conn.close()

    with open("bohemian_grove.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Camp", "Employer", "Title", "Source", "Notes"])
        writer.writerows(rows)
    print(f"Exported {len(rows)} rows to bohemian_grove.csv")


def export_html():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Summary stats
    cur.execute("SELECT COUNT(*) FROM members")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM members WHERE employer IS NOT NULL")
    with_employer = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT camp) FROM members")
    camps = cur.fetchone()[0]

    # Camp breakdown
    cur.execute("""
        SELECT camp, COUNT(*) as total,
               SUM(CASE WHEN employer IS NOT NULL THEN 1 ELSE 0 END) as researched
        FROM members GROUP BY camp ORDER BY total DESC
    """)
    camp_rows = cur.fetchall()

    # Members with employer data
    cur.execute("""
        SELECT name, camp, employer, employer_title, employer_source
        FROM members WHERE employer IS NOT NULL
        ORDER BY camp, name
    """)
    employer_rows = cur.fetchall()

    conn.close()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bohemian Grove Member Database</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
  h1 {{ color: #5a2d0c; }}
  h2 {{ color: #7a4d1c; border-bottom: 2px solid #c8a96e; padding-bottom: 6px; }}
  .stats {{ background: #fdf6ec; border: 1px solid #c8a96e; padding: 12px; border-radius: 6px; margin: 10px 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }}
  th {{ background: #7a4d1c; color: white; padding: 8px; text-align: left; }}
  tr:nth-child(even) {{ background: #fdf6ec; }}
  td {{ padding: 6px 8px; border-bottom: 1px solid #e0d0b8; }}
  .camp-name {{ font-weight: bold; color: #5a2d0c; }}
  a {{ color: #5a2d0c; }}
  .filter {{ margin: 10px 0; }}
  input {{ padding: 6px; width: 300px; border: 1px solid #c8a96e; border-radius: 4px; }}
</style>
<script>
function filterTable(inputId, tableId) {{
  const filter = document.getElementById(inputId).value.toLowerCase();
  const rows = document.getElementById(tableId).getElementsByTagName('tr');
  for (let i = 1; i < rows.length; i++) {{
    const text = rows[i].textContent.toLowerCase();
    rows[i].style.display = text.includes(filter) ? '' : 'none';
  }}
}}
</script>
</head>
<body>
<h1>Bohemian Grove Member Database</h1>
<div class="stats">
  <strong>Total Members:</strong> {total} |
  <strong>Camps:</strong> {camps} |
  <strong>Members with Employer Data:</strong> {with_employer} ({100*with_employer//total if total else 0}%)
</div>

<h2>Members with Employer Data</h2>
<div class="filter">
  <input id="empSearch" onkeyup="filterTable('empSearch','empTable')" placeholder="Filter by name, camp, or employer...">
</div>
<table id="empTable">
  <tr><th>Name</th><th>Camp</th><th>Employer</th><th>Title</th><th>Source</th></tr>
"""
    for row in employer_rows:
        name, camp, employer, title, source = row
        src_link = f'<a href="{source}" target="_blank">link</a>' if source and source.startswith("http") else (source or "")
        html += f"  <tr><td>{name}</td><td class='camp-name'>{camp}</td><td>{employer or ''}</td><td>{title or ''}</td><td>{src_link}</td></tr>\n"

    html += """</table>

<h2>All Camps & Member Counts</h2>
<table>
  <tr><th>Camp</th><th>Members</th><th>Researched</th></tr>
"""
    for camp, total_c, researched in camp_rows:
        html += f"  <tr><td class='camp-name'>{camp}</td><td>{total_c}</td><td>{researched}</td></tr>\n"

    html += "</table>\n</body>\n</html>\n"

    with open("bohemian_grove_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Exported HTML report to bohemian_grove_report.html")


if __name__ == "__main__":
    export_csv()
    export_html()
