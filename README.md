# weavingspider

Research database of the 2,202 members of the Bohemian Grove, an all-male private club that holds an annual encampment at a 2,700-acre redwood camp in Monte Rio, California. Membership is drawn largely from senior figures in business, finance, government, and the military.

The source list is a leaked membership roster (Daniel Bogusław's transcription of a physical list). This project enriches it with publicly available professional and biographical information sourced from SEC EDGAR, OpenSecrets, corporate websites, Wikipedia, and news archives.

## Coverage

As of the last research run:

| Field | Count | % |
|---|---|---|
| Total members | 2,202 | — |
| Employer identified | 1,746 | 79.3% |
| Notes | 1,784 | 81.0% |
| NGOs / boards | 609 | 27.7% |
| Political donations | 148 | 6.7% |
| **Covered (any field)** | **1,875** | **85.1%** |
| Still empty | 327 | 14.9% |

The 327 empty members are individuals with no discoverable public footprint, or entries that appear to be data artifacts from the original source list (variant camp names, aliases).

## Database

**`bohemian_grove.db`** — SQLite database, single `members` table.

| Column | Description |
|---|---|
| `id` | Integer primary key |
| `name` | `LastName, FirstName` format |
| `camp` | Grove camp name |
| `employer` | Primary employer or organization |
| `employer_title` | Job title |
| `employer_source` | URL source for employer data |
| `notes` | Biographical notes |
| `ngos` | Board memberships and NGO roles (semicolon-separated) |
| `political_donations` | FEC/OpenSecrets donation summary |
| `opensecrets_url` | Link to OpenSecrets donor profile |

Quick queries:

```bash
# Count by camp
sqlite3 bohemian_grove.db "SELECT camp, COUNT(*) FROM members GROUP BY camp ORDER BY COUNT(*) DESC LIMIT 20"

# All members with donation records
sqlite3 bohemian_grove.db "SELECT name, camp, political_donations FROM members WHERE political_donations IS NOT NULL ORDER BY camp"

# Members with no data yet
sqlite3 bohemian_grove.db "SELECT name, camp FROM members WHERE employer IS NULL AND notes IS NULL AND political_donations IS NULL ORDER BY camp, name"
```

## Web Viewer

A static DataTables site hosted on GitHub Pages. Live at: https://benchoff.github.io/weavingspider/

To rebuild after database changes:

```bash
python build.py          # exports docs/data.json
# commit and push docs/  # GitHub Pages picks it up automatically
```

To browse locally just open `docs/index.html` in a browser — or run any static file server:

```bash
python -m http.server -d docs
# Open http://localhost:8000
```

Features: sortable table, global search, camp dropdown filter, "Has Employer" / "Has Donations" checkboxes, click any row for a full detail modal.

## Scripts

**`build.py`** — Export the database to `docs/data.json`. Run this after any database changes before committing.

```bash
python build.py
```

**`update_employers.py`** — Load research results into the database. Accepts one or more JSON files. Uses `COALESCE` so it never overwrites existing data.

```bash
python update_employers.py results/*.json
```

JSON format for new research files:

```json
[
  {
    "name": "LastName, FirstName",
    "employer": "...",
    "title": "...",
    "employer_source": "https://...",
    "political_donations": "...",
    "opensecrets_url": "https://...",
    "ngos": "...",
    "notes": "..."
  }
]
```

**`export_report.py`** — Export the database to `bohemian_grove.csv` and a standalone `bohemian_grove_report.html`.

```bash
python export_report.py
```

**`parse_grove.py`** — Original parser that built the database from `bohemian_grove.json`.

**`find_multiword.py`** — Utility for finding multi-word names in the source data.

## Source Files

- **`Daniel_Boguslaw_Bohemain_Grove_List.pdf`** — Scanned source membership list
- **`bohemian_grove.json`** — Parsed name + camp data (2,202 members)
- **`bohemian_grove_layout.txt`** — Notes on camp layout and structure

## Camps

The Grove has ~60 named camps ranging from ~30 to ~106 members. The largest are Mandalay (67), Aorangi Aviary (106), and Tunerville (69). Notable camps include Mandalay (traditionally hosts the most senior members), Owl's Nest (where Nixon famously decided not to run in 1968), and Cave Man.
