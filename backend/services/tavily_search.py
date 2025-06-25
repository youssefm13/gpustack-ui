from tavily import TavilyClient
from config import TAVILY_API_KEY, GPUSTACK_API_URL, GPUSTACK_API_KEY
import requests
import json
import re

client = TavilyClient(api_key=TAVILY_API_KEY)

def perform_web_search(query: str):
    # Enhance query for better results
    enhanced_query = enhance_search_query(query)
    
    # Enhanced search with better parameters for content quality
    response = client.search(
        query=enhanced_query, 
        max_results=8,  # Get more results to filter from
        include_raw_content=True,  # Get more detailed content
        search_depth="advanced",  # Use advanced search for better results
        exclude_domains=["google.com", "bing.com", "yahoo.com", "facebook.com", "twitter.com"]  # Exclude low-content sites
    )
    
    # Create structured results with enhanced content
    structured_results = {
        "query": query,
        "results": []
    }
    
    for i, result in enumerate(response["results"]):
        # Get more content - try raw_content first, then content
        content = result.get('raw_content', '') or result.get('content', '')
        
        # Filter out low-quality content (navigation pages, etc.)
        if is_low_quality_content(content, result.get('title', '')):
            continue
            
        # Clean and process content
        content = clean_content(content)
        
        # If content is too long, truncate it to ~1500 chars to avoid LLM context issues
        if len(content) > 1500:
            content = content[:1500] + "...[content truncated]"
        
        # Only add results with substantial content
        if len(content.strip()) > 100:  # Minimum content length
            structured_results["results"].append({
                "title": result.get('title', 'No title'),
                "url": result.get('url', ''),
                "content": content,
                "score": result.get('score', 0),
                "published_date": result.get('published_date', ''),
                "index": len(structured_results["results"]) + 1
            })
    
    # Process results through LLM for better context
    try:
        processed_results = process_search_results_with_llm(query, structured_results)
        return processed_results
    except Exception as e:
        print(f"Error processing search results with LLM: {e}")
        # Return original results if LLM processing fails
        return structured_results

def process_search_results_with_llm(query: str, search_results: dict):
    """Process search results through LLM to create better summaries and context."""
    
    # Create a prompt for the LLM to process the search results
    results_text = "\n\n".join([
        f"Title: {result['title']}\nURL: {result['url']}\nContent: {result['content']}"
        for result in search_results['results']
    ])
    
    # Create source links for reference
    source_links = "\n".join([
        f"[{i+1}] {result['title']} - {result['url']}"
        for i, result in enumerate(search_results['results'])
    ])
    
    prompt = f"""You are an expert analyst providing comprehensive insights based on web search results.

User Query: "{query}"

Search Results:
{results_text}

Provide a detailed, comprehensive analysis that includes:
1. A thorough summary of the key information and main findings
2. Important trends, patterns, and insights from the data
3. Specific facts, numbers, dates, and concrete details when available
4. Different perspectives or viewpoints if present
5. Context and implications of the findings
6. Any notable developments or recent changes

IMPORTANT: You MUST end your response with a "Sources:" section listing these exact links:
{source_links}

Write in a clear, informative style that provides substantial value beyond just summarizing. Make it comprehensive and insightful."""
    
    try:
        # Send request to GPUStack
        response = requests.post(
            GPUSTACK_API_URL,
            headers={
                "Authorization": f"Bearer {GPUSTACK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen3",  # Default model
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that summarizes web search results clearly and concisely."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1200,  # Increased for comprehensive summaries with sources
                "temperature": 0.2,  # Lower temperature for more factual responses
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                llm_summary = data['choices'][0]['message']['content']
                
                # Add sources section if not already included
                if 'Sources:' not in llm_summary:
                    llm_summary += f"\n\n---\n\n**Sources:**\n{source_links}"
                
                # Add the LLM-processed summary to the results
                search_results['llm_summary'] = llm_summary
                search_results['processing_status'] = 'success'
            else:
                search_results['processing_status'] = 'no_response'
        else:
            search_results['processing_status'] = 'api_error'
            search_results['processing_error'] = f'HTTP {response.status_code}: {response.text}'
            
    except Exception as e:
        print(f"Error in LLM processing: {e}")
        search_results['processing_status'] = 'error'
        search_results['processing_error'] = str(e)
    
    return search_results

def is_low_quality_content(content: str, title: str) -> bool:
    """Check if content is low quality (navigation, empty, etc.)"""
    if not content or len(content.strip()) < 50:
        return True
    
    # Check for navigation-heavy content
    nav_indicators = [
        "Settings", "Help", "Privacy", "Terms", "About", 
        "Navigation", "Menu", "Search", "Login", "Sign in",
        "Subscribe", "Newsletter", "Follow us", "Social media",
        "Cookie policy", "Advanced search", "Clear"
    ]
    
    # Count navigation indicators
    nav_count = sum(1 for indicator in nav_indicators if indicator.lower() in content.lower())
    
    # If more than 30% of content length is navigation-like or too many nav indicators
    content_words = len(content.split())
    if nav_count > 5 or (content_words < 100 and nav_count > 2):
        return True
    
    # Check for generic page titles
    generic_titles = ["google", "search", "news", "homepage", "home page"]
    if any(generic in title.lower() for generic in generic_titles) and len(content.strip()) < 200:
        return True
    
    return False

def clean_content(content: str) -> str:
    """Clean and improve content quality"""
    if not content:
        return ""
    
    # Remove excessive whitespace and newlines
    content = re.sub(r'\n\s*\n', '\n', content)
    content = re.sub(r'\s+', ' ', content)
    
    # Remove common navigation elements
    nav_patterns = [
        r'\*\s+[A-Za-z\s]+\n',  # Bullet points that are likely nav
        r'\[.*?\]\(.*?\)',       # Markdown links that are often nav
        r'Settings\s*\*.*?\n',   # Settings lines
        r'Help\s*\*.*?\n',      # Help lines
    ]
    
    for pattern in nav_patterns:
        content = re.sub(pattern, '', content)
    
    # Extract meaningful sentences
    sentences = content.split('.')
    meaningful_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        # Keep sentences that are substantial and informative
        if (len(sentence) > 20 and 
            not any(nav_word in sentence.lower() for nav_word in ["click", "menu", "navigation", "settings", "help"])):
            meaningful_sentences.append(sentence)
    
    return '. '.join(meaningful_sentences[:10])  # Limit to 10 meaningful sentences

def enhance_search_query(query: str) -> str:
    """Enhance search query for better results"""
    query = query.strip().lower()
    
    # Add context for news/current events queries
    news_keywords = ['news', 'today', 'latest', 'current', 'recent', 'market', 'stock']
    if any(keyword in query for keyword in news_keywords):
        if 'stock' in query or 'market' in query:
            return f"{query} financial news articles latest"
        else:
            return f"{query} news articles latest updates"
    
    # For general queries, add context for better content
    return f"{query} comprehensive information articles"

