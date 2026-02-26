#!/usr/bin/env python3
"""
Parse Bohemian Grove member list from layout-extracted PDF text.
Produces bohemian_grove.db (SQLite) and bohemian_grove.json.
"""

import re
import json
import sqlite3

INPUT_FILE = "bohemian_grove_layout.txt"

# Multi-word camp names that get split across two lines in the PDF layout
# The PDF stores "Word1" on one row and "Word2" on the next; both rows have members.
# Parser would split these into two camps; we need to JOIN them.
JOIN_CAMPS = {
    "Aorangi": "Aorangi Aviary",   # "Aviary" appears on next line
    "Aviary": "Aorangi Aviary",
}

# Camps that get MERGED by the parser because the first word appears solo
# (no member) and the second word appears on the next line WITH a member.
# The parser incorrectly joins them; we split them by renaming.
# Format: "WrongMergedName" -> "CorrectCampName"  (first word had 0 members)
RENAME_CAMPS = {
    "Care Less Cave Man":                       "Cave Man",
    "Hideaway Highlanders":                     "Highlanders",
    "Hillside Hualapai":                        "Hualapai",
    "Idlewild Interlude":                       "Interlude",
    "Iron Ring Isle of Aves":                   "Isle of Aves",
    "Cliff Dwellers/Aviary Cliff Dwellers/Band":"Cliff Dwellers/Band",
    "Pig 'N Whistle/Jinks Band Pig N Whistle":  "Pig N Whistle",
    "Whoo Cares/Jinks Band Wild Oats":          "Wild Oats",
    "Saug Harbor Sempervirens":                 "Sempervirens",
    "Sheldrake Lodge Shoestring":               "Shoestring",
    "Mathien Mathieu":                          "Mathieu",
    "Log Crossroads Lost Angels":               "Lost Angels",
    "Last Chance Log Crossroads":               "Log Crossroads",
}


def split_line(line):
    """Return (camp_fragment, member_name) from a layout-preserved line."""
    line = line.replace("\x0c", "").rstrip("\r\n")
    if not line.strip():
        return None, None
    if re.match(r'^\s*Camp\s+Member Name', line):
        return None, None
    if re.match(r'^\s*Camp\s*$', line.strip()):
        return None, None
    if re.match(r'^\s*Member Name\s*$', line.strip()):
        return None, None

    if line[0] != ' ':
        # Content starts at col 0 — has a camp fragment in the left zone
        m = re.match(r'^(\S.*?)\s{2,}(.+)$', line)
        if m:
            left = m.group(1).strip()
            right = m.group(2).strip()
            if left == "Abbey":
                # Section header, not a camp name; the right side is a member
                return None, right
            return left, right
        else:
            left = line.strip()
            if left in ("Abbey", "Camp", "Member Name"):
                return None, None
            return left, None
    else:
        member = line.strip()
        if member in ("Camp", "Member Name"):
            return None, None
        return None, member if member else None


def parse_members(filepath):
    members = []
    current_camp = "Unknown"
    pending_camp_parts = []
    prev_had_member = False

    with open(filepath, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    for line in lines:
        camp_frag, member = split_line(line)

        if camp_frag is None and member is None:
            continue

        if camp_frag is not None:
            if prev_had_member:
                # Close previous camp, start fresh
                if pending_camp_parts:
                    current_camp = " ".join(pending_camp_parts)
                    pending_camp_parts = []
                pending_camp_parts = [camp_frag]
            else:
                pending_camp_parts.append(camp_frag)

            if member is not None:
                current_camp = " ".join(pending_camp_parts)
                pending_camp_parts = []
                # Apply join-camps correction
                current_camp = JOIN_CAMPS.get(current_camp, current_camp)
                members.append({"name": member, "camp": current_camp})
                prev_had_member = True
            else:
                prev_had_member = False
        else:
            # Member-only line
            if pending_camp_parts:
                current_camp = " ".join(pending_camp_parts)
                current_camp = JOIN_CAMPS.get(current_camp, current_camp)
                pending_camp_parts = []
            if member:
                members.append({"name": member, "camp": current_camp})
            prev_had_member = False

    return members


def post_process(members):
    """Apply rename corrections and deduplicate."""
    fixed = []
    seen = set()
    for m in members:
        camp = RENAME_CAMPS.get(m["camp"], m["camp"])
        # Also clean up the "Band/LOH" prefix that sometimes bleeds into camp names
        if camp.startswith("Band/LOH "):
            camp = camp[len("Band/LOH "):].strip()
        key = (m["name"].lower(), camp.lower())
        if key not in seen:
            seen.add(key)
            fixed.append({"name": m["name"], "camp": camp})
    return fixed


def main():
    raw_members = parse_members(INPUT_FILE)
    members = post_process(raw_members)

    # Write JSON
    with open("bohemian_grove.json", "w", encoding="utf-8") as f:
        json.dump(members, f, indent=2)

    # Write SQLite
    conn = sqlite3.connect("bohemian_grove.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS members")
    cur.execute("""
        CREATE TABLE members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            camp TEXT NOT NULL,
            employer TEXT,
            employer_title TEXT,
            employer_source TEXT,
            notes TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_camp ON members(camp)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_name ON members(name)")

    for m in members:
        cur.execute("INSERT INTO members (name, camp) VALUES (?, ?)",
                    (m["name"], m["camp"]))
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM members")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT camp) FROM members")
    camp_count = cur.fetchone()[0]
    print(f"Total members: {total}")
    print(f"Total camps:   {camp_count}\n")

    print("All camps (by member count, descending):")
    cur.execute("""
        SELECT camp, COUNT(*) as cnt
        FROM members GROUP BY camp ORDER BY cnt DESC, camp
    """)
    for row in cur.fetchall():
        print(f"  {row[1]:4d}  {row[0]}")

    conn.close()
    print(f"\nOutput: bohemian_grove.db  (SQLite)")
    print(f"Output: bohemian_grove.json")


if __name__ == "__main__":
    main()
