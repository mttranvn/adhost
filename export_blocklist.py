import os
import requests

# Cấu hình
API_TOKEN = os.getenv("CF_API_TOKEN")
ACCOUNT_ID = "ee2cf540f158ad97275ca8c4fb55cca6"  # ← THAY ĐÚNG TỪ CLOUDFLARE DASHBOARD
LISTS_ENDPOINT = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/gateway/lists"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Output paths
blocklist_path = "my-blocklist.txt"
log_path = "logs/list_details.log"

# Tạo thư mục log nếu chưa có
os.makedirs("logs", exist_ok=True)

# Biến lưu trữ tạm
all_domains = []
log_lines = []

def fetch_lists():
    resp = requests.get(LISTS_ENDPOINT, headers=HEADERS)
    if not resp.ok:
        raise RuntimeError(f"❌ Failed to fetch lists: {resp.status_code} {resp.text}")
    return resp.json()["result"]

def fetch_list_items(list_id):
    url = f"{LISTS_ENDPOINT}/{list_id}/items"
    resp = requests.get(url, headers=HEADERS)

    if resp.status_code == 502:
        print(f"⚠️  Skipping list {list_id} due to 502 Bad Gateway")
        log_lines.append(f"⚠️  Bỏ qua list {list_id} vì lỗi 502 Bad Gateway\n")
        return []

    if not resp.ok:
        raise RuntimeError(f"❌ Failed to fetch items for list {list_id}: {resp.status_code} {resp.text}")

    return resp.json()["result"]

def main():
    print("📦 Fetching Cloudflare Gateway Lists...")
    lists = fetch_lists()
    print(f"✅ Found {len(lists)} lists")

    hostname_lists = [lst for lst in lists if lst.get("type") == "HOSTNAME"]
    print(f"🔍 Filtering HOSTNAME lists → {len(hostname_lists)} lists")

    for lst in hostname_lists:
        name = lst["name"]
        list_id = lst["id"]
        log_lines.append(f"📂 Danh sách: {name} ({list_id})")

        items = fetch_list_items(list_id)
        count = 0
        for item in items:
            domain = item.get("value", "").strip()
            if domain:
                all_domains.append(domain)
                log_lines.append(f"  - {domain}")
                count += 1

        log_lines.append(f"🔢 Tổng cộng: {count} domain\n")

    # Ghi ra blocklist
    with open(blocklist_path, "w") as f:
        f.write("\n".join(sorted(set(all_domains))) + "\n")

    # Ghi log
    with open(log_path, "w") as f:
        f.write("\n".join(log_lines))

    print(f"✅ Exported {len(set(all_domains))} unique domains to {blocklist_path}")
    print(f"📝 Log written to {log_path}")

if __name__ == "__main__":
    main()
