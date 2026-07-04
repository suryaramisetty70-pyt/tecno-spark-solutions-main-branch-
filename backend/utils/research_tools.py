from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 3) -> list:
    """
    Performs a live web search using DuckDuckGo to allow agents to research current data.
    """
    print(f"[Research Sector]: Scanning the internet for: '{query}'...")
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r.get("title"),
                "snippet": r.get("body"),
                "url": r.get("href")
            })
            
        return formatted_results
    except Exception as e:
        print(f"[Research Sector]: Search Error - {str(e)}")
        return []
