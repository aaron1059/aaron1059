import requests
import urllib.parse
from datetime import datetime, timedelta, timezone

SCKEY = "SCT334015TjyKtNeAukyNnmDI1jJCcLgqt"
KEYWORDS = ["育碧", "Ubisoft", "UBI", "拼多多", "PDD", "Temu"]
HOURS = 24
MAX_NEWS = 8

def get_google_news(keyword):
    news = []
    now = datetime.now(timezone.utc)
    since_time = now - timedelta(hours=HOURS)
    since_str = since_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=zh-CN&gl=CN&since={since_str}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=12)
        items = r.text.split("<item>")
        for item in items[1:]:
            try:
                title = item.split("<title>")[1].split("</title>")[0].strip()
                desc_part = item.split("<description>")[1].split("</description>")[0].strip()
                link = item.split("<link>")[1].split("</link>")[0].strip()
                news.append({
                    "title": title,
                    "desc": desc_part,
                    "link": link
                })
            except:
                continue
    except:
        pass
    return news

if __name__ == "__main__":
    all_news = []
    for kw in KEYWORDS:
        all_news.extend(get_google_news(kw))

    # 超强去重：标题一模一样直接删掉
    seen_titles = set()
    unique_news = []
    for n in all_news:
        if n["title"] not in seen_titles:
            seen_titles.add(n["title"])
            unique_news.append(n)

    unique_news = unique_news[:MAX_NEWS]

    lines = []
    for n in unique_news:
        lines.append(
            f"【新闻标题】{n['title']}\n\n"
            f"【新闻完整内容】\n{n['desc']}\n\n"
            f"🔗 链接：{n['link']}\n"
        )

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    desp = "\n" + "="*60 + "\n".join(lines)

    requests.post(
        f"https://sctapi.ftqq.com/{SCKEY}.send",
        data={
            "title": f"【新闻全文版】育碧/PDD/TEMU {today}",
            "desp": desp
        },
        timeout=10
    )
