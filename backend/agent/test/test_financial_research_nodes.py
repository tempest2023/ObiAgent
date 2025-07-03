import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from agent.function_nodes.company_info_search import CompanyInfoSearchNode
from agent.function_nodes.financial_data_search import FinancialDataSearchNode
from agent.function_nodes.news_analysis import NewsAnalysisNode
from agent.function_nodes.financial_metrics_calculator import FinancialMetricsCalculatorNode
from agent.function_nodes.financial_report_generator import FinancialReportGeneratorNode


class TestCompanyInfoSearchNode:
    """Test CompanyInfoSearchNode functionality"""
    
    def test_prep_with_valid_data(self):
        node = CompanyInfoSearchNode()
        shared = {
            "company_name": "OpenAI",
            "search_results": [{"title": "Test", "snippet": "Test content"}]
        }
        
        company_name, search_results = node.prep(shared)
        
        assert company_name == "OpenAI"
        assert len(search_results) == 1
        assert search_results[0]["title"] == "Test"
    
    def test_prep_with_missing_data(self):
        node = CompanyInfoSearchNode()
        shared = {}
        
        company_name, search_results = node.prep(shared)
        
        assert company_name == ""
        assert search_results == []
    
    @patch('agent.function_nodes.company_info_search.call_llm')
    def test_exec_successful_parsing(self, mock_llm):
        node = CompanyInfoSearchNode()
        
        # Mock LLM response with valid JSON
        mock_response = '''
Here is the analysis:
```json
{
    "company_name": "OpenAI",
    "founding_info": {
        "year": 2015,
        "founders": ["Sam Altman", "Elon Musk"],
        "location": "San Francisco, CA"
    },
    "business_model": "AI research and API services",
    "industry": "Artificial Intelligence",
    "description": "Leading AI research organization",
    "key_personnel": [
        {"name": "Sam Altman", "role": "CEO"}
    ],
    "headquarters": "San Francisco, CA",
    "employee_count": 1000,
    "website": "https://openai.com",
    "products_services": ["GPT-4", "API"],
    "target_market": "Developers and enterprises",
    "confidence_score": 0.9
}
```
'''
        mock_llm.return_value = mock_response
        
        inputs = ("OpenAI", [{"title": "OpenAI info", "snippet": "AI company founded in 2015"}])
        result = node.exec(inputs)
        
        assert result["company_name"] == "OpenAI"
        assert result["founding_info"]["year"] == 2015
        assert result["industry"] == "Artificial Intelligence"
        assert result["confidence_score"] == 0.9
        assert "Sam Altman" in result["founding_info"]["founders"]
    
    @patch('agent.function_nodes.company_info_search.call_llm')
    def test_exec_parsing_error(self, mock_llm):
        node = CompanyInfoSearchNode()
        
        # Mock LLM response with invalid JSON
        mock_llm.return_value = "Invalid response without proper JSON"
        
        inputs = ("OpenAI", [{"title": "Test", "snippet": "Test content"}])
        result = node.exec(inputs)
        
        # Should return fallback structure
        assert result["company_name"] == "OpenAI"
        assert result["confidence_score"] == 0.1
        assert result["business_model"] == "Information extraction failed"
    
    def test_exec_no_search_results(self):
        node = CompanyInfoSearchNode()
        
        inputs = ("OpenAI", [])
        result = node.exec(inputs)
        
        assert result["company_name"] == "OpenAI"
        assert result["confidence_score"] == 0.0
        assert result["founding_info"]["year"] is None
    
    def test_post_stores_data_correctly(self):
        node = CompanyInfoSearchNode()
        shared = {}
        
        exec_res = {
            "company_name": "OpenAI",
            "industry": "AI",
            "confidence_score": 0.8
        }
        
        action = node.post(shared, ("OpenAI", []), exec_res)
        
        assert action == "default"
        assert shared["company_info"] == exec_res
        assert shared["openai_info"] == exec_res


class TestFinancialDataSearchNode:
    """Test FinancialDataSearchNode functionality"""
    
    def test_prep_with_complete_data(self):
        node = FinancialDataSearchNode()
        shared = {
            "company_name": "OpenAI",
            "search_results": [{"title": "OpenAI funding"}],
            "company_info": {"industry": "AI"}
        }
        
        company_name, search_results, company_info = node.prep(shared)
        
        assert company_name == "OpenAI"
        assert len(search_results) == 1
        assert company_info["industry"] == "AI"
    
    @patch('agent.function_nodes.financial_data_search.call_llm')
    def test_exec_successful_financial_extraction(self, mock_llm):
        node = FinancialDataSearchNode()
        
        # Mock LLM response with financial data
        mock_response = '''
```json
{
    "company_name": "OpenAI",
    "financial_year": "2024",
    "revenue": {
        "annual_revenue": {
            "amount": 2000000000,
            "currency": "USD",
            "year": 2023,
            "confidence": 0.8
        },
        "revenue_growth": {
            "rate": 300,
            "period": "year-over-year",
            "confidence": 0.7
        },
        "revenue_sources": ["API subscriptions", "Enterprise licenses"],
        "confidence_score": 0.8
    },
    "funding": {
        "total_funding": {
            "amount": 13000000000,
            "currency": "USD",
            "confidence": 0.9
        },
        "latest_round": {
            "amount": 10000000000,
            "type": "Series C",
            "date": "2023-01",
            "lead_investor": "Microsoft",
            "confidence": 0.9
        },
        "funding_history": [
            {"round": "Series A", "amount": 1000000000, "date": "2019"},
            {"round": "Series C", "amount": 10000000000, "date": "2023-01"}
        ],
        "confidence_score": 0.9
    },
    "valuation": {
        "current_valuation": {
            "amount": 80000000000,
            "currency": "USD",
            "date": "2023-01",
            "confidence": 0.8
        },
        "market_cap": {
            "amount": "Not Available",
            "currency": "USD",
            "confidence": 0.0
        },
        "confidence_score": 0.8
    },
    "overall_confidence": 0.8
}
```
'''
        mock_llm.return_value = mock_response
        
        inputs = ("OpenAI", [{"title": "OpenAI funding news"}], {"industry": "AI"})
        result = node.exec(inputs)
        
        assert result["company_name"] == "OpenAI"
        assert result["revenue"]["annual_revenue"]["amount"] == 2000000000
        assert result["funding"]["total_funding"]["amount"] == 13000000000
        assert result["valuation"]["current_valuation"]["amount"] == 80000000000
        assert result["overall_confidence"] == 0.8
    
    def test_exec_no_search_results(self):
        node = FinancialDataSearchNode()
        
        inputs = ("OpenAI", [], {})
        result = node.exec(inputs)
        
        # Should return empty structure
        assert result["company_name"] == "OpenAI"
        assert result["overall_confidence"] == 0.0
        assert result["revenue"]["annual_revenue"]["amount"] == "Not Available"
    
    def test_post_stores_financial_data(self):
        node = FinancialDataSearchNode()
        shared = {}
        
        exec_res = {
            "company_name": "OpenAI",
            "revenue": {"annual_revenue": {"amount": 1000000000}},
            "valuation": {"current_valuation": {"amount": 80000000000}},
            "funding": {"total_funding": {"amount": 13000000000}},
            "financial_metrics": {"profitability": {"status": "Profitable"}},
            "overall_confidence": 0.8
        }
        
        action = node.post(shared, ("OpenAI", [], {}), exec_res)
        
        assert action == "default"
        assert shared["financial_data"] == exec_res
        assert shared["openai_financial_data"] == exec_res
        assert shared["key_financial_metrics"]["revenue"] == 1000000000
        assert shared["key_financial_metrics"]["valuation"] == 80000000000


class TestNewsAnalysisNode:
    """Test NewsAnalysisNode functionality"""
    
    def test_prep_with_timeframe(self):
        node = NewsAnalysisNode()
        shared = {
            "company_name": "OpenAI",
            "search_results": [{"title": "OpenAI news"}],
            "news_timeframe": "6 months",
            "company_info": {"industry": "AI"}
        }
        
        company_name, search_results, timeframe, company_info = node.prep(shared)
        
        assert company_name == "OpenAI"
        assert timeframe == "6 months"
        assert len(search_results) == 1
    
    @patch('agent.function_nodes.news_analysis.call_llm')
    def test_exec_successful_news_analysis(self, mock_llm):
        node = NewsAnalysisNode()
        
        # Mock LLM response with news analysis
        mock_response = '''
```json
{
    "company_name": "OpenAI",
    "analysis_period": "12 months",
    "financial_impact": {
        "revenue_impact": {
            "positive_factors": ["ChatGPT launch", "Enterprise partnerships"],
            "negative_factors": ["Increased competition"],
            "impact_score": 0.8,
            "confidence": 0.7
        },
        "funding_news": [
            {
                "type": "funding_round",
                "amount": "10B",
                "impact": "positive",
                "relevance": 0.9,
                "summary": "Major funding round from Microsoft"
            }
        ]
    },
    "market_sentiment": {
        "overall_sentiment": "positive",
        "sentiment_score": 0.8,
        "investor_sentiment": "very_positive",
        "media_coverage": "extensive"
    },
    "risk_assessment": {
        "regulatory_risks": [],
        "competitive_threats": [
            {
                "threat": "Google Bard competition",
                "severity": "medium",
                "impact_on_market_share": 0.3
            }
        ],
        "overall_risk_level": "medium"
    },
    "analysis_quality": {
        "data_coverage": 0.8,
        "source_reliability": 0.7,
        "overall_confidence": 0.75
    }
}
```
'''
        mock_llm.return_value = mock_response
        
        inputs = ("OpenAI", [{"title": "OpenAI ChatGPT launch"}], "12 months", {"industry": "AI"})
        result = node.exec(inputs)
        
        assert result["company_name"] == "OpenAI"
        assert result["market_sentiment"]["sentiment_score"] == 0.8
        assert result["financial_impact"]["revenue_impact"]["impact_score"] == 0.8
        assert len(result["financial_impact"]["funding_news"]) == 1
        assert result["analysis_quality"]["overall_confidence"] == 0.75
    
    def test_post_stores_news_analysis(self):
        node = NewsAnalysisNode()
        shared = {}
        
        exec_res = {
            "company_name": "OpenAI",
            "market_sentiment": {"sentiment_score": 0.8, "overall_sentiment": "positive"},
            "risk_assessment": {"overall_risk_level": "medium"},
            "top_news_items": [{"headline": "OpenAI launches GPT-4"}],
            "financial_impact": {"revenue_impact": {"impact_score": 0.7}},
            "analysis_quality": {"overall_confidence": 0.8}
        }
        
        action = node.post(shared, ("OpenAI", [], "12 months", {}), exec_res)
        
        assert action == "default"
        assert shared["news_analysis"] == exec_res
        assert shared["news_insights"]["sentiment"] == "positive"
        assert shared["news_insights"]["sentiment_score"] == 0.8
        assert shared["news_insights"]["risk_level"] == "medium"


class TestFinancialMetricsCalculatorNode:
    """Test FinancialMetricsCalculatorNode functionality"""
    
    def test_prep_with_all_data(self):
        node = FinancialMetricsCalculatorNode()
        shared = {
            "financial_data": {"company_name": "OpenAI", "revenue": {}},
            "company_info": {"employee_count": 1000},
            "news_analysis": {"market_sentiment": {}}
        }
        
        financial_data, company_info, news_analysis = node.prep(shared)
        
        assert financial_data["company_name"] == "OpenAI"
        assert company_info["employee_count"] == 1000
        assert "market_sentiment" in news_analysis
    
    def test_exec_comprehensive_metrics_calculation(self):
        node = FinancialMetricsCalculatorNode()
        
        # Prepare comprehensive test data
        financial_data = {
            "company_name": "OpenAI",
            "revenue": {
                "annual_revenue": {"amount": 2000000000, "currency": "USD", "year": 2023},
                "revenue_growth": {"rate": 300, "period": "year-over-year"},
                "revenue_sources": ["API", "Enterprise", "Consumer"]
            },
            "funding": {
                "total_funding": {"amount": 13000000000, "currency": "USD"},
                "latest_round": {"amount": 10000000000, "type": "Series C", "date": "2023-01"},
                "funding_history": [
                    {"round": "Series A", "amount": 1000000000, "date": "2019"},
                    {"round": "Series C", "amount": 10000000000, "date": "2023-01"}
                ]
            },
            "valuation": {
                "current_valuation": {"amount": 80000000000, "currency": "USD", "date": "2023-01"}
            },
            "financial_metrics": {
                "profitability": {"status": "Profitable", "details": "Strong margins"},
                "burn_rate": {"monthly_burn": 50000000, "runway_months": 30}
            }
        }
        
        company_info = {
            "company_name": "OpenAI",
            "employee_count": 1000,
            "industry": "Artificial Intelligence"
        }
        
        news_analysis = {
            "financial_impact": {"revenue_impact": {"impact_score": 0.8}},
            "market_sentiment": {"sentiment_score": 0.8},
            "risk_assessment": {"overall_risk_level": "medium"},
            "key_trends": {
                "market_position": {
                    "current_position": "market_leader",
                    "position_trend": "strengthening",
                    "key_differentiators": ["Technology", "Brand", "Talent"]
                }
            }
        }
        
        inputs = (financial_data, company_info, news_analysis)
        result = node.exec(inputs)
        
        # Verify comprehensive metrics calculation
        assert result["company_name"] == "OpenAI"
        assert "valuation_metrics" in result
        assert "growth_metrics" in result
        assert "performance_metrics" in result
        assert "investment_metrics" in result
        assert "risk_metrics" in result
        assert "market_metrics" in result
        assert "health_indicators" in result
        assert "overall_assessment" in result
        
        # Check specific calculations
        assert result["valuation_metrics"]["current_valuation"] == 80000000000
        assert result["valuation_metrics"]["price_to_revenue_ratio"] == 40.0  # 80B / 2B
        assert result["growth_metrics"]["revenue_growth_rate"] == "300%"
        assert result["growth_metrics"]["growth_category"] == "High Growth"
        assert result["performance_metrics"]["revenue_per_employee"] == 2000000  # 2B / 1000
        assert result["performance_metrics"]["profitability_status"] == "Profitable"
        assert result["health_indicators"]["financial_health_score"] >= 80  # Should be high
        assert result["overall_assessment"]["investment_grade"] in ["A", "B+"]
    
    def test_exec_with_limited_data(self):
        node = FinancialMetricsCalculatorNode()
        
        # Test with minimal data
        financial_data = {"company_name": "TestCorp"}
        company_info = {}
        news_analysis = {}
        
        inputs = (financial_data, company_info, news_analysis)
        result = node.exec(inputs)
        
        assert result["company_name"] == "TestCorp"
        assert result["health_indicators"]["financial_health_score"] == 0
        assert result["health_indicators"]["health_rating"] == "Critical"
    
    def test_post_stores_calculated_metrics(self):
        node = FinancialMetricsCalculatorNode()
        shared = {}
        
        exec_res = {
            "company_name": "OpenAI",
            "health_indicators": {"financial_health_score": 85, "health_rating": "Excellent"},
            "overall_assessment": {"investment_grade": "A"},
            "growth_metrics": {"growth_category": "High Growth"},
            "market_metrics": {"market_position": "market_leader"}
        }
        
        action = node.post(shared, ({}, {}, {}), exec_res)
        
        assert action == "default"
        assert shared["financial_metrics_calculated"] == exec_res
        assert shared["financial_summary"]["health_score"] == 85
        assert shared["financial_summary"]["health_rating"] == "Excellent"
        assert shared["financial_summary"]["investment_grade"] == "A"


class TestFinancialReportGeneratorNode:
    """Test FinancialReportGeneratorNode functionality"""
    
    def test_prep_with_comprehensive_data(self):
        node = FinancialReportGeneratorNode()
        shared = {
            "company_info": {"company_name": "OpenAI"},
            "financial_data": {"revenue": {}},
            "news_analysis": {"market_sentiment": {}},
            "financial_metrics_calculated": {"health_indicators": {}},
            "report_type": "comprehensive"
        }
        
        company_info, financial_data, news_analysis, financial_metrics, report_type = node.prep(shared)
        
        assert company_info["company_name"] == "OpenAI"
        assert report_type == "comprehensive"
        assert "revenue" in financial_data
        assert "market_sentiment" in news_analysis
        assert "health_indicators" in financial_metrics
    
    def test_exec_comprehensive_report_generation(self):
        node = FinancialReportGeneratorNode()
        
        # Prepare comprehensive test data for report generation
        company_info = {
            "company_name": "OpenAI",
            "industry": "Artificial Intelligence",
            "founding_info": {"year": 2015, "founders": ["Sam Altman"]},
            "headquarters": "San Francisco, CA",
            "employee_count": 1000,
            "business_model": "AI research and API services",
            "confidence_score": 0.9
        }
        
        financial_data = {
            "company_name": "OpenAI",
            "revenue": {
                "annual_revenue": {"amount": 2000000000, "currency": "USD", "year": 2023},
                "revenue_growth": {"rate": 300},
                "revenue_sources": ["API", "Enterprise"]
            },
            "funding": {
                "total_funding": {"amount": 13000000000, "currency": "USD"},
                "latest_round": {"amount": 10000000000, "type": "Series C"}
            },
            "valuation": {
                "current_valuation": {"amount": 80000000000, "currency": "USD"}
            },
            "overall_confidence": 0.8
        }
        
        news_analysis = {
            "market_sentiment": {"sentiment_score": 0.8, "overall_sentiment": "positive"},
            "risk_assessment": {"overall_risk_level": "medium"},
            "key_trends": {"growth_indicators": ["User growth", "Revenue growth"]},
            "strategic_developments": {"market_expansion": ["International", "Enterprise"]},
            "analysis_quality": {"overall_confidence": 0.75}
        }
        
        financial_metrics = {
            "company_name": "OpenAI",
            "health_indicators": {
                "financial_health_score": 85,
                "health_rating": "Excellent",
                "key_strengths": ["Strong revenue", "Market leader"],
                "key_weaknesses": ["High burn rate"]
            },
            "overall_assessment": {
                "investment_grade": "A",
                "key_insights": ["Strong growth", "Market dominance"]
            },
            "growth_metrics": {"growth_category": "High Growth"},
            "market_metrics": {"market_position": "market_leader"},
            "valuation_metrics": {"price_to_revenue_ratio": 40.0},
            "risk_metrics": {"market_risk_level": "medium"}
        }
        
        inputs = (company_info, financial_data, news_analysis, financial_metrics, "comprehensive")
        result = node.exec(inputs)
        
        # Verify comprehensive report structure
        assert result["report_type"] == "comprehensive"
        assert result["company_name"] == "OpenAI"
        assert "generated_date" in result
        assert "report_sections" in result
        assert "report_metadata" in result
        
        # Check all required sections
        sections = result["report_sections"]
        assert "executive_summary" in sections
        assert "company_overview" in sections
        assert "financial_performance" in sections
        assert "market_analysis" in sections
        assert "risk_assessment" in sections
        assert "key_metrics" in sections
        assert "investment_analysis" in sections
        assert "recommendations" in sections
        
        # Verify executive summary content
        exec_summary = sections["executive_summary"]
        assert "key_highlights" in exec_summary
        assert "financial_health" in exec_summary
        assert exec_summary["financial_health"]["score"] == 85
        assert exec_summary["financial_health"]["investment_grade"] == "A"
        assert exec_summary["investment_recommendation"] in ["Strong Buy", "Buy"]
        
        # Verify report metadata
        metadata = result["report_metadata"]
        assert "data_sources" in metadata
        assert "confidence_scores" in metadata
        assert "data_coverage" in metadata
    
    def test_exec_executive_summary_only(self):
        node = FinancialReportGeneratorNode()
        
        company_info = {"company_name": "OpenAI"}
        financial_data = {"company_name": "OpenAI"}
        news_analysis = {}
        financial_metrics = {
            "health_indicators": {"financial_health_score": 70},
            "overall_assessment": {"investment_grade": "B+"},
            "growth_metrics": {"growth_category": "Moderate Growth"}
        }
        
        inputs = (company_info, financial_data, news_analysis, financial_metrics, "executive_summary")
        result = node.exec(inputs)
        
        assert result["report_type"] == "executive_summary"
        assert result["company_name"] == "OpenAI"
        assert "executive_summary" in result
        assert "key_metrics" in result
        assert result["key_metrics"]["health_score"] == 70
        assert result["key_metrics"]["investment_grade"] == "B+"
    
    def test_post_stores_report_correctly(self):
        node = FinancialReportGeneratorNode()
        shared = {}
        
        exec_res = {
            "report_type": "comprehensive",
            "company_name": "OpenAI",
            "report_sections": {
                "executive_summary": {"investment_recommendation": "Buy"},
                "company_overview": {},
                "financial_performance": {},
                "market_analysis": {},
                "risk_assessment": {},
                "key_metrics": {},
                "investment_analysis": {},
                "recommendations": {}
            },
            "report_metadata": {
                "confidence_scores": {"overall_confidence": 0.8},
                "data_coverage": {"overall": "Good"}
            }
        }
        
        action = node.post(shared, ({}, {}, {}, {}, "comprehensive"), exec_res)
        
        assert action == "default"
        assert shared["financial_report"] == exec_res
        assert shared["openai_financial_report"] == exec_res
        assert shared["report_summary"]["report_type"] == "comprehensive"
        assert shared["report_summary"]["sections_count"] == 8
        assert shared["report_summary"]["confidence"] == 0.8
        assert shared["report_summary"]["investment_recommendation"] == "Buy"


class TestIntegrationWorkflow:
    """Test the complete workflow integration"""
    
    @patch('agent.function_nodes.company_info_search.call_llm')
    @patch('agent.function_nodes.financial_data_search.call_llm')
    @patch('agent.function_nodes.news_analysis.call_llm')
    def test_complete_workflow_integration(self, mock_news_llm, mock_financial_llm, mock_company_llm):
        """Test the complete financial research workflow"""
        
        # Mock LLM responses
        mock_company_llm.return_value = '''
```json
{
    "company_name": "OpenAI",
    "founding_info": {"year": 2015, "founders": ["Sam Altman"]},
    "industry": "Artificial Intelligence",
    "business_model": "AI research and API services",
    "description": "Leading AI research organization",
    "employee_count": 1000,
    "confidence_score": 0.9
}
```
'''
        
        mock_financial_llm.return_value = '''
```json
{
    "company_name": "OpenAI",
    "revenue": {
        "annual_revenue": {"amount": 2000000000, "currency": "USD", "year": 2023},
        "revenue_growth": {"rate": 300},
        "confidence_score": 0.8
    },
    "funding": {
        "total_funding": {"amount": 13000000000, "currency": "USD"},
        "confidence_score": 0.9
    },
    "valuation": {
        "current_valuation": {"amount": 80000000000, "currency": "USD"},
        "confidence_score": 0.8
    },
    "overall_confidence": 0.8
}
```
'''
        
        mock_news_llm.return_value = '''
```json
{
    "company_name": "OpenAI",
    "market_sentiment": {"sentiment_score": 0.8, "overall_sentiment": "positive"},
    "risk_assessment": {"overall_risk_level": "medium"},
    "analysis_quality": {"overall_confidence": 0.75}
}
```
'''
        
        # Initialize shared store
        shared = {
            "company_name": "OpenAI",
            "search_results": [
                {"title": "OpenAI Company Info", "snippet": "AI research company"},
                {"title": "OpenAI Funding", "snippet": "Raised $13B total"}
            ]
        }
        
        # Step 1: Company Info Search
        company_node = CompanyInfoSearchNode()
        company_prep = company_node.prep(shared)
        company_result = company_node.exec(company_prep)
        company_node.post(shared, company_prep, company_result)
        
        # Step 2: Financial Data Search
        financial_node = FinancialDataSearchNode()
        financial_prep = financial_node.prep(shared)
        financial_result = financial_node.exec(financial_prep)
        financial_node.post(shared, financial_prep, financial_result)
        
        # Step 3: News Analysis
        news_node = NewsAnalysisNode()
        news_prep = news_node.prep(shared)
        news_result = news_node.exec(news_prep)
        news_node.post(shared, news_prep, news_result)
        
        # Step 4: Financial Metrics Calculation
        metrics_node = FinancialMetricsCalculatorNode()
        metrics_prep = metrics_node.prep(shared)
        metrics_result = metrics_node.exec(metrics_prep)
        metrics_node.post(shared, metrics_prep, metrics_result)
        
        # Step 5: Financial Report Generation
        report_node = FinancialReportGeneratorNode()
        report_prep = report_node.prep(shared)
        report_result = report_node.exec(report_prep)
        report_node.post(shared, report_prep, report_result)
        
        # Verify final results
        assert "company_info" in shared
        assert "financial_data" in shared
        assert "news_analysis" in shared
        assert "financial_metrics_calculated" in shared
        assert "financial_report" in shared
        
        # Check data flow between nodes
        assert shared["company_info"]["company_name"] == "OpenAI"
        assert shared["financial_data"]["company_name"] == "OpenAI"
        assert shared["financial_metrics_calculated"]["company_name"] == "OpenAI"
        assert shared["financial_report"]["company_name"] == "OpenAI"
        
        # Verify report quality
        final_report = shared["financial_report"]
        assert final_report["report_type"] == "comprehensive"
        assert len(final_report["report_sections"]) == 8
        
        # Check calculated metrics
        metrics = shared["financial_metrics_calculated"]
        assert metrics["health_indicators"]["financial_health_score"] > 70  # Should be high given strong data
        assert metrics["overall_assessment"]["investment_grade"] in ["A", "B+", "B"]
        
        # Verify summary data
        assert "financial_summary" in shared
        assert "report_summary" in shared
        assert shared["report_summary"]["investment_recommendation"] in ["Strong Buy", "Buy", "Hold"]


if __name__ == "__main__":
    pytest.main([__file__])