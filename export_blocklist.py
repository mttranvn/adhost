import os
import requests

API_TOKEN = os.getenv("CF_API_TOKEN")
ACCOUNT_ID = "ee2cf540f158ad97275ca8c4fb55cca6"  # sửa lại đúng
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

LISTS_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/gateway/lists"

def fetch_lists():
    resp = requests.get(LISTS_URL, headers=HEADERS)
    data = resp.json()
    if not data.get("success", False):
        raise RuntimeError("❌ Không thể lấy danh sách.")
    return data["result"]

def fetch_items(list_id):
    items = []
    page = 1
    while True:
        url = f"{LISTS_URL}/{list_id}/items?page={page}&per_page=1000"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            raise RuntimeError(f"❌ Lỗi khi tải list {list_id}: {resp.status_code} {resp.text}")
        result = resp.json().get("result", [])
        if not result:
            break
        items.extend(result)
        if len(result) < 1000:
            break
        page += 1
    return items

def main():
    print("📦 Đang lấy danh sách...")
    lists = fetch_lists()
    print(f"✅ Tìm thấy {len(lists)} danh sách")

    all_domains = []
    log_lines = []

    for lst in lists:
        list_id = lst["id"]
        list_name = lst["name"]
        list_type = lst.get("type", "UNKNOWN")

        try:
            items = fetch_items(list_id)
            domains = [item["value"] for item in items if "value" in item]
            all_domains.extend(domains)
            log_lines.append(f"[{list_name}] ({list_type}) - {len(domains)} mục")
        except Exception as e:
            log_lines.append(f"[{list_name}] ({list_type}) - Lỗi: {str(e)}")

    # Ghi domain ra file
    with open("my-blocklist.txt", "w") as f:
        for domain in sorted(set(all_domains)):
            f.write(domain.strip() + "\n")

    # Ghi log
    os.makedirs("logs", exist_ok=True)
    with open("logs/list_details.log", "w") as logf:
        for line in log_lines:
            logf.write(line + "\n")

    print("✅ Đã xuất xong my-blocklist.txt và logs/list_details.log")

if __name__ == "__main__":
    main()
