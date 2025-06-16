import os
import requests
import re

urls = os.getenv("NGUON_URLS", "").strip().splitlines()
domains = set()

for url in urls:
    try:
        print(f"🔽 Fetching: {url}")
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            for line in resp.text.splitlines():
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                match = re.match(r"^(?:0\.0\.0\.0|127\.0\.0\.1)\s+([^\s#]+)", line)
                if match:
                    domains.add(match.group(1).lower())
        else:
            print(f"⚠️ Failed to fetch {url}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")

# Ghi ra file
with open("merged_blocklist.txt", "w", encoding="utf-8") as f:
    for domain in sorted(domains):
        f.write(f"{domain}\n")

print(f"✅ Done! Extracted {len(domains)} unique domains.")
