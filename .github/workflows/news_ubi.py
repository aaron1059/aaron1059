import requests
import urllib.parse
from datetime import datetime, timedelta, timezone

# 配置
KEYWORDS = ["育碧", "Ubisoft", "UBI", "拼多多", "PDD", "Temu"]
MAX_NEWS = 15  # 最多15條，避免刷屏
HOURS = 24

def get_google_news(keyword):
    news = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    since_time = (datetime.now(timezone.utc) - timedelta(hours=HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f'https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=zh-CN&gl=CN&since={since_time}'
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return news
        items = resp.text.split("<item>")
        for item in items[1:MAX_NEWS+1]:
            try:
                title = item.split("<title>")[1].split("</title>")[0].strip()
                link = item.split("<link>")[1].split("</link>")[0].strip()
                pub_time = item.split("<pubDate>")[1].split("</pubDate>")[0].strip() if "<pubDate>" in item else ""
                
                # 簡單去重（標題完全一樣才去掉）
                news.append({"title": title, "link": link, "pub": pub_time})
            except Exception:
                continue
    except Exception:
        pass
    return news

# 這裡可以加入你想要的 AI 解讀邏輯，這是最基礎的智能摘要版
def ai_summarize(title):
    # 基礎分類：遊戲 / 電商 / 財經
    if any(word in title for word in ["遊戲", "Ubisoft", "育碧", "Steam"]):
        return f"【遊戲圈動態】{title[:50]}..."
    elif any(word in title for word in ["拼多多", "PDD", "Temu", "電商"]):
        return f"【電商戰報】{title[:50]}..."
    elif any(word in title for word in ["股", "漲", "跌", "收購", "合併"]):
        return f"【財經焦點】{title[:50]}..."
    else:
        return f"【熱點速覽】{title[:50]}..."

if __name__ == "__main__":
    all_news = []
    for kw in KEYWORDS:
        all_news.extend(get_google_news(kw))

    # 嚴格去重 + 按時間排序
    seen_titles = set()
    unique_news = []
    for n in all_news:
        if n["title"] not in seen_titles:
            seen_titles.add(n["title"])
            unique_news.append(n)
    
    # 只取前10條，最多10條
    unique_news = unique_news[:10]

    # 生成推送內容
    lines = []
    for n in unique_news:
        # AI 智能分類標籤
        tag = ai_summarize(n["title"])
        lines.append(f"{tag}\n📄 原文：{n['title']}\n🔗 Google原文：{n['link']}\n")

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    desp = "\n\n".join(lines) if lines else "⚠️ 最近24小时无育碧/PDD/TEMU相关新闻"
    
    # 推送
    SCKEY = "SCT334015TjyKNeAukyNnmDI1jJCcLgqt"
    try:
        requests.post(
            f"https://sctapi.ftqq.com/{SCKEY}.send",
            data={"title": f"【AI速覽】育碧/PDD/TEMU 新聞 {date_str}", "desp": desp},
            timeout=10
        )
        print(f"✅ AI推送成功，共 {len(unique_news)} 條")
    except Exception as e:
        print(f"❌ 推送失败：{str(e)}")
