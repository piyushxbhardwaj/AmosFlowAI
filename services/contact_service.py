import os
import requests
from dotenv import load_dotenv

load_dotenv()

def find_decision_maker(company_name: str, website: str) -> dict:
    """
    Finds a decision maker (CEO, Founder, Head of Growth, Marketing Lead) for the target company.
    Queries Apollo API if APOLLO_API_KEY is present; otherwise falls back to a simulated contact.
    """
    apollo_key = os.getenv("APOLLO_API_KEY")
    domain = website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    
    if apollo_key:
        url = "https://api.apollo.io/v1/people/match"
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        # Look for typical decision maker roles
        payload = {
            "api_key": apollo_key,
            "reveal_personal_emails": True,
            "domain": domain,
            "titles": ["founder", "ceo", "head of growth", "marketing lead", "chief executive officer"]
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=8)
            if response.status_code == 200:
                data = response.json()
                person = data.get("person", {})
                if person:
                    name = person.get("name", "Demo Contact (CEO)")
                    role = person.get("title", "Chief Executive Officer")
                    email = person.get("email") or f"demo-contact@example.com"
                    linkedin = person.get("linkedin_url") or "https://www.linkedin.com/company/demo-contact"
                    
                    return {
                        "name": name,
                        "role": role,
                        "email": email,
                        "linkedin": linkedin,
                        "confidence": 0.90,
                        "simulated": False
                    }
        except Exception as e:
            # Log error and fall back
            print(f"Apollo API lookup failed: {e}. Falling back to simulation.")
            
    # Mock fallback (clearly labeled as Simulated Contact)
    # Customize roles based on company profile for realistic simulation, but keep it neutral
    return {
        "name": f"Demo Contact ({company_name} CEO)",
        "role": "Chief Executive Officer",
        "email": "demo-contact@example.com",
        "linkedin": f"https://www.linkedin.com/in/demo-contact-{company_name.lower()}",
        "confidence": 0.50,
        "simulated": True
    }
