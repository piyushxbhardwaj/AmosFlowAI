import os
import json
import re
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

T = TypeVar('T', bound=BaseModel)

def clean_json_string(text: str) -> str:
    """
    Cleans markdown code blocks (e.g. ```json ... ```) from LLM output.
    """
    text = text.strip()
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        return match.group(1).strip()
    return text

def get_llm():
    """
    Initializes and returns the Chat model based on environment variables.
    """
    gemini_key = os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if gemini_key:
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=gemini_key,
                temperature=0.2
            )
        except Exception as e:
            print(f"Failed to load ChatGoogleGenerativeAI: {e}")
            
    if openai_key:
        try:
            return ChatOpenAI(
                model="gpt-4o-mini",
                openai_api_key=openai_key,
                temperature=0.2
            )
        except Exception as e:
            print(f"Failed to load ChatOpenAI: {e}")
            
    return None

def query_llm_json(system_prompt: str, user_prompt: str, mock_fallback_data: dict) -> dict:
    """
    Queries LLM expecting a JSON string response. Parses and returns a dict.
    Uses exponential backoff for retries. Falls back to mock data if key/model fails.
    """
    llm = get_llm()
    if not llm:
        print("[LLM INFO] No API keys configured. Returning simulated structured output.")
        return mock_fallback_data

    import time
    max_retries = 3
    delay = 1.0  # seconds

    for attempt in range(max_retries):
        try:
            messages = [
                SystemMessage(content=system_prompt + "\nIMPORTANT: You must respond ONLY with a raw JSON object. Do not include markdown code block formatting (```json) or conversational text around the JSON."),
                HumanMessage(content=user_prompt)
            ]
            response = llm.invoke(messages)
            raw_content = response.content.strip()
            
            cleaned_content = clean_json_string(raw_content)
            parsed_data = json.loads(cleaned_content)
            return parsed_data
            
        except json.JSONDecodeError as je:
            print(f"[LLM WARNING] Attempt {attempt+1}: Failed to parse JSON from LLM: {je}")
            # Try to extract JSON using regex
            try:
                # Find first '{' and last '}'
                start = raw_content.find('{')
                end = raw_content.rfind('}')
                if start != -1 and end != -1:
                    json_str = raw_content[start:end+1]
                    return json.loads(json_str)
            except Exception:
                pass
        except Exception as e:
            print(f"[LLM WARNING] Attempt {attempt+1}: LLM query error: {e}")
            
        # Exponential backoff
        time.sleep(delay)
        delay *= 2

    print(f"[LLM ERROR] All {max_retries} attempts failed. Falling back to mock data.")
    return mock_fallback_data
