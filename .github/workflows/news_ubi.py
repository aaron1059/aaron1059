import requests
import urllib.parse
from datetime import datetime, timedelta, timezone

# 配置
SCKEY = "SCT334015TjyKtNeAukyNnmDI1jJCcLgqt"
KEYWORDS = ["育碧", "Ubisoft", "UBI", "拼多多", "PDD", "Temu"]
HOURS = 24
MAX_NEWS = 10

# ==============================================
# AI 完整解读（长篇完整文字）
# ==============================================
def ai_full_analysis(title):
    t = title.lower()

    # 育碧类
    if any(w in t for w in ["ubi", "育碧", "ubisoft", "游戏", "发行", "steam", "epic", "玩家"]):
        return (
            "本条新闻属于游戏行业动态，内容大概率涉及育碧新游戏发布、财报表现、"
            "全球发行策略调整、玩家社区反馈或与平台方的合作变动。"
            "从行业角度看，这类信息会直接影响公司短期口碑与长期收入结构，"
            "若涉及重磅作品或战略转向，通常会带来市场预期变化。"
        )

    # 电商 / PDD / Temu
    elif any(w in t for w in ["pdd", "拼多多", "temu", "电商", "海外", "跨境", "用户", "增长"]):
        return (
            "本条属于跨境电商与全球化扩张类新闻，内容多围绕用户规模增长、"
            "区域市场拓展、供应链优化、营销投入或监管政策变化展开。"
            "这类信息直接反映平台竞争力与国际化进度，是判断中长期价值的重要依据。"
        )

    # 财经 / 股价 / 并购
    elif any(w in t for w in ["财报", "业绩", "股价", "收购", "并购", "投资", "重组"]):
        return (
            "本条为重要财经事件，涉及公司财务表现、资本运作或重大资产重组。"
            "这类新闻通常会影响市场情绪与估值判断，属于高关注度信息，"
            "需要重点关注其对业务基本面的实际改变。"
        )

    # 通用
    else:
        return (
            "本条为公司相关重要动态，虽然不属于明显的游戏或电商核心事件，"
            "但仍可能涉及战略、合作、人事或品牌层面变化，"
            "建议结合整体行业环境综合判断其影响。"
        )

# ==============================================
# 只抓 24 小时内新闻，避免旧闻
# ==============================================
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
                link  = item.split("<link>")[1].split("</link>")[0].strip()
                news.append({"title": title, "link": link})
            except:
                continue
    except:
        pass
    return news

# ==============================================
# 主程序
# ==============================================
if __name__ == "__main__":
    all_news = []
    for kw in KEYWORDS:
        all_news.extend(get_google_news(kw))

    # 严格去重
    seen = set()
    unique_news = []
    for n in all_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            unique_news.append(n)

    unique_news = unique_news[:MAX_NEWS]

    # 构建推送内容
    lines = []
    for n in unique_news:
        ai_text = ai_full_analysis(n["title"])
        lines.append(
            f"【新闻】{n['title']}\n\n"
            f"【AI 完整解读】\n{ai_text}\n\n"
            f"🔗 原文链接：{n['link']}\n"
        )

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    desp = "\n" + "="*50 + "\n".join(lines)

    # 推送微信
    requests.post(
        f"https://sctapi.ftqq.com/{SCKEY}.send",
        data={
            "title": f"【AI 完整解读】育碧 / PDD / TEMU 新闻 {today_str}",
            "desp": desp
        },
        timeout=10
    )
