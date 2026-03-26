"""AI Service - Azure OpenAI GPT-4o Integration."""
import httpx
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List

from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_MODEL,
    AZURE_OPENAI_API_VERSION
)


SYSTEM_PROMPT = """You are AgentERP AI assistant. Parse user requests and return JSON.

Actions: check_customer, create_customer, create_sales_order, list_sales_orders, list_invoices, list_customers, dashboard_stats, comprehensive_analytics, general_query

Items: SKU001-SKU005

Return JSON only:
{"intent": "action", "customer": "name", "items": [{"item_code": "X", "qty": N}], "natural_response": "brief response"}"""


class AIService:
    """AI Service using Azure OpenAI GPT-4o."""
    
    def __init__(self):
        self.endpoint = AZURE_OPENAI_ENDPOINT
        self.api_key = AZURE_OPENAI_API_KEY
        self.model = AZURE_OPENAI_MODEL
        self.api_version = AZURE_OPENAI_API_VERSION
        
        self.chat_url = f"{self.endpoint}/openai/deployments/{self.model}/chat/completions?api-version={self.api_version}"
        
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        logging.info(f"Azure OpenAI initialized: {self.endpoint}, model: {self.model}")
    
    async def _call_azure_openai(self, messages: List[Dict], timeout: float = 60.0) -> Dict[str, Any]:
        """Make API call to Azure OpenAI."""
        payload = {
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                logging.info(f"Calling Azure OpenAI: {self.chat_url}")
                response = await client.post(
                    self.chat_url, 
                    headers=self.headers, 
                    json=payload
                )
                
                if response.status_code == 200:
                    logging.info("Azure OpenAI call successful")
                    return {"status": "success", "data": response.json()}
                elif response.status_code == 429:
                    logging.warning("Azure OpenAI rate limited (429)")
                    return {"status": "rate_limited", "message": "Rate limited, please try again"}
                else:
                    error_text = response.text
                    logging.error(f"Azure OpenAI error {response.status_code}: {error_text}")
                    return {"status": "error", "message": f"Azure OpenAI error: {response.status_code} - {error_text}"}
                    
        except httpx.TimeoutException:
            logging.error("Azure OpenAI timeout")
            return {"status": "error", "message": "Request timed out"}
        except Exception as e:
            logging.error(f"Azure OpenAI exception: {type(e).__name__}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def parse_natural_language(self, user_message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Parse natural language using Azure OpenAI GPT-4o."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history (last 6 messages for context)
        if conversation_history:
            messages.extend(conversation_history[-6:])
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            result = await self._call_azure_openai(messages)
            
            if result["status"] == "success":
                return self._process_ai_response(result["data"])
            else:
                return {"status": "error", "message": result.get("message", "AI service error")}
                
        except Exception as e:
            logging.error(f"AI service error: {type(e).__name__}: {str(e)}")
            return {"status": "error", "message": f"AI error: {str(e)}"}
    
    def _process_ai_response(self, data: Dict) -> Dict[str, Any]:
        """Process AI response and extract intent."""
        try:
            ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            ai_response = ai_response.strip()
            
            # Clean markdown code blocks if present
            if ai_response.startswith("```"):
                parts = ai_response.split("```")
                if len(parts) > 1:
                    ai_response = parts[1]
                    if ai_response.startswith("json"):
                        ai_response = ai_response[4:].strip()
            
            # Try to parse as JSON
            parsed = json.loads(ai_response)
            return {"status": "success", "parsed_intent": parsed}
            
        except json.JSONDecodeError:
            # If not JSON, return as general query with natural response
            return {
                "status": "success",
                "parsed_intent": {
                    "intent": "general_query",
                    "natural_response": ai_response if ai_response else "I can help you with ERP tasks."
                }
            }
    
    async def generate_response(self, prompt: str, context: str = None) -> Dict[str, Any]:
        """Generate a general AI response (not for intent parsing)."""
        messages = []
        
        if context:
            messages.append({"role": "system", "content": context})
        
        messages.append({"role": "user", "content": prompt})
        
        result = await self._call_azure_openai(messages)
        
        if result["status"] == "success":
            content = result["data"].get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"status": "success", "response": content}
        else:
            return result


# Singleton instance
ai_service = AIService()
