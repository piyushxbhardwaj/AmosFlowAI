import os
from services.contact_service import find_decision_maker

def run_contacts_agent(company_name: str, website: str) -> dict:
    """
    Finds the most relevant decision maker contact (CEO, Founder, Head of Growth) for a company.
    """
    print(f"[{company_name}] Finding target contact...")
    contact = find_decision_maker(company_name, website)
    
    # Clearly format or add simulated labels if fallback was used
    if contact.get("simulated"):
        print(f"[{company_name}] Contact discovery falling back to SIMULATED contact.")
    else:
        print(f"[{company_name}] Discovered contact: {contact['name']} ({contact['role']})")
        
    return contact
