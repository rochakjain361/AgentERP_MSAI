"""
Agent Intelligence Service - Uses Azure AI Foundry Agent for real AI-powered analysis.

This service provides:
1. Real AI analysis of ERP data (not dummy data)
2. Intelligent recommendations based on business context
3. Risk assessment and opportunity detection
4. Comprehensive manager intelligence dashboard data
"""
import os
import httpx
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging

from services.erp_service import erp_service
from services.erp_entity_service import erp_entity_service

logger = logging.getLogger(__name__)

# Azure AI Foundry Agent configuration
AZURE_AGENT_ENDPOINT = os.environ.get("AZURE_AGENT_ENDPOINT") or os.environ.get("AZURE_AI_AGENT_RESPONSES_ENDPOINT")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_AGENT_API_VERSION = os.environ.get("AZURE_AGENT_API_VERSION", "2025-11-15-preview")

# Fallback to regular Azure OpenAI if agent endpoint not available
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_MODEL = os.environ.get("AZURE_OPENAI_MODEL", "gpt-4o")


class AgentIntelligenceService:
    """Service for AI-powered business intelligence using Azure AI Foundry Agent."""
    
    def __init__(self):
        self.use_agent = bool(AZURE_AGENT_ENDPOINT)
        logger.info(f"Agent Intelligence Service initialized. Using Agent: {self.use_agent}")
    
    async def _call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """Call AI (Agent or fallback to OpenAI) for analysis."""
        try:
            if self.use_agent and AZURE_AGENT_ENDPOINT:
                # Use Azure AI Foundry Agent
                return await self._call_agent(system_prompt, user_prompt)
            else:
                # Fallback to Azure OpenAI
                return await self._call_openai(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"AI call failed: {str(e)}")
            return f"AI analysis unavailable: {str(e)}"
    
    async def _call_agent(self, system_prompt: str, user_prompt: str) -> str:
        """Call Azure AI Foundry Agent."""
        try:
            # Build URL - endpoint may already include api-version
            url = AZURE_AGENT_ENDPOINT
            if "api-version" not in url:
                url = f"{url}?api-version={AZURE_AGENT_API_VERSION}"
            
            headers = {
                "Content-Type": "application/json",
                "api-key": AZURE_OPENAI_API_KEY,
                "User-Agent": "AgentERP/2.0"
            }
            
            # Azure AI Foundry Agent expects messages format similar to OpenAI
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            logger.info(f"Calling Azure AI Foundry Agent at {url[:80]}...")
            
            async with httpx.AsyncClient(timeout=90.0, verify=False) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                logger.info(f"Agent response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle Azure AI Foundry Agent response format (messages)
                    if "output" in data and isinstance(data["output"], list):
                        for item in data["output"]:
                            if isinstance(item, dict) and "content" in item:
                                for content in item.get("content", []):
                                    if isinstance(content, dict) and content.get("type") == "text":
                                        return content.get("text", "")
                    
                    # Handle OpenAI-format response (messages/choices)
                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if "message" in choice:
                            return choice["message"].get("content", "")
                    
                    # Fallback: return any text-like content
                    if "result" in data:
                        return str(data["result"])
                    
                    logger.warning(f"Unexpected agent response format: {str(data)[:200]}")
                    return str(data)
                    
                else:
                    logger.warning(f"Agent returned {response.status_code}: {response.text[:200]}")
                    logger.info("Falling back to Azure OpenAI...")
                    return await self._call_openai(system_prompt, user_prompt)
                    
        except Exception as e:
            logger.error(f"Agent call failed: {str(e)}, falling back to OpenAI")
            return await self._call_openai(system_prompt, user_prompt)
    
    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call Azure OpenAI as fallback."""
        try:
            url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_MODEL}/chat/completions?api-version=2024-10-21"
            
            headers = {
                "Content-Type": "application/json",
                "api-key": AZURE_OPENAI_API_KEY
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenAI returned {response.status_code}: {response.text}")
                    return "AI analysis temporarily unavailable"
                    
        except Exception as e:
            logger.error(f"OpenAI call failed: {str(e)}")
            return f"AI analysis error: {str(e)}"
    
    async def get_manager_intelligence(self, company_filter: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive AI-powered intelligence report for managers.
        
        This is the main entry point for the Manager Intelligence Dashboard.
        Uses real ERP data + AI analysis.
        """
        try:
            # 1. Gather real ERP data
            erp_data = await self._gather_erp_data(company_filter)
            
            # 2. Generate AI analysis
            ai_analysis = await self._generate_ai_analysis(erp_data, company_filter)
            
            # 3. Structure the response
            return {
                "status": "success",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "company": company_filter,
                "ai_powered": True,
                "using_agent": self.use_agent,
                
                # ERP Data Summary
                "data_summary": erp_data,
                
                # AI Analysis
                "ai_analysis": ai_analysis,
                
                # Metrics
                "metrics": {
                    "data_points_analyzed": erp_data.get("total_records", 0),
                    "ai_model": "Azure AI Foundry Agent" if self.use_agent else "Azure OpenAI GPT-4o",
                    "analysis_depth": "comprehensive"
                }
            }
            
        except Exception as e:
            logger.error(f"Manager intelligence error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _gather_erp_data(self, company_filter: str = None) -> Dict[str, Any]:
        """Gather real data from ERPNext for analysis."""
        data = {
            "total_records": 0,
            "sales_orders": [],
            "invoices": [],
            "customers": [],
            "summary": {}
        }
        
        try:
            # Get sales orders
            orders_result = await erp_entity_service.query(
                doctype="Sales Order",
                filters=[],
                fields=["name", "customer", "grand_total", "status", "transaction_date"],
                limit=50,
                company_filter=company_filter
            )
            if orders_result["status"] == "success":
                data["sales_orders"] = orders_result.get("data", [])
                data["total_records"] += len(data["sales_orders"])
            
            # Get invoices
            invoices_result = await erp_entity_service.query(
                doctype="Sales Invoice",
                filters=[],
                fields=["name", "customer", "grand_total", "outstanding_amount", "status", "due_date", "posting_date"],
                limit=50,
                company_filter=company_filter
            )
            if invoices_result["status"] == "success":
                data["invoices"] = invoices_result.get("data", [])
                data["total_records"] += len(data["invoices"])
            
            # Get customers
            customers_result = await erp_entity_service.query(
                doctype="Customer",
                filters=[],
                fields=["name", "customer_name", "customer_group", "territory"],
                limit=50,
                company_filter=company_filter
            )
            if customers_result["status"] == "success":
                data["customers"] = customers_result.get("data", [])
                data["total_records"] += len(data["customers"])
            
            # Calculate summary stats
            total_order_value = sum(o.get("grand_total", 0) for o in data["sales_orders"])
            total_outstanding = sum(i.get("outstanding_amount", 0) for i in data["invoices"])
            draft_orders = len([o for o in data["sales_orders"] if o.get("status") == "Draft"])
            
            data["summary"] = {
                "total_orders": len(data["sales_orders"]),
                "total_order_value": total_order_value,
                "total_invoices": len(data["invoices"]),
                "total_outstanding": total_outstanding,
                "total_customers": len(data["customers"]),
                "draft_orders": draft_orders,
                "overdue_invoices": len([i for i in data["invoices"] if i.get("outstanding_amount", 0) > 0])
            }
            
        except Exception as e:
            logger.error(f"ERP data gathering error: {str(e)}")
        
        return data
    
    async def _generate_ai_analysis(self, erp_data: Dict, company_filter: str = None) -> Dict[str, Any]:
        """Generate AI-powered analysis of ERP data."""
        
        # Prepare data summary for AI
        summary = erp_data.get("summary", {})
        orders = erp_data.get("sales_orders", [])[:10]  # Top 10 for context
        invoices = erp_data.get("invoices", [])[:10]
        
        system_prompt = """You are an expert ERP business analyst AI agent. Analyze the provided business data and give actionable insights.

Your analysis should be structured as JSON with these sections:
1. "executive_summary": A 2-3 sentence overview of business health
2. "key_findings": Array of 3-5 important observations (each with "finding", "impact", "severity")
3. "risks": Array of identified risks (each with "risk", "probability", "mitigation")
4. "opportunities": Array of growth opportunities (each with "opportunity", "potential_value", "action")
5. "recommendations": Array of 3-5 prioritized actions (each with "priority", "action", "expected_outcome")
6. "health_score": Number 1-100 representing overall business health

Be specific with numbers and actionable with recommendations. Focus on what a manager needs to know."""

        data_context = f"""
Company: {company_filter or 'All Companies'}

BUSINESS DATA SUMMARY:
- Total Sales Orders: {summary.get('total_orders', 0)}
- Total Order Value: ₹{summary.get('total_order_value', 0):,.2f}
- Draft Orders Pending: {summary.get('draft_orders', 0)}
- Total Invoices: {summary.get('total_invoices', 0)}
- Outstanding Amount: ₹{summary.get('total_outstanding', 0):,.2f}
- Overdue Invoices: {summary.get('overdue_invoices', 0)}
- Total Customers: {summary.get('total_customers', 0)}

RECENT ORDERS (sample):
{json.dumps(orders[:5], indent=2, default=str)}

RECENT INVOICES (sample):
{json.dumps(invoices[:5], indent=2, default=str)}

Analyze this data and provide your structured assessment."""

        # Call AI for analysis
        ai_response = await self._call_ai(system_prompt, data_context)
        
        # Parse AI response - handle various formats including Azure AI Foundry Agent
        return self._parse_ai_response(ai_response)
    
    def _parse_ai_response(self, ai_response) -> Dict[str, Any]:
        """Parse AI response handling various formats."""
        try:
            # Handle list response (from Azure AI Foundry Agent)
            if isinstance(ai_response, list):
                for item in ai_response:
                    if isinstance(item, dict) and "content" in item:
                        for content in item.get("content", []):
                            if content.get("type") == "output_text":
                                text = content.get("text", "")
                                return self._extract_json_from_text(text)
            
            # Handle string response
            if isinstance(ai_response, str):
                return self._extract_json_from_text(ai_response)
            
            # Handle dict response
            if isinstance(ai_response, dict):
                # Check if it's already parsed
                if "executive_summary" in ai_response:
                    return ai_response
                # Check for nested output
                if "output_text" in ai_response:
                    return self._extract_json_from_text(ai_response["output_text"])
                if "output" in ai_response:
                    return self._extract_json_from_text(str(ai_response["output"]))
            
            return {
                "executive_summary": "Analysis completed",
                "key_findings": [],
                "risks": [],
                "opportunities": [],
                "recommendations": [],
                "health_score": 70,
                "raw_analysis": str(ai_response)[:1000]
            }
            
        except Exception as e:
            logger.error(f"Parse error: {str(e)}")
            return {
                "executive_summary": "Analysis pending",
                "key_findings": [],
                "risks": [],
                "opportunities": [],
                "recommendations": [],
                "health_score": 70
            }
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text that may contain markdown code blocks."""
        try:
            # Try to extract JSON from markdown code block
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            
            # Try to extract JSON from regular code block
            if "```" in text:
                parts = text.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("{"):
                        try:
                            return json.loads(part)
                        except:
                            pass
            
            # Try to find JSON object in text
            if "{" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                if end > start:
                    return json.loads(text[start:end])
            
            # Return as raw analysis
            return {
                "executive_summary": text[:500] if text else "No analysis available",
                "key_findings": [],
                "risks": [],
                "opportunities": [],
                "recommendations": [],
                "health_score": 70,
                "raw_analysis": text
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {e}")
            return {
                "executive_summary": text[:500] if text else "Analysis format error",
                "key_findings": [],
                "risks": [],
                "opportunities": [],
                "recommendations": [],
                "health_score": 70
            }
    
    async def analyze_specific_situation(
        self, 
        situation_type: str, 
        context_data: Dict,
        company_filter: str = None
    ) -> Dict[str, Any]:
        """
        Use AI to analyze a specific business situation and recommend actions.
        
        This powers the "AI Priorities" reasoning panel with real AI insights.
        """
        system_prompt = """You are an expert ERP consultant AI. Analyze the specific business situation and provide:

1. "situation_assessment": Clear description of the situation
2. "severity": "critical", "high", "medium", or "low"
3. "root_cause_analysis": What's causing this situation
4. "recommended_actions": Array of specific actions to take (each with "action", "urgency", "expected_impact")
5. "business_impact": Financial/operational impact if not addressed
6. "success_metrics": How to measure if the intervention worked

Respond in JSON format. Be specific and actionable."""

        user_prompt = f"""
Situation Type: {situation_type}
Company: {company_filter or 'All'}

Context Data:
{json.dumps(context_data, indent=2, default=str)}

Analyze this situation and provide your expert assessment."""

        ai_response = await self._call_ai(system_prompt, user_prompt)
        
        try:
            if "```json" in ai_response:
                json_str = ai_response.split("```json")[1].split("```")[0]
                return json.loads(json_str)
            elif "{" in ai_response:
                start = ai_response.find("{")
                end = ai_response.rfind("}") + 1
                return json.loads(ai_response[start:end])
            else:
                return {"raw_analysis": ai_response}
        except Exception:
            return {"raw_analysis": ai_response}


# Singleton instance
agent_intelligence = AgentIntelligenceService()
