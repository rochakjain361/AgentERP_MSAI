"""AI Service - GitHub Models (Primary/Free) + Azure AI Foundry (Fallback/Paid)."""
import httpx
import json
import logging
from typing import Dict, Any, List

from config import AI_ENDPOINT, AI_MODEL, GITHUB_TOKEN, AZURE_AI_ENDPOINT, AZURE_AI_KEY, AZURE_AI_MODEL


SYSTEM_PROMPT = """You are AgentERP AI assistant. Parse user requests and return JSON.

Actions: check_customer, create_customer, create_sales_order, list_sales_orders, list_invoices, list_customers, dashboard_stats, comprehensive_analytics, general_query

For create_customer: include customer_data with customer_name (required), customer_type (optional, default "Company"), territory (optional, default "India")
For create_sales_order: include customer, items array with item_code and qty

Customers: Grant Plastics Ltd., West View Software Ltd., Palmer Productions Ltd.
Items: SKU001-SKU005

Return JSON only:
{"intent": "action", "customer": "name", "customer_data": {"customer_name": "name"}, "items": [{"item_code": "X", "qty": N}], "natural_response": "brief response"}"""


class AIService:
    """AI Service: GitHub Models (free) first, Azure AI Foundry (paid) as fallback."""
    
    def __init__(self):
        # Primary: GitHub Models (Free)
        self.github_endpoint = AI_ENDPOINT
        self.github_model = AI_MODEL
        self.github_token = GITHUB_TOKEN
        self.github_headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json"
        }
        
        # Fallback: Azure AI Foundry (Paid)
        self.azure_endpoint = AZURE_AI_ENDPOINT
        self.azure_model = AZURE_AI_MODEL
        self.azure_key = AZURE_AI_KEY
        self.azure_headers = {
            "api-key": self.azure_key,
            "Content-Type": "application/json"
        }
        
        self.using_fallback = False
    
    async def _call_ai_api(self, endpoint: str, headers: Dict, payload: Dict, service_name: str, timeout: float = 30.0) -> Dict[str, Any]:
        """Make API call to AI service."""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                
                if response.status_code == 200:
                    return {"status": "success", "data": response.json(), "service": service_name}
                elif response.status_code == 429:
                    logging.warning(f"{service_name} rate limited (429)")
                    return {"status": "rate_limited", "service": service_name}
                else:
                    logging.error(f"{service_name} error: {response.status_code}")
                    return {"status": "error", "message": f"{service_name} error: {response.status_code}"}
        except Exception as e:
            logging.error(f"{service_name} exception: {type(e).__name__}")
            return {"status": "error", "message": str(e)}
    
    async def parse_natural_language(self, user_message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Parse natural language. GitHub Models first (free), Azure fallback (paid)."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        if conversation_history:
            messages.extend(conversation_history[-4:])
        
        messages.append({"role": "user", "content": user_message})
        
        payload = {
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 300
        }
        
        try:
            # Try GitHub Models first (FREE)
            if self.github_token and not self.using_fallback:
                github_payload = {**payload, "model": self.github_model}
                result = await self._call_ai_api(
                    self.github_endpoint, 
                    self.github_headers, 
                    github_payload, 
                    "GitHub Models"
                )
                
                if result["status"] == "success":
                    logging.info("Using GitHub Models (free)")
                    return self._process_ai_response(result["data"])
                elif result["status"] == "rate_limited":
                    logging.warning("GitHub rate limited, switching to Azure (paid)")
                    self.using_fallback = True
            
            # Fallback to Azure AI Foundry (PAID)
            if self.azure_key and self.azure_endpoint:
                azure_payload = {**payload, "model": self.azure_model}
                result = await self._call_ai_api(
                    self.azure_endpoint,
                    self.azure_headers,
                    azure_payload,
                    "Azure AI Foundry",
                    timeout=60.0  # Longer timeout for Azure
                )
                
                if result["status"] == "success":
                    logging.info("Using Azure AI Foundry (paid fallback)")
                    return self._process_ai_response(result["data"])
                else:
                    return {"status": "error", "message": result.get("message", "Azure error")}
            
            return {"status": "error", "message": "No AI service available"}
                
        except Exception as e:
            logging.error(f"AI service error: {type(e).__name__}: {str(e)}")
            return {"status": "error", "message": f"AI error: {str(e)}"}
    
    def _process_ai_response(self, data: Dict) -> Dict[str, Any]:
        """Process AI response and extract intent."""
        try:
            ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            ai_response = ai_response.strip()
            
            # Clean markdown if present
            if ai_response.startswith("```"):
                parts = ai_response.split("```")
                if len(parts) > 1:
                    ai_response = parts[1]
                    if ai_response.startswith("json"):
                        ai_response = ai_response[4:].strip()
            
            parsed = json.loads(ai_response)
            return {"status": "success", "parsed_intent": parsed}
        except json.JSONDecodeError:
            return {
                "status": "success",
                "parsed_intent": {
                    "intent": "general_query",
                    "natural_response": ai_response if ai_response else "I can help you with ERP tasks."
                }
            }


# Singleton instance
ai_service = AIService()
