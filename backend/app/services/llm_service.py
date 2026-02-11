import httpx
from typing import List
import json
import re

from app.config import get_settings


async def generate_talk_starters(
    friend_name: str,
    relation_type: str,
    interaction_context: str,
    language: str = "en"
) -> List[str]:
    """Generate conversation starters using LLM."""
    settings = get_settings()
    
    if not settings.llm_proxy_key:
        # Return default starters if no API key
        return [
            "How have you been lately?",
            "What's new in your life?",
            "Any exciting plans coming up?"
        ]
    
    language_prompts = {
        "en": "English",
        "zh": "Chinese (Simplified)",
        "ja": "Japanese",
        "de": "German",
        "fr": "French",
        "ko": "Korean",
        "es": "Spanish"
    }
    
    target_language = language_prompts.get(language, "English")
    
    prompt = f"""You are helping someone with ADHD reconnect with their {relation_type} named {friend_name}.

Based on their previous interactions:
{interaction_context}

Generate 5 natural, warm conversation starters that:
1. Reference previous topics if available
2. Are open-ended to encourage real connection
3. Feel genuine, not forced or awkward
4. Account for the time passed since last contact

Respond in {target_language}.

Format: Return ONLY a JSON array of 5 strings, no other text.
Example: ["How did the project you mentioned go?", "I was thinking about you when...", ...]"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.llm_proxy_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_proxy_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            
            # Parse JSON array from response
            # Try to find JSON array in the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                starters = json.loads(json_match.group())
                return starters[:5]
            else:
                return [content]
                
    except Exception as e:
        print(f"LLM error: {e}")
        return [
            "How have you been?",
            "What's been keeping you busy lately?",
            "I was thinking about our last conversation..."
        ]
