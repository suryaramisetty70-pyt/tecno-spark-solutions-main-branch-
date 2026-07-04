import urllib.request
import json
import xml.etree.ElementTree as ET

def fetch_google_news(query):
    # Google News RSS format
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        
        news_list = []
        for item in items[:5]: # Get top 5
            title = item.find('title').text
            link = item.find('link').text
            pubDate = item.find('pubDate').text
            news_list.append({"title": title, "link": link, "date": pubDate})
        return news_list
    except Exception as e:
        return f"Error: {e}"

print("--- AI NEWS (Research & News Agents) ---")
ai_news = fetch_google_news("Artificial Intelligence OR OpenAI OR Gemini")
for i, n in enumerate(ai_news):
    print(f"[{i+1}] {n['title']}")

print("\n--- TRADING NEWS (Trading & News Agents) ---")
trading_news = fetch_google_news("Stock Market OR Crypto OR Bitcoin")
for i, n in enumerate(trading_news):
    print(f"[{i+1+len(ai_news)}] {n['title']}")
