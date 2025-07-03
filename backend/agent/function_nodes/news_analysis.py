from pocketflow import Node
from typing import Dict, List, Any, Optional
from agent.utils.stream_llm import call_llm
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NewsAnalysisNode(Node):
    """
    Node to analyze recent news and developments for financial impact,
    sentiment analysis, and relevance to financial reporting.
    
    Example:
        >>> node = NewsAnalysisNode()
        >>> shared = {"company_name": "OpenAI", "search_results": [...]}
        >>> node.prep(shared)
        # Returns (company_name, search_results, timeframe)
        >>> node.exec(("OpenAI", [...], "6 months"))
        # Returns structured news analysis
    """
    
    def prep(self, shared: Dict[str, Any]) -> tuple:
        """Prepare company name, news results, and analysis timeframe"""
        company_name = shared.get("company_name", "")
        search_results = shared.get("search_results", [])
        timeframe = shared.get("news_timeframe", "12 months")
        company_info = shared.get("company_info", {})
        
        logger.info(f"🔄 NewsAnalysisNode: prep - company='{company_name}', results_count={len(search_results)}, timeframe='{timeframe}'")
        
        if not company_name:
            logger.warning("⚠️ NewsAnalysisNode: No company name provided")
            
        return company_name, search_results, timeframe, company_info
    
    def exec(self, inputs: tuple) -> Dict[str, Any]:
        """Analyze news results for financial impact and trends"""
        company_name, search_results, timeframe, company_info = inputs
        
        logger.info(f"🔄 NewsAnalysisNode: exec - company='{company_name}', results_count={len(search_results)}")
        
        if not search_results:
            logger.warning("⚠️ NewsAnalysisNode: No search results to analyze")
            return self._get_empty_news_analysis(company_name)
        
        # Format search results for LLM analysis
        formatted_results = []
        for i, result in enumerate(search_results[:20], 1):  # More results for comprehensive news analysis
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
- Business Model: {company_info.get('business_model', 'Unknown')}
- Key Products/Services: {', '.join(company_info.get('products_services', []))}
"""
        
        prompt = f"""
Analyze the following news and search results about "{company_name}" for financial impact and trends over the past {timeframe}.

{company_context}

{chr(10).join(formatted_results)}

Please analyze and categorize the news based on:

1. Financial Impact Analysis:
   - Revenue impact (positive/negative/neutral)
   - Cost impact
   - Funding/investment news
   - Valuation changes
   - Market performance factors

2. Strategic Developments:
   - New product launches
   - Market expansion
   - Partnerships and collaborations
   - Acquisitions or mergers
   - Leadership changes

3. Risk Assessment:
   - Regulatory issues
   - Legal challenges
   - Competitive threats
   - Market risks
   - Operational risks

4. Market Sentiment:
   - Overall sentiment (positive/negative/neutral)
   - Investor sentiment
   - Customer sentiment
   - Media sentiment

5. Key Trends:
   - Growth trends
   - Innovation trends
   - Market position changes
   - Industry trends affecting the company

For each news item, assess:
- Relevance to financial performance (0.0-1.0)
- Impact magnitude (low/medium/high)
- Time horizon (immediate/short-term/long-term)

Output in JSON format:
```json
{{
    "company_name": "{company_name}",
    "analysis_period": "{timeframe}",
    "financial_impact": {{
        "revenue_impact": {{
            "positive_factors": ["Factor 1", "Factor 2"],
            "negative_factors": ["Factor 1", "Factor 2"],
            "impact_score": 0.7,
            "confidence": 0.8
        }},
        "funding_news": [
            {{
                "type": "funding_round",
                "amount": "100M",
                "impact": "positive",
                "relevance": 0.9,
                "summary": "Brief summary"
            }}
        ],
        "valuation_factors": [
            {{
                "factor": "New product launch",
                "impact": "positive",
                "relevance": 0.8,
                "time_horizon": "short-term"
            }}
        ]
    }},
    "strategic_developments": {{
        "product_launches": [
            {{
                "product": "Product Name",
                "impact": "high",
                "financial_relevance": 0.8,
                "summary": "Brief description"
            }}
        ],
        "partnerships": [
            {{
                "partner": "Partner Name",
                "type": "strategic_partnership",
                "impact": "medium",
                "financial_relevance": 0.6
            }}
        ],
        "market_expansion": [
            {{
                "market": "Geographic/Sector",
                "impact": "high",
                "financial_relevance": 0.7
            }}
        ]
    }},
    "risk_assessment": {{
        "regulatory_risks": [
            {{
                "risk": "Risk description",
                "severity": "medium",
                "probability": 0.6,
                "financial_impact": "negative"
            }}
        ],
        "competitive_threats": [
            {{
                "threat": "Competitor action",
                "severity": "high",
                "impact_on_market_share": 0.4
            }}
        ],
        "overall_risk_level": "medium"
    }},
    "market_sentiment": {{
        "overall_sentiment": "positive",
        "sentiment_score": 0.7,
        "investor_sentiment": "positive",
        "media_coverage": "mostly_positive",
        "sentiment_trends": [
            {{
                "period": "last_month",
                "sentiment": "positive",
                "key_drivers": ["Product launch", "Strong earnings"]
            }}
        ]
    }},
    "key_trends": {{
        "growth_indicators": [
            "User base expansion",
            "Revenue growth"
        ],
        "innovation_focus": [
            "AI development",
            "Platform expansion"
        ],
        "market_position": {{
            "current_position": "market_leader",
            "position_trend": "strengthening",
            "key_differentiators": ["Technology", "Brand"]
        }}
    }},
    "top_news_items": [
        {{
            "headline": "News headline",
            "financial_relevance": 0.9,
            "impact": "positive",
            "category": "funding",
            "summary": "Brief summary of financial implications"
        }}
    ],
    "analysis_quality": {{
        "data_coverage": 0.8,
        "source_reliability": 0.7,
        "overall_confidence": 0.75
    }},
    "last_updated": "2024-01-01"
}}
```
"""
        
        try:
            logger.info("🤖 NewsAnalysisNode: Calling LLM for news analysis")
            response = call_llm(prompt)
            
            # Extract JSON from response
            json_str = response.split("```json")[1].split("```")[0].strip()
            news_analysis = json.loads(json_str)
            
            logger.info("✅ NewsAnalysisNode: Successfully parsed news analysis")
            
            # Validate and clean the data
            news_analysis = self._validate_news_analysis(news_analysis, company_name)
            
            return news_analysis
            
        except (IndexError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ NewsAnalysisNode: Error parsing LLM response: {e}")
            logger.error(f"📄 NewsAnalysisNode: Raw response: {response}")
            
            # Return fallback structure
            return self._get_empty_news_analysis(company_name)
        
        except Exception as e:
            logger.error(f"❌ NewsAnalysisNode: Unexpected error: {e}")
            raise
    
    def _get_empty_news_analysis(self, company_name: str) -> Dict[str, Any]:
        """Return empty news analysis structure"""
        return {
            "company_name": company_name,
            "analysis_period": "12 months",
            "financial_impact": {
                "revenue_impact": {
                    "positive_factors": [],
                    "negative_factors": [],
                    "impact_score": 0.5,
                    "confidence": 0.0
                },
                "funding_news": [],
                "valuation_factors": []
            },
            "strategic_developments": {
                "product_launches": [],
                "partnerships": [],
                "market_expansion": []
            },
            "risk_assessment": {
                "regulatory_risks": [],
                "competitive_threats": [],
                "overall_risk_level": "unknown"
            },
            "market_sentiment": {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.5,
                "investor_sentiment": "neutral",
                "media_coverage": "limited",
                "sentiment_trends": []
            },
            "key_trends": {
                "growth_indicators": [],
                "innovation_focus": [],
                "market_position": {
                    "current_position": "unknown",
                    "position_trend": "stable",
                    "key_differentiators": []
                }
            },
            "top_news_items": [],
            "analysis_quality": {
                "data_coverage": 0.0,
                "source_reliability": 0.0,
                "overall_confidence": 0.0
            },
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
    
    def _validate_news_analysis(self, data: Dict[str, Any], company_name: str) -> Dict[str, Any]:
        """Validate and clean news analysis data"""
        # Ensure company name is correct
        data["company_name"] = company_name
        
        # Validate confidence and score values
        def validate_score(obj, key, default=0.5):
            if key in obj:
                obj[key] = max(0.0, min(1.0, obj[key]))
            else:
                obj[key] = default
        
        # Validate financial impact scores
        if "financial_impact" in data and "revenue_impact" in data["financial_impact"]:
            validate_score(data["financial_impact"]["revenue_impact"], "impact_score")
            validate_score(data["financial_impact"]["revenue_impact"], "confidence")
        
        # Validate market sentiment
        if "market_sentiment" in data:
            validate_score(data["market_sentiment"], "sentiment_score")
        
        # Validate analysis quality
        if "analysis_quality" in data:
            for key in ["data_coverage", "source_reliability", "overall_confidence"]:
                validate_score(data["analysis_quality"], key, 0.0)
        
        # Ensure required sections exist
        required_sections = [
            "financial_impact", "strategic_developments", "risk_assessment", 
            "market_sentiment", "key_trends", "top_news_items", "analysis_quality"
        ]
        
        for section in required_sections:
            if section not in data:
                data[section] = {}
        
        return data
    
    def post(self, shared: Dict[str, Any], prep_res: tuple, exec_res: Dict[str, Any]) -> str:
        """Store news analysis in shared store"""
        logger.info(f"💾 NewsAnalysisNode: post - Storing news analysis for {exec_res.get('company_name', 'Unknown')}")
        
        shared["news_analysis"] = exec_res
        
        # Also store in a more specific key for downstream nodes
        company_name = exec_res.get("company_name", "unknown")
        shared[f"{company_name.lower().replace(' ', '_')}_news_analysis"] = exec_res
        
        # Extract key insights for easy access
        sentiment_score = exec_res.get("market_sentiment", {}).get("sentiment_score", 0.5)
        overall_risk = exec_res.get("risk_assessment", {}).get("overall_risk_level", "unknown")
        
        shared["news_insights"] = {
            "sentiment_score": sentiment_score,
            "sentiment": "positive" if sentiment_score > 0.6 else "negative" if sentiment_score < 0.4 else "neutral",
            "risk_level": overall_risk,
            "top_developments": [item.get("headline", "") for item in exec_res.get("top_news_items", [])[:3]],
            "financial_impact_score": exec_res.get("financial_impact", {}).get("revenue_impact", {}).get("impact_score", 0.5)
        }
        
        confidence = exec_res.get("analysis_quality", {}).get("overall_confidence", 0.0)
        logger.info(f"✅ NewsAnalysisNode: Stored news analysis with confidence score: {confidence}")
        
        return "default"