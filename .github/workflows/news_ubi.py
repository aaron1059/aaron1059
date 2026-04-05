import requests
import urllib.parse
from datetime import datetime

# 配置
SCKEY = "SCT334015TjyKtNeAukyNnmDI1jJCcLgqt"
# 只监控国内可访问的关键词，对应国内新闻源
KEYWORDS = ["育碧", "拼多多", "Temu"]
MAX_NEWS = 10

# 用百度新闻RSS（国内可访问，链接直接点开）
def get_baidu_news(keyword):
    news = []
    # 百度新闻RSS源，国内直接访问，无墙
    url = f"https://news.baidu.com/ns?word={urllib.parse.quote(keyword)}&pn=0&cl=2&ct=1&tn=newsrss"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        items = r.text.split("<item>")
        for item in items[1:]:
            try:
                title = item.split("<title>")[1].split("</title>")[0].strip()
                link = item.split("<link>")[1].split("</link>")[0].strip()
                # 百度RSS无HTML，直接用
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

    # 严格去重：标题一样直接删
    seen = set()
    final_news = []
    for n in all_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            final_news.append(n)
    
    # 只取前10条，不刷屏
    final_news = final_news[:MAX_NEWS]

    # 生成推送内容（纯标题+国内可点开链接，无AI、无HTML）
    lines = []
    for n in final_news:
        lines.append(f"【新闻】{n['title']}\n🔗 链接：{n['link']}\n")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    desp = "\n\n------------------------\n\n".join(lines) if lines else "今日暂无相关新闻"

    # 推送微信
    requests.post(
        f"https://sctapi.ftqq.com/{SCKEY}.send",
        data={
            "title": f"【国内可点开】育碧/PDD/TEMU 新闻 {today}",
            "desp": desp
        },
        timeout=10
    )
