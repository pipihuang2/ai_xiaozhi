import requests

GITHUB_TOKEN = ""
OWNER = "pipihuang2"
REPO = "miaomiao_cat"

url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

params = {
    "state": "open",  # 只获取打开的 PR
    "per_page": 100,  # 每页最多 100 条
    "page": 1         # 当前页码
}

all_prs = []

while True:
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch PRs. Status code: {response.status_code}")
        break

    prs = response.json()
    if not prs:
        break

    all_prs.extend(prs)
    params["page"] += 1

print(f"Total open PRs: {len(all_prs)}")
for pr in all_prs:
    print(f"PR #{pr['number']}: {pr['title']} (by {pr['user']['login']})")

    # 获取每个 PR 的文件改动
    pr_files_url = pr['url'] + '/files'
    pr_files_response = requests.get(pr_files_url, headers=headers)
    if pr_files_response.status_code == 200:
        files = pr_files_response.json()
        for file in files:
            print(f"  File: {file['filename']}")
            print(f"  Status: {file['status']}")
            print(f"  Changes: {file['changes']} lines")
            # 如果想查看具体差异（diff），可以使用 'patch' 字段
            print(f"  Diff: {file['patch']}\n")
    else:
        print(f"Failed to fetch files for PR #{pr['number']}. Status code: {pr_files_response.status_code}")