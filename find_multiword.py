import re

with open("bohemian_grove_layout.txt", encoding="utf-8", errors="replace") as f:
    lines = [l.rstrip("\r\n") for l in f]

prev_had_both = False
prev_line = ""
for i, line in enumerate(lines):
    if not line.strip():
        prev_had_both = False
        continue
    line_clean = line.replace("\x0c", "")
    if re.match(r'^\s*Camp\s+Member Name', line_clean):
        prev_had_both = False
        continue
    if re.match(r'^\s*Camp\s*$', line_clean):
        prev_had_both = False
        continue
    if line_clean and line_clean[0] != ' ':
        m = re.match(r'^(\S.*?)\s{2,}(.+)$', line_clean)
        has_member = bool(m)
        if has_member and prev_had_both:
            print(f"Line {i+1}: [{prev_line[:50]}] THEN [{line_clean[:50]}]")
        prev_had_both = has_member
        prev_line = line_clean
    else:
        prev_had_both = False
