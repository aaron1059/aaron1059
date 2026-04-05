import requests
import urllib.parse
from datetime import datetime, timedelta, timezone

# 你的 KEY 正确，不用改
SCKEY = "SCT334015TjyKtNeAukyNnmDI1jJCcLgqt"
KEYWORDS = ["育碧", "Ubisoft", "UBI", "拼多多", "PDD", "Temu"]
MAX_NEWS = 10
HOURS = 24

def get_google_news(keyword):
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}
    since_time = (datetime.now(timezone.utc) - timedelta(hours=HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f'https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=zh-CN&gl=CN&since={since_time}'
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        items = resp.text.split("<item>")
        for item in items[1:MAX_NEWS+1]:
            try:
                title = item.split("<title>")[1].split("</title>")[0].strip()
                link = item.split("<link>")[1].split("</link>")[0].strip()
                news.append({"title": title, "link": link})
            except Exception:
                continue
    except Exception:
        pass
    return news

# AI 分类标签
def ai_tag(title):
    if any(word in title for word in ["游戏", "育碧", "Ubisoft"]):
        return "【游戏动态】"
    elif any(word in title for word in ["拼多多", "PDD", "Temu"]):
        return "【电商热点】"
    else:
        return "【最新消息】"

if __name__ == "__main__":
    all_news = []
    for kw in KEYWORDS:
        all_news.extend(get_google_news(kw))

    # 严格去重
    seen = set()
    final_news = []
    for n in all_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            final_news.append(n)
    final_news = final_news[:10]

    # 生成内容
    lines = []
    for n in final_news:
        tag = ai_tag(n["title"])
        lines.append(f"{tag}\n{n['title']}\n🔗 {n['link']}\n")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    content = "\n".join(lines)

    # 推送微信
    requests.post(f"https://sctapi.ftqq.com/{SCKEY}.send", data={
        "title": f"【AI 新闻】育碧 / PDD / TEMU {today}",
        "desp": content
    }, timeout=10)
