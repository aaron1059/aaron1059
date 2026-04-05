import requests
import urllib.parse
from datetime import datetime, timedelta, timezone
import re

# 配置
SCKEY = "SCT334015TjyKtNeAukyNnmDI1jJCcLgqt"
KEYWORDS = ["育碧", "Ubisoft", "UBI", "拼多多", "PDD", "Temu"]
HOURS = 24
MAX_NEWS = 8

# ==============================================
# 终极HTML清洗函数：多层暴力清除所有标签和转义
# ==============================================
def clean_html(raw_html):
    # 1. 先处理所有HTML实体（&nbsp; &gt; 等）
    clean_text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', raw_html)
    # 2. 清除所有<a>标签（包含href属性）
    clean_text = re.sub(r'<a\s+[^>]*>', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'</a>', '', clean_text, flags=re.IGNORECASE)
    # 3. 清除所有<font>标签
    clean_text = re.sub(r'<font\s+[^>]*>', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'</font>', '', clean_text, flags=re.IGNORECASE)
    # 4. 清除所有其他HTML标签（通用匹配）
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    # 5. 清除多余的空格、换行
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text

# ==============================================
# 标题清洗：去除末尾的 "- 来源域名"
# ==============================================
def clean_title(raw_title):
    # 匹配末尾的 "- xxx.com" 格式并删除
    clean_title = re.sub(r'\s*-\s*[\w\.]+\.com\s*$', '', raw_title)
    return clean_title.strip()

# ==============================================
# 获取24小时内Google新闻
# ==============================================
def get_google_news(keyword):
    news = []
    now = datetime.now(timezone.utc)
    since_str = (now - timedelta(hours=HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=zh-CN&gl=CN&since={since_str}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        items = r.text.split("<item>")
        
        for item in items[1:]:
            try:
                # 提取并清洗标题
                raw_title = item.split("<title>")[1].split("</title>")[0].strip()
                clean_title_text = clean_title(raw_title)
                
                # 提取并清洗描述
                raw_desc = item.split("<description>")[1].split("</description>")[0].strip()
                clean_desc_text = clean_html(raw_desc)
                
                # 过滤无效内容
                if len(clean_title_text) > 10 and len(clean_desc_text) > 20:
                    news.append({
                        "title": clean_title_text,
                        "desc": clean_desc_text
                    })
            except Exception:
                continue
    except Exception:
        pass
    return news

# ==============================================
# 主程序
# ==============================================
if __name__ == "__main__":
    all_news = []
    for kw in KEYWORDS:
        all_news.extend(get_google_news(kw))

    # 1. 严格去重：标题完全一致则过滤
    seen_titles = set()
    unique_news = []
    for n in all_news:
        if n["title"] not in seen_titles:
            seen_titles.add(n["title"])
            unique_news.append(n)

    # 2. 限制最大条数
    unique_news = unique_news[:MAX_NEWS]

    # 3. 生成推送内容
    lines = []
    for n in unique_news:
        lines.append(f"【新闻标题】{n['title']}\n【新闻内容】{n['desc']}\n")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    desp = "\n\n--------------------------------------------------\n\n".join(lines) if lines else "⚠️ 过去24小时无相关新闻"

    # 4. 推送微信
    try:
        requests.post(
            f"https://sctapi.ftqq.com/{SCKEY}.send",
            data={
                "title": f"【纯文字无码】育碧/PDD/TEMU 新闻 {today}",
                "desp": desp
            },
            timeout=15
        )
        print("✅ 推送成功，已完成HTML全清洗+去重")
    except Exception as e:
        print(f"❌ 推送失败: {str(e)}")
