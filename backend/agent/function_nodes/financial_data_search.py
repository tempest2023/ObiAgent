from pocketflow import Node
from typing import Dict, List, Any, Optional
from agent.utils.stream_llm import call_llm
import logging
import json
import re

logger = logging.getLogger(__name__)

class FinancialDataSearchNode(Node):
    """
    Node to search for and extract financial data including revenue, funding rounds,
    valuation, market cap, and other financial metrics.
    
    Example:
        >>> node = FinancialDataSearchNode()
        >>> shared = {"company_name": "OpenAI", "search_results": [...]}
        >>> node.prep(shared)
        # Returns (company_name, search_results)
        >>> node.exec(("OpenAI", [...]))
        # Returns structured financial data
    """
    
    def prep(self, shared: Dict[str, Any]) -> tuple:
        """Prepare company name and search results for financial analysis"""
        company_name = shared.get("company_name", "")
        search_results = shared.get("search_results", [])
        company_info = shared.get("company_info", {})
        
        logger.info(f"🔄 FinancialDataSearchNode: prep - company='{company_name}', results_count={len(search_results)}")
        
        if not company_name:
            logger.warning("⚠️ FinancialDataSearchNode: No company name provided")
            
        return company_name, search_results, company_info
    
    def exec(self, inputs: tuple) -> Dict[str, Any]:
        """Extract and structure financial data from search results"""
        company_name, search_results, company_info = inputs
        
        logger.info(f"🔄 FinancialDataSearchNode: exec - company='{company_name}', results_count={len(search_results)}")
        
        if not search_results:
            logger.warning("⚠️ FinancialDataSearchNode: No search results to analyze")
            return self._get_empty_financial_data(company_name)
        
        # Format search results for LLM analysis
        formatted_results = []
        for i, result in enumerate(search_results[:15], 1):  # More results for financial data
            formatted_results.append(f"""
Result {i}:
Title: {result.get('title', '')}
Content: {result.get('snippet', '')}
URL: {result.get('link', '')}
""")
        
        # Include company context if available
        company_context = ""
        if company_info:
            company_context = f"""
Company Context:
- Industry: {company_info.get('industry', 'Unknown')}
- Founded: {company_info.get('founding_info', {}).get('year', 'Unknown')}
- Business Model: {company_info.get('business_model', 'Unknown')}
"""
        
        prompt = f"""
Analyze the following search results about "{company_name}" and extract financial information.

{company_context}

{chr(10).join(formatted_results)}

Please extract and structure the following financial information:

1. Revenue Information:
   - Annual revenue (latest available year)
   - Revenue growth rate
   - Revenue sources/breakdown
   - Revenue trends

2. Funding and Investment:
   - Total funding raised
   - Latest funding round (amount, date, type)
   - Key investors
   - Funding history (major rounds)

3. Valuation:
   - Current valuation
   - Market cap (if public)
   - Valuation history

4. Financial Metrics:
   - Profitability status
   - EBITDA (if available)
   - Burn rate (if mentioned)
   - Financial ratios

5. Stock Information (if public):
   - Stock symbol
   - Stock price
   - Market performance

Provide confidence scores (0.0-1.0) for each category and an overall confidence score.
Use "Not Available" for missing information and include the data source year when possible.

Output in JSON format:
```json
{{
    "company_name": "{company_name}",
    "financial_year": "2024",
    "revenue": {{
        "annual_revenue": {{
            "amount": 1000000000,
            "currency": "USD",
            "year": 2023,
            "confidence": 0.8
        }},
        "revenue_growth": {{
            "rate": 25.5,
            "period": "year-over-year",
            "confidence": 0.7
        }},
        "revenue_sources": ["Product sales", "Subscriptions"],
        "confidence_score": 0.8
    }},
    "funding": {{
        "total_funding": {{
            "amount": 100000000,
            "currency": "USD",
            "confidence": 0.9
        }},
        "latest_round": {{
            "amount": 50000000,
            "type": "Series B",
            "date": "2023-12",
            "lead_investor": "Investor Name",
            "confidence": 0.8
        }},
        "funding_history": [
            {{"round": "Series A", "amount": 10000000, "date": "2022-01"}},
            {{"round": "Series B", "amount": 50000000, "date": "2023-12"}}
        ],
        "confidence_score": 0.8
    }},
    "valuation": {{
        "current_valuation": {{
            "amount": 1000000000,
            "currency": "USD",
            "date": "2023-12",
            "confidence": 0.7
        }},
        "market_cap": {{
            "amount": "Not Available",
            "currency": "USD",
            "confidence": 0.0
        }},
        "confidence_score": 0.7
    }},
    "financial_metrics": {{
        "profitability": {{
            "status": "Profitable/Loss-making/Break-even",
            "details": "Additional details",
            "confidence": 0.6
        }},
        "ebitda": {{
            "amount": "Not Available",
            "currency": "USD",
            "year": 2023,
            "confidence": 0.0
        }},
        "burn_rate": {{
            "monthly_burn": "Not Available",
            "runway_months": "Not Available",
            "confidence": 0.0
        }},
        "confidence_score": 0.6
    }},
    "stock_info": {{
        "is_public": false,
        "stock_symbol": "Not Available",
        "stock_price": "Not Available",
        "confidence_score": 1.0
    }},
    "data_sources": ["Source 1", "Source 2"],
    "overall_confidence": 0.7,
    "last_updated": "2024-01-01"
}}
```
"""
        
        try:
            logger.info("🤖 FinancialDataSearchNode: Calling LLM for financial data extraction")
            response = call_llm(prompt)
            
            # Extract JSON from response
            json_str = response.split("```json")[1].split("```")[0].strip()
            financial_data = json.loads(json_str)
            
            logger.info("✅ FinancialDataSearchNode: Successfully parsed financial data")
            
            # Validate and clean the data
            financial_data = self._validate_financial_data(financial_data, company_name)
            
            return financial_data
            
        except (IndexError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ FinancialDataSearchNode: Error parsing LLM response: {e}")
            logger.error(f"📄 FinancialDataSearchNode: Raw response: {response}")
            
            # Return fallback structure
            return self._get_empty_financial_data(company_name)
        
        except Exception as e:
            logger.error(f"❌ FinancialDataSearchNode: Unexpected error: {e}")
            raise
    
    def _get_empty_financial_data(self, company_name: str) -> Dict[str, Any]:
        """Return empty financial data structure"""
        return {
            "company_name": company_name,
            "financial_year": "2024",
            "revenue": {
                "annual_revenue": {"amount": "Not Available", "currency": "USD", "year": None, "confidence": 0.0},
                "revenue_growth": {"rate": "Not Available", "period": "year-over-year", "confidence": 0.0},
                "revenue_sources": [],
                "confidence_score": 0.0
            },
            "funding": {
                "total_funding": {"amount": "Not Available", "currency": "USD", "confidence": 0.0},
                "latest_round": {"amount": "Not Available", "type": "Unknown", "date": None, "lead_investor": "Unknown", "confidence": 0.0},
                "funding_history": [],
                "confidence_score": 0.0
            },
            "valuation": {
                "current_valuation": {"amount": "Not Available", "currency": "USD", "date": None, "confidence": 0.0},
                "market_cap": {"amount": "Not Available", "currency": "USD", "confidence": 0.0},
                "confidence_score": 0.0
            },
            "financial_metrics": {
                "profitability": {"status": "Unknown", "details": "No data available", "confidence": 0.0},
                "ebitda": {"amount": "Not Available", "currency": "USD", "year": None, "confidence": 0.0},
                "burn_rate": {"monthly_burn": "Not Available", "runway_months": "Not Available", "confidence": 0.0},
                "confidence_score": 0.0
            },
            "stock_info": {
                "is_public": False,
                "stock_symbol": "Not Available",
                "stock_price": "Not Available",
                "confidence_score": 0.0
            },
            "data_sources": [],
            "overall_confidence": 0.0,
            "last_updated": "2024-01-01"
        }
    
    def _validate_financial_data(self, data: Dict[str, Any], company_name: str) -> Dict[str, Any]:
        """Validate and clean financial data"""
        # Ensure company name is correct
        data["company_name"] = company_name
        
        # Validate confidence scores
        def validate_confidence(obj, key="confidence_score"):
            if key in obj:
                obj[key] = max(0.0, min(1.0, obj[key]))
        
        # Validate main sections
        for section in ["revenue", "funding", "valuation", "financial_metrics", "stock_info"]:
            if section not in data:
                data[section] = {}
            validate_confidence(data[section])
        
        # Validate overall confidence
        validate_confidence(data, "overall_confidence")
        
        # Ensure required nested structures exist
        required_structures = {
            "revenue": ["annual_revenue", "revenue_growth"],
            "funding": ["total_funding", "latest_round"],
            "valuation": ["current_valuation", "market_cap"],
            "financial_metrics": ["profitability"],
            "stock_info": ["is_public"]
        }
        
        for section, required_keys in required_structures.items():
            for key in required_keys:
                if key not in data[section]:
                    data[section][key] = {"confidence": 0.0}
        
        return data
    
    def post(self, shared: Dict[str, Any], prep_res: tuple, exec_res: Dict[str, Any]) -> str:
        """Store financial data in shared store"""
        logger.info(f"💾 FinancialDataSearchNode: post - Storing financial data for {exec_res.get('company_name', 'Unknown')}")
        
        shared["financial_data"] = exec_res
        
        # Also store in a more specific key for downstream nodes
        company_name = exec_res.get("company_name", "unknown")
        shared[f"{company_name.lower().replace(' ', '_')}_financial_data"] = exec_res
        
        # Extract key metrics for easy access
        shared["key_financial_metrics"] = {
            "revenue": exec_res.get("revenue", {}).get("annual_revenue", {}).get("amount", "Not Available"),
            "valuation": exec_res.get("valuation", {}).get("current_valuation", {}).get("amount", "Not Available"),
            "funding": exec_res.get("funding", {}).get("total_funding", {}).get("amount", "Not Available"),
            "profitability": exec_res.get("financial_metrics", {}).get("profitability", {}).get("status", "Unknown")
        }
        
        logger.info(f"✅ FinancialDataSearchNode: Stored financial data with confidence score: {exec_res.get('overall_confidence', 0.0)}")
        
        return "default"