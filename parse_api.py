import os
import re
import requests

# 1. 从环境变量中读取你在网页端输入的内容
input_text = os.getenv("USER_INPUT", "")

# 匹配文本中所有的 Shopee API 链接
api_urls = re.findall(r"https?://[^\s]+api/v4/item/get[^\s]+", input_text)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://shopee.co.id/",
}

results = []
image_links_only = []

for url in api_urls:
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            item_data = data.get("data") or data.get("item") or {}
            images = item_data.get("images", [])

            if images:
                first_hash = images[0]
                img_url = (
                    f"https://down-id.img.susercontent.com/file/{first_hash}"
                )
                results.append(f"| `{url[:40]}...` | {img_url} |")
                image_links_only.append(img_url)
            else:
                results.append(f"| `{url[:40]}...` | ⚠️ 未找到 images 字段 |")
        else:
            results.append(
                f"| `{url[:40]}...` | ❌ 请求失败 (HTTP {res.status_code}) |"
            )
    except Exception as e:
        results.append(f"| `{url[:40]}...` | ❌ 异常: {str(e)} |")

# 将生成的 Markdown 结果写入 GITHUB_STEP_SUMMARY（会自动直接显示在 GitHub 运行页面）
summary_content = "### 🚀 批量提取主图链接成功！\n\n| API 链接预览 | 生成的主图 CDN 链接 |\n|---|---|\n"
summary_content += "\n".join(results) + "\n\n"
summary_content += "#### 📋 纯链接列表（方便直接复制）：\n```text\n"
summary_content += "\n".join(image_links_only) + "\n```"

with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
    f.write(summary_content)

# 同时更新覆盖保存到 image_links.txt 文件中
with open("image_links.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(image_links_only) + "\n")
