import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

def scrape_website(url: str) -> dict:
    """
    Scrapes a target website's homepage to extract structural and text signals.
    """
    result = {
        "website_title": "",
        "meta_description": "",
        "headings": [],
        "paragraphs_snippet": "",
        "success": False,
        "error": None
    }
    
    # Standardize URL
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Title
        title_tag = soup.find('title')
        if title_tag:
            result["website_title"] = title_tag.get_text().strip()
            
        # 2. Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            result["meta_description"] = meta_desc.get('content', '').strip()
        else:
            # Try og:description
            og_desc = soup.find('meta', attrs={'property': 'og:description'})
            if og_desc:
                result["meta_description"] = og_desc.get('content', '').strip()
                
        # 3. Headings (H1, H2)
        headings = []
        for h in soup.find_all(['h1', 'h2']):
            text = h.get_text().strip()
            if text and len(text) > 5 and len(text) < 100:
                headings.append(text)
        result["headings"] = headings[:8] # Limit to top 8 headings
        
        # 4. Paragraphs snippet (First 1500 chars of body text)
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 20:
                paragraphs.append(text)
        
        body_text = "\n".join(paragraphs)
        result["paragraphs_snippet"] = body_text[:2000]
        result["success"] = True
        
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        
    return result

def query_tavily(query: str) -> dict:
    """
    Optional: Queries Tavily Search API for structured company news/info.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"success": False, "error": "No Tavily API key provided."}
        
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "max_results": 3
    }
    
    try:
        response = requests.post(url, json=payload, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        news_items = []
        for r in data.get("results", []):
            news_items.append({
                "title": r.get("title"),
                "content": r.get("content"),
                "url": r.get("url")
            })
            
        return {
            "success": True,
            "results": news_items
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def enrich_company_data(company_name: str, website: str) -> dict:
    """
    Core entrypoint for company enrichment. Combines local scraping and search APIs.
    """
    enrichment = {
        "website_title": "",
        "scraped_text": "",
        "news": "No news found.",
        "sources": []
    }
    
    # 1. Scrape Website
    scraped = scrape_website(website)
    if scraped["success"]:
        enrichment["website_title"] = scraped["website_title"]
        enrichment["scraped_text"] = f"Title: {scraped['website_title']}\n"
        if scraped["meta_description"]:
            enrichment["scraped_text"] += f"Description: {scraped['meta_description']}\n"
        enrichment["scraped_text"] += f"Headings: {', '.join(scraped['headings'])}\n"
        enrichment["scraped_text"] += f"Content Snippet: {scraped['paragraphs_snippet']}"
        enrichment["sources"].append(website)
    else:
        enrichment["scraped_text"] = f"Scraping failed: {scraped['error']}"
        
    # 2. Check Tavily for news
    news_res = query_tavily(f"{company_name} company news announcements 2025 2026")
    if news_res["success"] and news_res["results"]:
        news_lines = []
        for item in news_res["results"]:
            news_lines.append(f"- {item['title']}: {item['content']} (Source: {item['url']})")
            enrichment["sources"].append(item['url'])
        enrichment["news"] = "\n".join(news_lines)
    else:
        # Fallback news simulation for demo purposes
        enrichment["news"] = f"No live search results available for {company_name}. Scoped to homepage signals."
        
    return enrichment
