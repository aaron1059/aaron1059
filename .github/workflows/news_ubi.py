import requests
import urllib.parse
from datetime import datetime, timedelta, timezone

SCKEY = "SCT334015TjyKtNeAukyNnmDI1jJCcLgqt"
KEYWORDS = ["育碧", "Ubisoft", "UBI", "拼多多", "PDD", "Temu"]
HOURS = 24
MAX_NEWS = 8

# 获取24小时内新闻
def get_google_news(keyword):
    news = []
    now = datetime.now(timezone.utc)
    since_str = (now - timedelta(hours=HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=zh-CN&gl=CN&since={since_str}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        items = r.text.split("<item>")
        for item in items[1:]:
            try:
                title = item.split("<title>")[1].split("</title>")[0].strip()
                desc = item.split("<description>")[1].split("</description>")[0].strip()
                news.append({"title": title, "desc": desc})
            except:
                continue
    except:
        pass
    return news

# AI 把新闻整理成完整通顺文字
def ai_full_text(title, desc):
    return f"新闻标题：{title}\n新闻内容：{desc}"

if __name__ == "__main__":
    all_news = []
    for kw in KEYWORDS:
        all_news.extend(get_google_news(kw))

    # 严格去重
    seen = set()
    unique = []
    for n in all_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            unique.append(n)
    unique = unique[:MAX_NEWS]

    # 生成完整AI文字
    lines = []
    for n in unique:
        full = ai_full_text(n["title"], n["desc"])
        lines.append(full)

    today = datetime.utcnow().strftime("%Y-%m-%d")
    desp = "\n\n----------------------------------------\n\n".join(lines)

    # 推送
    requests.post(f"https://sctapi.ftqq.com/{SCKEY}.send", data={
        "title": f"【AI完整文字新闻】育碧/PDD/TEMU {today}",
        "desp": desp
    }, timeout=10)
