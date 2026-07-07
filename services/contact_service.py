import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Curated simulated contacts for our 10 target companies (Demo fallback mode)
CURATED_CONTACTS = {
    "vercel": {
        "name": "Lee Robinson",
        "role": "VP of Product",
        "email": "demo-contact@example.com",
        "linkedin": "https://www.linkedin.com/in/leerob",
        "confidence": 0.85,
        "simulated": True
    },
    "cursor": {
        "name": "Arvid Lunnemark",
        "role": "Co-Founder",
        "email": "demo-contact@example.com",
        "linkedin": "https://www.linkedin.com/in/arvidlunnemark",
        "confidence": 0.90,
        "simulated": True
    },
    "linear": {
        "name": "Karri Saarinen",
        "role": "CEO & Co-Founder",
        "email": "demo-contact@example.com",
        "linkedin": "https://www.linkedin.com/in/karrisaarinen",
        "confidence": 0.92,
        "simulated": True
    },
    "resend": {
        "name": "Zeno Rocha",
        "role": "Founder & CEO",
        "email": "demo-contact@example.com",
        "linkedin": "https://www.linkedin.com/in/zenorocha",
        "confidence": 0.93,
        "simulated": True
    },
    "supabase": {
        "name": "Paul Copplestone",
        "role": "CEO & Co-Founder",
        "email": "demo-contact@example.com",
        "linkedin": "https://www.linkedin.com/in/paulcopplestone",
        "confidence": 0.91,
        "simulated": True
    },
    "phind": {
        "name": "Michael Tang",
        "role": "Founder & CEO",
        "email": "demo-contact@example.com",
        "linkedin": "https://www.linkedin.com/in/michaeltang-phind",
        "confidence": 0.88,
        "simulated": True
    },
    "perplexity": {
        "name": "Aravind Srinivas",
        "role": "CEO & Co-Founder",
        "email": "demo-contact@example.com",
        "linkedin": "https://www.linkedin.com/in/aravindsrinivas",
        "confidence": 0.94,
        "simulated": True
    },
    "midjourney": {
        "name": "David Holz",
        "role": "Founder & CEO",
        "email": "demo-contact@example.com",
        "linkedin": "https://www.linkedin.com/in/davidholz",
        "confidence": 0.82,
        "simulated": True
    },
    "jasper": {
        "name": "Dave Rogenmoser",
        "role": "Co-Founder",
        "email": "demo-contact@example.com",
        "linkedin": "https://www.linkedin.com/in/daverogenmoser",
        "confidence": 0.86,
        "simulated": True
    },
    "langchain": {
        "name": "Harrison Chase",
        "role": "CEO & Co-Founder",
        "email": "demo-contact@example.com",
        "linkedin": "https://www.linkedin.com/in/harrisonchase",
        "confidence": 0.95,
        "simulated": True
    }
}

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
                    email = person.get("email") or "demo-contact@example.com"
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
            print(f"Apollo API lookup failed: {e}. Falling back to simulation.")
            
    # Curated simulated fallback search
    comp_key = company_name.strip().lower()
    if comp_key in CURATED_CONTACTS:
        return CURATED_CONTACTS[comp_key]
        
    # Default generic mock fallback
    return {
        "name": f"Demo Contact ({company_name} CEO)",
        "role": "Chief Executive Officer",
        "email": "demo-contact@example.com",
        "linkedin": f"https://www.linkedin.com/in/demo-contact-{company_name.lower()}",
        "confidence": 0.50,
        "simulated": True
    }
