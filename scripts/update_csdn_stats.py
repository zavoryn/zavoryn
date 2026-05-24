"""Fetch CSDN profile stats and update README.md."""
import re
import urllib.request


CSDN_URL = "https://blog.csdn.net/qq_62915969?type=blog"
README_PATH = "README.md"


def fetch_stats():
    req = urllib.request.Request(CSDN_URL, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8")

    # Profile statistics: 总访问量, 原创, 粉丝, 关注
    stat_blocks = re.findall(
        r'user-profile-statistics-num[^>]*>([^<]+)<.*?'
        r'user-profile-statistics-name[^>]*>([^<]+)<',
        html, re.DOTALL
    )
    stats = {}
    for val, name in stat_blocks:
        stats[name.strip()] = val.strip()

    # Aside stats: 点赞, 评论, 收藏, 排名
    aside_blocks = re.findall(
        r'aside-common-box-content-text[^>]*>(.*?)</div>',
        html, re.DOTALL
    )
    for block in aside_blocks:
        text = re.sub(r'<[^>]+>', '', block).strip()
        m = re.match(r'获得(\d+)次点赞', text)
        if m:
            stats["点赞"] = m.group(1)
        m = re.match(r'获得(\d+)次收藏', text)
        if m:
            stats["收藏"] = m.group(1)
        m = re.match(r'博客总排名([\d,]+)名', text)
        if m:
            stats["排名"] = m.group(1).replace(",", "")

    return stats


def format_views(n):
    n = int(n.replace(",", ""))
    if n >= 10000:
        return f"{n / 10000:.1f}w"
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


def update_readme(stats):
    views_raw = stats.get("总访问量", "0")
    likes = stats.get("点赞", "0")
    collects = stats.get("收藏", "0")
    views = format_views(views_raw)

    badges = (
        f"  ![](https://img.shields.io/badge/阅读-{views}-2088FF"
        f"?style=flat-square&logo=readthedocs&logoColor=white) "
        f"![](https://img.shields.io/badge/点赞-{likes}-FF6B6B"
        f"?style=flat-square&logo=thumbsup&logoColor=white) "
        f"![](https://img.shields.io/badge/收藏-{collects}-FFD700"
        f"?style=flat-square&logo=star&logoColor=white)"
    )

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(
        r'(<!-- CSDN-STATS:START -->\n).*?(<!-- CSDN-STATS:END -->)',
        f'\\1{badges}\n\\2',
        content,
        flags=re.DOTALL,
    )

    if new_content == content:
        print("No changes.")
        return False

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Updated: 阅读={views}, 点赞={likes}, 收藏={collects}")
    return True


if __name__ == "__main__":
    stats = fetch_stats()
    print(f"Fetched stats: {stats}")
    update_readme(stats)
