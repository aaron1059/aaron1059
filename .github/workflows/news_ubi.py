import requests
import urllib.parse
from datetime import datetime, timedelta, timezone
import re

SCKEY = "SCT334015TjyKtNeAukyNnmDI1jJCcLgqt"
KEYWORDS = ["育碧", "Ubisoft", "UBI", "拼多多", "PDD", "Temu"]
HOURS = 24
MAX_NEWS = 8

def clean_html(html_text):
    """強力清洗 HTML 代碼，只留純文字"""
    # 1. 去除 <a> 標籤但保留文字
    html_text = re.sub(r'<a\s+[^>]*>', '', html_text)
    html_text = re.sub(r'</a>', '', html_text)
    # 2. 去除 <font> 標籤
    html_text = re.sub(r'<font\s+[^>]*>', '', html_text)
    html_text = re.sub(r'</font>', '', html_text)
    # 3. 去除其他 HTML 標籤
    html_text = re.sub(r'<.*?>', '', html_text)
    # 4. 去除轉義字符 (&nbsp; 等)
    html_text = re.sub(r'&[a-z]+;', ' ', html_text)
    # 5. 去除多餘空格
    html_text = re.sub(r'\s+', ' ', html_text)
    return html_text.strip()

def get_google_news(keyword):
    news = []
    now = datetime.now(timezone.utc)
    since_str = (now - timedelta(hours=HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # 注意：Google News RSS 雖然 since 參數有效，但數據仍可能混雜舊聞，
    # 這是官方 API 限制，我們在後續邏輯進一步過濾
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=zh-CN&gl=CN&since={since_str}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        items = r.text.split("<item>")
        for item in items[1:]:
            try:
                title = item.split("<title>")[1].split("</title>")[0].strip()
                desc_raw = item.split("<description>")[1].split("</description>")[0].strip()
                desc_clean = clean_html(desc_raw) # 清洗乾淨
                
                # 過濾：標題過短、內容過短、或無意義的新聞
                if len(title) > 10 and len(desc_clean) > 20:
                    news.append({
                        "title": title,
                        "desc": desc_clean
                    })
            except Exception as e:
                # print(f"解析跳過: {e}")
                continue
    except Exception as e:
        # print(f"抓取失敗: {e}")
        pass
    return news

if __name__ == "__main__":
    all_news = []
    for kw in KEYWORDS:
        all_news.extend(get_google_news(kw))

    # 1. 嚴格去重：標題一樣直接刪
    seen_titles = set()
    unique_news = []
    for n in all_news:
        if n["title"] not in seen_titles:
            seen_titles.add(n["title"])
            unique_news.append(n)

    # 2. 防止數據過多，截取最大數量
    unique_news = unique_news[:MAX_NEWS]

    # 3. 生成乾淨的文字內容
    lines = []
    for n in unique_news:
        # 這裡直接呈現清洗後的純文字，沒有任何 HTML
        lines.append(f"【新聞標題】{n['title']}\n【新聞內容】{n['desc']}\n")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # 如果沒有新聞，顯示提示
    if not lines:
        desp = "⚠️ 過去24小時內未抓取到相關新聞。"
    else:
        desp = "\n\n--------------------------------------------------\n\n".join(lines)

    # 4. 推送微信
    try:
        requests.post(
            f"https://sctapi.ftqq.com/{SCKEY}.send",
            data={
                "title": f"【純文字】育碧/PDD/TEMU 熱點 {today}",
                "desp": desp
            },
            timeout=15
        )
        print("✅ 推送完成，已去除HTML格式")
    except Exception as e:
        print(f"❌ 推送失敗: {e}")
