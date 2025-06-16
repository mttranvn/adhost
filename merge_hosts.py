import os
import requests
import re

def is_valid_host_line(line: str) -> str | None:
    """
    Trích xuất domain từ dòng host hợp lệ.
    Hợp lệ: bắt đầu bằng 0.0.0.0 hoặc 127.0.0.1
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    match = re.match(r"^(?:0\.0\.0\.0|127\.0\.0\.1)\s+([^\s#]+)", line)
    return match.group(1).lower() if match else None

def main():
    urls = os.getenv("NGUON_URLS", "").strip().splitlines()
    if not urls:
        print("❌ Không có URL nào trong biến NGUON_URLS.")
        return

    domains = set()

    for url in urls:
        try:
            print(f"🔽 Đang tải: {url}")
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    domain = is_valid_host_line(line)
                    if domain:
                        domains.add(domain)
            else:
                print(f"⚠️ Lỗi khi tải {url}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Lỗi khi tải {url}: {e}")

    output_file = "merged_blocklist.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for domain in sorted(domains):
            f.write(f"{domain}\n")

    print(f"✅ Hoàn tất. Đã ghi {len(domains)} domain vào {output_file}")

if __name__ == "__main__":
    main()
