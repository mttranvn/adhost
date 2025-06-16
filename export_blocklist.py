import os
import requests

# Nhập ID tài khoản Cloudflare của bạn tại đây
ACCOUNT_ID = "ee2cf540f158ad97275ca8c4fb55cca6"

# Token được truyền qua biến môi trường
API_TOKEN = os.getenv("CF_API_TOKEN")

if not API_TOKEN:
    raise ValueError("❌ CF_API_TOKEN is not set. Please add it as a GitHub Secret.")

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

LISTS_ENDPOINT = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/gateway/lists"

# Tạo thư mục logs nếu chưa có
os.makedirs("logs", exist_ok=True)

blocklist_path = "my-blocklist.txt"
log_path = "logs/list_details.log"

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
    if not resp.ok:
        raise RuntimeError(f"❌ Failed to fetch items for list {list_id}: {resp.status_code} {resp.text}")
    return resp.json()["result"]

def main():
    print("📦 Fetching Cloudflare Gateway Lists...")
    lists = fetch_lists()
    print(f"✅ Found {len(lists)} lists")

    for lst in lists:
        name = lst["name"]
        list_id = lst["id"]
        log_lines.append(f"📂 Danh sách: {name} ({list_id})")

        items = fetch_list_items(list_id)
        for item in items:
            domain = item.get("value", "").strip()
            if domain:
                all_domains.append(domain)
                log_lines.append(f"  - {domain}")

        log_lines.append("")

    # Ghi ra file chính
    with open(blocklist_path, "w") as f:
        f.write("\n".join(sorted(set(all_domains))) + "\n")

    # Ghi log chi tiết
    with open(log_path, "w") as f:
        f.write("\n".join(log_lines))

    print(f"✅ Exported {len(all_domains)} domains to {blocklist_path}")
    print(f"📝 Log written to {log_path}")

if __name__ == "__main__":
    main()
