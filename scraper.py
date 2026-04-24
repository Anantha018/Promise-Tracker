import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from database import get_conn

RSS_SOURCES = {
    "NPR Politics": "https://feeds.npr.org/1014/rss.xml",
    "Washington Post": "https://feeds.washingtonpost.com/rss/politics",
}

POLITICIAN_KEYWORDS = {
    "trump": {
        "Complete the border wall and conduct the largest deportation in US history": ["border wall deportation Trump 2025"],
        "Impose 10-25% tariffs on all imports and 60% tariffs on Chinese goods": ["Trump tariffs China 2025"],
        "Extend the 2017 Tax Cuts and Jobs Act and eliminate taxes on tips": ["Trump tax cuts tips 2025"],
        "Repeal Obamacare and replace with better cheaper healthcare": ["Trump healthcare ACA 2025"],
        "Withdraw from the Paris Climate Agreement again": ["Trump Paris climate 2025"],
        "End the war in Ukraine within 24 hours of taking office": ["Trump Ukraine peace 2025"],
        "Restore energy dominance — drill baby drill": ["Trump energy drilling 2025"],
        "Protect Social Security and Medicare with no cuts": ["Trump Social Security Medicare 2025"],
        "Prosecute political opponents and weaponization of government": ["Trump DOJ prosecution 2025"],
        "Bring back manufacturing jobs and rebuild American cities": ["Trump manufacturing jobs 2025"],
    },
    "wes_moore": {
        "Invest in public education and increase teacher pay": ["Wes Moore education Maryland 2024"],
        "Create 100000 new jobs in clean energy sector": ["Maryland clean energy jobs Moore"],
        "End child poverty in Maryland by 2026": ["Maryland child poverty Moore 2024"],
        "Expand affordable housing across Maryland": ["Maryland affordable housing Moore"],
        "Legalize recreational marijuana and expunge past convictions": ["Maryland marijuana legalization Moore"],
        "Improve public safety and reduce violent crime": ["Maryland crime public safety Moore"],
        "Expand Medicaid and healthcare access for low income Marylanders": ["Maryland Medicaid healthcare Moore"],
        "Invest in infrastructure and broadband in rural Maryland": ["Maryland infrastructure broadband Moore"],
        "Support small businesses and minority owned businesses": ["Maryland small business Moore"],
        "Reform the criminal justice system and reduce incarceration": ["Maryland criminal justice reform Moore"],
    },
    "modi": {
        "Build 20 million affordable houses under PM Awas Yojana": ["PM Awas Yojana houses Modi 2024"],
        "Provide piped water to every household under Jal Jeevan Mission": ["Jal Jeevan Mission water Modi"],
        "Create 1 crore jobs for youth every year": ["Modi jobs youth India 2024"],
        "Double farmer income by 2025": ["Modi farmer income India 2024"],
        "Make India a 5 trillion dollar economy": ["India 5 trillion economy Modi"],
        "Eliminate corruption and black money": ["Modi corruption black money India"],
        "Provide free ration to 80 crore people under PM Garib Kalyan": ["PM Garib Kalyan ration Modi"],
        "Build world class infrastructure with 100 trillion rupee investment": ["India infrastructure Modi 2024"],
        "Make India a global manufacturing hub under Make in India": ["Make in India manufacturing Modi"],
        "Achieve net zero carbon emissions by 2070": ["India net zero carbon Modi 2070"],
    }
}

MODI_RSS = {
    "The Hindu": "https://www.thehindu.com/news/national/feeder/default.rss",
    "NDTV": "https://feeds.feedburner.com/ndtvnews-india-news",
}


def fetch_google_news(query: str, max_results: int = 4) -> list[dict]:
    encoded = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    try:
        r = httpx.get(url, timeout=10, follow_redirects=True)
        root = ET.fromstring(r.text)
        articles = []
        for item in root.findall(".//item")[:max_results]:
            source_el = item.find("source")
            articles.append({
                "title":     item.findtext("title", ""),
                "url":       item.findtext("link", ""),
                "published": item.findtext("pubDate", ""),
                "source":    source_el.text if source_el is not None else "Google News"
            })
        return articles
    except Exception as e:
        print(f"    Google News failed: {e}")
        return []


def fetch_rss_filtered(feed_url: str, source_name: str, keywords: list, max_results: int = 2) -> list[dict]:
    try:
        r = httpx.get(feed_url, timeout=8, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(r.text)
        articles = []
        kw_lower = [k.lower() for k in keywords]
        for item in root.findall(".//item"):
            title = item.findtext("title", "")
            combined = (title + " " + item.findtext("description", "")).lower()
            if any(any(w in combined for w in kw.split()) for kw in kw_lower):
                articles.append({
                    "title": title,
                    "url": item.findtext("link", ""),
                    "published": item.findtext("pubDate", ""),
                    "source": source_name
                })
                if len(articles) >= max_results:
                    break
        return articles
    except Exception as e:
        print(f"    {source_name} failed: {e}")
        return []


def scrape_politician(politician: str, conn):
    keywords_map = POLITICIAN_KEYWORDS.get(politician, {})
    promises = conn.execute(
        "SELECT id, text FROM promises WHERE politician=?", (politician,)
    ).fetchall()

    rss = MODI_RSS if politician == "modi" else RSS_SOURCES

    for promise in promises:
        pid, text = promise["id"], promise["text"]
        keywords = keywords_map.get(text, [text[:40]])
        all_articles = []

        for kw in keywords[:1]:
            all_articles.extend(fetch_google_news(kw, max_results=4))

        flat_kw = [w for kw in keywords for w in kw.split() if len(w) > 4]
        for source_name, feed_url in rss.items():
            all_articles.extend(fetch_rss_filtered(feed_url, source_name, flat_kw))

        seen, unique = set(), []
        for a in all_articles:
            if a["title"] and a["title"] not in seen:
                seen.add(a["title"])
                unique.append(a)

        count = 0
        for article in unique[:8]:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO news_articles (promise_id, title, url, source, published) VALUES (?,?,?,?,?)",
                    (pid, article["title"], article["url"], article["source"], article["published"])
                )
                count += 1
            except: pass

        conn.commit()
        print(f"    [{politician}] {text[:50]}... → {count} articles")


def scrape_all():
    conn = get_conn()
    for politician in ["trump", "wes_moore", "modi"]:
        print(f"\n🔍 Scraping {politician}...")
        scrape_politician(politician, conn)
    conn.close()
    print("\n✅ Done — run verdict.py next")

if __name__ == "__main__":
    scrape_all()