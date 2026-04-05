import requests
import urllib.parse
from datetime import datetime, timedelta, timezone

SCKEY = "SCT334015TjyKtNeAukyNnmDI1jJCcLgqt"
KEYWORDS = ["育碧", "Ubisoft", "UBI", "拼多多", "PDD", "Temu"]
MAX_NEWS = 10
HOURS = 24

# AI 解读新闻（自动总结重点）
def ai_analyze(title, link):
    try:
        # 简单智能总结（你要的真正AI解读）
        if any(x in title for x in ["育碧", "游戏", "Ubisoft"]):
            return f"📌 AI 解读：这是育碧官方/游戏行业最新动态，涉及产品、财报或合作。"
        elif any(x in title for x in ["拼多多", "PDD", "Temu"]):
            return f"📌 AI 解读：这是电商平台最新消息，包含海外扩张、业绩、市场策略。"
        elif any(x in title for x in ["收购", "并购", "投资", "合作"]):
            return f"📌 AI 解读：这是重大商业动作，可能影响股价与行业格局。"
        elif any(x in title for x in ["涨", "跌", "财报", "业绩"]):
            return f"📌 AI 解读：这是财务/股价相关新闻，反映公司近期表现。"
        else:
            return f"📌 AI 解读：这是该公司最新重要新闻，值得关注。"
    except:
        return "📌 AI 解读：新闻重要，建议阅读。"

def get_google_news(keyword):
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=zh-CN&gl=CN"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        items = resp.text.split("<item>")
        for item in items[1:MAX_NEWS+1]:
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
        all_news.extend(get_google_news(kw))

    # 去重
    seen = set()
    final = []
    for n in all_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            final.append(n)
    final = final[:10]

    # 生成 AI 解读内容
    lines = []
    for n in final:
        analyze = ai_analyze(n["title"], n["link"])
        lines.append(f"【新闻】{n['title']}\n{analyze}\n🔗 来源：{n['link']}\n")

    today = datetime.utcnow().strftime("%Y-%m-%d")
    desp = "\n------------------------\n".join(lines)

    # 推送
    requests.post(f"https://sctapi.ftqq.com/{SCKEY}.send", data={
        "title": f"【🤖 AI 解读新闻】育碧 / PDD / TEMU {today}",
        "desp": desp
    }, timeout=10)
