import requests
import urllib.parse
from datetime import datetime

SCKEY = "SCT334015TjyKtNeAukyNnmDI1jJCcLgqt"
KEYWORDS = ["并购", "收购", "破产", "重组", "拆分"]
MAX_NEWS = 10

def get_baidu_news(keyword):
    news = []
    url = f"https://news.baidu.com/ns?word={urllib.parse.quote(keyword)}&pn=0&cl=2&ct=1&tn=newsrss"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        items = r.text.split("<item>")
        for item in items[1:]:
            try:
                title = item.split("<title>")[1].split("</title>")[0].strip()
                link = item.split("<link>")[1].split("</link>")[0].strip()
                news.append({"title": title, "link": link})
            except:
                continue
    except:
        pass
    return news

if __name__ == "__main__":
    all_news = []
    for kw in KEYWORDS:
        all_news.extend(get_baidu_news(kw))

    seen = set()
    final_news = []
    for n in all_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            final_news.append(n)

    final_news = final_news[:MAX_NEWS]
    lines = [f"【新闻】{n['title']}\n🔗 {n['link']}" for n in final_news]
    today = datetime.utcnow().strftime("%Y-%m-%d")
    desp = "\n\n----------------\n\n".join(lines) if lines else "今日暂无新闻"

    requests.post(f"https://sctapi.ftqq.com/{SCKEY}.send", data={
        "title": f"【国内新闻】并购/重组/破产 {today}",
        "desp": desp
    }, timeout=10)
