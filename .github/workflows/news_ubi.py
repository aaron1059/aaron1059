import requests
import urllib.parse
from datetime import datetime

keywords = ["育碧", "Ubisoft", "UBI", "拼多多", "PDD", "Temu"]

news_list = []

for kw in keywords:
    try:
        url = f"https://news.google.com/rss/search?q={kw}&hl=zh-CN&gl=CN"
        r = requests.get(url, timeout=10)
        items = r.text.split("<item>")
        
        for item in items[1:11]:
            try:
                title = item.split("<title>")[1].split("</title>")[0]
                link = item.split("<link>")[1].split("</link>")[0]
                q = urllib.parse.quote(title)

                wechat = f"https://weixin.sogou.com/weixin?type=2&query={q}"
                baidu = f"https://news.baidu.com/ns?word={q}&tn=news&lm=24"
                youtube = f"https://www.youtube.com/results?search_query={q}"

                news_list.append(f"• {title}\n📱 微信可看：{wechat}\n🔗 国内24h：{baidu}\n🌍 Google：{link}\n▶️ YouTube：{youtube}")
            except:
                continue
    except:
        continue

news_list = list(dict.fromkeys(news_list))[:30]
today = datetime.utcnow().strftime("%Y-%m-%d")

SCKEY = "SCT334015TjyKtNeAukyNnmDI1jJCcLgqt"
requests.post(f"https://sctapi.ftqq.com/{SCKEY}.send", data={
    "title": f"【育碧/PDD/TEMU 新闻 {today}】",
    "desp": "\n\n".join(news_list) if news_list else "今日暂无新闻"
})
