#!/usr/bin/env python3
# Placeholder generator: fetch sources & write daily page (manual curation for now)
import datetime, pathlib

root = pathlib.Path('/Users/kenefe/LOCAL/momo-agent/daily-brief')
(date,) = (datetime.date.today().isoformat(),)

# For now, just ensure a daily page exists.
path = root / 'daily' / f"{date}.html"
if not path.exists():
    path.write_text(f"""<!doctype html><html><head><meta charset='utf-8'><title>{date}</title></head><body><h1>{date}</h1><p>Placeholder</p></body></html>""")

print(path)
