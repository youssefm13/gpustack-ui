from tavily import TavilyClient
from config import TAVILY_API_KEY

client = TavilyClient(api_key=TAVILY_API_KEY)

def perform_web_search(query: str):
    response = client.search(query=query, max_results=5)
    
    # Create structured results
    structured_results = {
        "query": query,
        "results": []
    }
    
    for i, result in enumerate(response["results"]):
        structured_results["results"].append({
            "title": result.get('title', 'No title'),
            "url": result.get('url', ''),
            "content": result.get('content', ''),
            "score": result.get('score', 0),
            "published_date": result.get('published_date', ''),
            "index": i + 1
        })
    
    return structured_results

