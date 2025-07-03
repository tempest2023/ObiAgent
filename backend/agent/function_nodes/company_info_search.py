from pocketflow import Node
from typing import Dict, List, Any, Optional
from agent.utils.stream_llm import call_llm
import logging
import json

logger = logging.getLogger(__name__)

class CompanyInfoSearchNode(Node):
    """
    Node to search for basic company information including founding details,
    business model, location, industry, and key personnel.
    
    Example:
        >>> node = CompanyInfoSearchNode()
        >>> shared = {"company_name": "OpenAI", "search_results": [...]}
        >>> node.prep(shared)
        # Returns (company_name, search_results)
        >>> node.exec(("OpenAI", [...]))
        # Returns structured company information
    """
    
    def prep(self, shared: Dict[str, Any]) -> tuple:
        """Prepare company name and search results for analysis"""
        company_name = shared.get("company_name", "")
        search_results = shared.get("search_results", [])
        
        logger.info(f"🔄 CompanyInfoSearchNode: prep - company='{company_name}', results_count={len(search_results)}")
        
        if not company_name:
            logger.warning("⚠️ CompanyInfoSearchNode: No company name provided")
            
        return company_name, search_results
    
    def exec(self, inputs: tuple) -> Dict[str, Any]:
        """Extract and structure company information from search results"""
        company_name, search_results = inputs
        
        logger.info(f"🔄 CompanyInfoSearchNode: exec - company='{company_name}', results_count={len(search_results)}")
        
        if not search_results:
            logger.warning("⚠️ CompanyInfoSearchNode: No search results to analyze")
            return {
                "company_name": company_name,
                "founding_info": {"year": None, "founders": [], "location": None},
                "business_model": "",
                "industry": "",
                "description": "",
                "key_personnel": [],
                "headquarters": "",
                "employee_count": None,
                "website": "",
                "confidence_score": 0.0
            }
        
        # Format search results for LLM analysis
        formatted_results = []
        for i, result in enumerate(search_results[:10], 1):  # Limit to top 10 results
            formatted_results.append(f"""
Result {i}:
Title: {result.get('title', '')}
Content: {result.get('snippet', '')}
URL: {result.get('link', '')}
""")
        
        prompt = f"""
Analyze the following search results about "{company_name}" and extract structured company information.

{chr(10).join(formatted_results)}

Please extract and structure the following information:

1. Basic Information:
   - Company name
   - Founding year
   - Founders (names)
   - Industry/sector
   - Business description (2-3 sentences)

2. Business Details:
   - Business model (how they make money)
   - Primary products/services
   - Target market

3. Company Details:
   - Headquarters location
   - Website
   - Approximate employee count (if available)
   - Key executives/leadership

Provide a confidence score (0.0-1.0) for the accuracy of the information based on source reliability.

Output in JSON format:
```json
{{
    "company_name": "{company_name}",
    "founding_info": {{
        "year": 2015,
        "founders": ["Founder Name 1", "Founder Name 2"],
        "location": "City, Country"
    }},
    "business_model": "Description of how they make money",
    "industry": "Industry/sector",
    "description": "Brief company description",
    "key_personnel": [
        {{"name": "CEO Name", "role": "CEO"}},
        {{"name": "CTO Name", "role": "CTO"}}
    ],
    "headquarters": "City, Country",
    "employee_count": 1000,
    "website": "https://company.com",
    "products_services": ["Product 1", "Service 1"],
    "target_market": "Description of target market",
    "confidence_score": 0.8
}}
```
"""
        
        try:
            logger.info("🤖 CompanyInfoSearchNode: Calling LLM for company info extraction")
            response = call_llm(prompt)
            
            # Extract JSON from response
            json_str = response.split("```json")[1].split("```")[0].strip()
            company_info = json.loads(json_str)
            
            logger.info("✅ CompanyInfoSearchNode: Successfully parsed company information")
            
            # Validate required fields
            required_fields = ["company_name", "founding_info", "business_model", "industry", "description"]
            for field in required_fields:
                if field not in company_info:
                    company_info[field] = ""
                    
            # Ensure confidence score is between 0 and 1
            confidence = company_info.get("confidence_score", 0.5)
            company_info["confidence_score"] = max(0.0, min(1.0, confidence))
            
            return company_info
            
        except (IndexError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ CompanyInfoSearchNode: Error parsing LLM response: {e}")
            logger.error(f"📄 CompanyInfoSearchNode: Raw response: {response}")
            
            # Return fallback structure
            return {
                "company_name": company_name,
                "founding_info": {"year": None, "founders": [], "location": None},
                "business_model": "Information extraction failed",
                "industry": "Unknown",
                "description": f"Unable to extract detailed information about {company_name}",
                "key_personnel": [],
                "headquarters": "",
                "employee_count": None,
                "website": "",
                "products_services": [],
                "target_market": "",
                "confidence_score": 0.1
            }
        
        except Exception as e:
            logger.error(f"❌ CompanyInfoSearchNode: Unexpected error: {e}")
            raise
    
    def post(self, shared: Dict[str, Any], prep_res: tuple, exec_res: Dict[str, Any]) -> str:
        """Store company information in shared store"""
        logger.info(f"💾 CompanyInfoSearchNode: post - Storing company info for {exec_res.get('company_name', 'Unknown')}")
        
        shared["company_info"] = exec_res
        
        # Also store in a more specific key for downstream nodes
        company_name = exec_res.get("company_name", "unknown")
        shared[f"{company_name.lower().replace(' ', '_')}_info"] = exec_res
        
        logger.info(f"✅ CompanyInfoSearchNode: Stored company info with confidence score: {exec_res.get('confidence_score', 0.0)}")
        
        return "default"