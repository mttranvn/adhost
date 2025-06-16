import requests
import os
import subprocess

API_TOKEN = os.getenv("CF_API_TOKEN")
ACCOUNT_ID = "ee2cf540f158ad97275ca8c4fb55cca6"  # 👈 THAY bằng Account ID của bạn
BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/gateway/lists"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

os.makedirs("logs", exist_ok=True)

def get_all_lists():
    response = requests.get(BASE_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json()["result"]

def get_items_from_list(list_id):
    items = []
    page = 1
    per_page = 1000
    while True:
        url = f"{BASE_URL}/{list_id}/items"
        response = requests.get(url, headers=HEADERS, params={"page": page, "per_page": per_page})
        response.raise_for_status()
        data = response.json()
        items.extend([item["value"] for item in data["result"]])
        if page * per_page >= data["result_info"]["total_count"]:
            break
        page += 1
    return items

def export_all_lists():
    all_domains = set()
    log_lines = []

    all_lists = get_all_lists()
    for lst in all_lists:
        print(f"⏳ Đang xử lý list: {lst['name']}")
        domains = get_items_from_list(lst["id"])
        all_domains.update(domains)
        log_lines.append(f"--- {lst['name']} ({len(domains)} domains) ---")
        log_lines.extend(domains)
        log_lines.append("")  # Dòng trống

    with open("my-blocklist.txt", "w") as f:
        for domain in sorted(all_domains):
            f.write(domain + "\n")

    with open("logs/list_details.log", "w") as f:
        f.write("\n".join(log_lines))

    print(f"✅ Đã xuất {len(all_domains)} domain vào my-blocklist.txt")
    print(f"📄 Log chi tiết đã ghi vào logs/list_details.log")

def git_commit_push():
    subprocess.run(["git", "config", "user.email", "github-actions@users.noreply.github.com"])
    subprocess.run(["git", "config", "user.name", "GitHub Actions"])
    subprocess.run(["git", "add", "my-blocklist.txt", "logs/list_details.log"])
    subprocess.run(["git", "commit", "-m", "Update blocklist and log from Cloudflare lists"], check=False)
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    export_all_lists()
    git_commit_push()
