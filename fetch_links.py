import re
import requests

# 1. 在这里输入你需要解析的 Shopee 商品链接
URLS = [
    "https://shopee.co.id/product/965090902/40625686177",
    # 可以在下面继续添加更多链接...
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://shopee.co.id/",
}


def parse_shopee_url(url):
    match = re.search(r"product/(\d+)/(\d+)", url)
    if match:
        return match.group(1), match.group(2)
    match = re.search(r"i\.(\d+)\.(\d+)", url)
    if match:
        return match.group(1), match.group(2)
    return None, None


extracted_links = []

for url in URLS:
    shopid, itemid = parse_shopee_url(url)
    if not shopid or not itemid:
        print(f"❌ 无法解析的链接: {url}")
        continue

    api_url = (
        f"https://shopee.co.id/api/v4/item/get?itemid={itemid}&shopid={shopid}"
    )

    try:
        res = requests.get(api_url, headers=HEADERS, timeout=10)
        data = res.json()
        images = data.get("data", {}).get("images", [])

        if images:
            first_hash = images[0]
            img_url = f"https://down-id.img.susercontent.com/file/{first_hash}"
            print(f"✅ ItemID {itemid}: {img_url}")
            extracted_links.append(f"{itemid}: {img_url}")
        else:
            print(f"⚠️ 未找到主图: {itemid}")

    except Exception as e:
        print(f"❌ 请求失败 ({itemid}): {e}")

# 将提取到的所有主图链接写入 txt 文件
with open("image_links.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(extracted_links))

print("\n🎉 链接提取完成，已保存至 image_links.txt")
