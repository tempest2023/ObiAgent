from pocketflow import Node
from typing import Dict, List, Any, Optional
from agent.utils.stream_llm import call_llm
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class FinancialReportGeneratorNode(Node):
    """
    Node to generate comprehensive financial reports from collected data,
    metrics, and analysis. Creates structured reports with multiple sections.
    
    Example:
        >>> node = FinancialReportGeneratorNode()
        >>> shared = {"company_info": {...}, "financial_data": {...}, "financial_metrics_calculated": {...}}
        >>> node.prep(shared)
        # Returns all collected data for report generation
        >>> node.exec((...))
        # Returns structured financial report
    """
    
    def prep(self, shared: Dict[str, Any]) -> tuple:
        """Prepare all collected data for financial report generation"""
        company_info = shared.get("company_info", {})
        financial_data = shared.get("financial_data", {})
        news_analysis = shared.get("news_analysis", {})
        financial_metrics = shared.get("financial_metrics_calculated", {})
        report_type = shared.get("report_type", "comprehensive")
        
        company_name = company_info.get("company_name", financial_data.get("company_name", "Unknown"))
        logger.info(f"🔄 FinancialReportGeneratorNode: prep - generating {report_type} report for {company_name}")
        
        if not company_info and not financial_data:
            logger.warning("⚠️ FinancialReportGeneratorNode: Limited data available for report generation")
            
        return company_info, financial_data, news_analysis, financial_metrics, report_type
    
    def exec(self, inputs: tuple) -> Dict[str, Any]:
        """Generate comprehensive financial report"""
        company_info, financial_data, news_analysis, financial_metrics, report_type = inputs
        
        company_name = company_info.get("company_name", financial_data.get("company_name", "Unknown"))
        logger.info(f"🔄 FinancialReportGeneratorNode: exec - generating report for {company_name}")
        
        try:
            if report_type == "comprehensive":
                report = self._generate_comprehensive_report(company_info, financial_data, news_analysis, financial_metrics)
            elif report_type == "executive_summary":
                report = self._generate_executive_summary(company_info, financial_data, news_analysis, financial_metrics)
            elif report_type == "metrics_only":
                report = self._generate_metrics_report(financial_metrics, financial_data)
            else:
                # Default to comprehensive
                report = self._generate_comprehensive_report(company_info, financial_data, news_analysis, financial_metrics)
            
            logger.info("✅ FinancialReportGeneratorNode: Successfully generated financial report")
            return report
            
        except Exception as e:
            logger.error(f"❌ FinancialReportGeneratorNode: Error generating report: {e}")
            return self._get_empty_report(company_name, report_type)
    
    def _generate_comprehensive_report(self, company_info: Dict, financial_data: Dict, news_analysis: Dict, financial_metrics: Dict) -> Dict[str, Any]:
        """Generate a comprehensive financial report"""
        company_name = company_info.get("company_name", financial_data.get("company_name", "Unknown"))
        
        report = {
            "report_type": "comprehensive",
            "company_name": company_name,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_sections": {}
        }
        
        # Section 1: Executive Summary
        report["report_sections"]["executive_summary"] = self._create_executive_summary(
            company_info, financial_data, financial_metrics
        )
        
        # Section 2: Company Overview
        report["report_sections"]["company_overview"] = self._create_company_overview(company_info)
        
        # Section 3: Financial Performance
        report["report_sections"]["financial_performance"] = self._create_financial_performance(
            financial_data, financial_metrics
        )
        
        # Section 4: Market Analysis
        report["report_sections"]["market_analysis"] = self._create_market_analysis(
            news_analysis, financial_metrics
        )
        
        # Section 5: Risk Assessment
        report["report_sections"]["risk_assessment"] = self._create_risk_assessment(
            news_analysis, financial_metrics
        )
        
        # Section 6: Key Metrics Dashboard
        report["report_sections"]["key_metrics"] = self._create_metrics_dashboard(financial_metrics)
        
        # Section 7: Investment Analysis
        report["report_sections"]["investment_analysis"] = self._create_investment_analysis(
            financial_data, financial_metrics, news_analysis
        )
        
        # Section 8: Recommendations and Outlook
        report["report_sections"]["recommendations"] = self._create_recommendations(
            financial_metrics, news_analysis
        )
        
        # Report metadata
        report["report_metadata"] = {
            "data_sources": self._extract_data_sources(financial_data, news_analysis),
            "confidence_scores": self._extract_confidence_scores(financial_data, news_analysis, financial_metrics),
            "data_coverage": self._assess_data_coverage(company_info, financial_data, news_analysis, financial_metrics),
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
        
        return report
    
    def _create_executive_summary(self, company_info: Dict, financial_data: Dict, financial_metrics: Dict) -> Dict[str, Any]:
        """Create executive summary section"""
        summary = {}
        
        try:
            # Key highlights
            highlights = []
            
            # Company basics
            company_name = company_info.get("company_name", "Unknown")
            industry = company_info.get("industry", "Unknown")
            founded_year = company_info.get("founding_info", {}).get("year")
            
            if founded_year:
                highlights.append(f"{company_name} is a {industry} company founded in {founded_year}")
            else:
                highlights.append(f"{company_name} operates in the {industry} industry")
            
            # Financial highlights
            revenue = financial_data.get("revenue", {}).get("annual_revenue", {}).get("amount")
            if isinstance(revenue, (int, float)) and revenue > 0:
                revenue_formatted = self._format_currency(revenue)
                highlights.append(f"Annual revenue: {revenue_formatted}")
            
            valuation = financial_data.get("valuation", {}).get("current_valuation", {}).get("amount")
            if isinstance(valuation, (int, float)) and valuation > 0:
                valuation_formatted = self._format_currency(valuation)
                highlights.append(f"Current valuation: {valuation_formatted}")
            
            funding = financial_data.get("funding", {}).get("total_funding", {}).get("amount")
            if isinstance(funding, (int, float)) and funding > 0:
                funding_formatted = self._format_currency(funding)
                highlights.append(f"Total funding raised: {funding_formatted}")
            
            # Health and performance
            health_score = financial_metrics.get("health_indicators", {}).get("financial_health_score", 0)
            health_rating = financial_metrics.get("health_indicators", {}).get("health_rating", "Unknown")
            investment_grade = financial_metrics.get("overall_assessment", {}).get("investment_grade", "N/A")
            
            summary = {
                "key_highlights": highlights,
                "financial_health": {
                    "score": health_score,
                    "rating": health_rating,
                    "investment_grade": investment_grade
                },
                "key_strengths": financial_metrics.get("health_indicators", {}).get("key_strengths", []),
                "key_concerns": financial_metrics.get("health_indicators", {}).get("key_weaknesses", []),
                "investment_recommendation": self._get_investment_recommendation(financial_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error creating executive summary: {e}")
            summary = {"error": "Unable to generate executive summary"}
        
        return summary
    
    def _create_company_overview(self, company_info: Dict) -> Dict[str, Any]:
        """Create company overview section"""
        overview = {}
        
        try:
            overview = {
                "basic_information": {
                    "company_name": company_info.get("company_name", "Unknown"),
                    "industry": company_info.get("industry", "Unknown"),
                    "founded": company_info.get("founding_info", {}).get("year", "Unknown"),
                    "founders": company_info.get("founding_info", {}).get("founders", []),
                    "headquarters": company_info.get("headquarters", "Unknown"),
                    "website": company_info.get("website", "Unknown"),
                    "employee_count": company_info.get("employee_count", "Unknown")
                },
                "business_model": {
                    "description": company_info.get("business_model", "Unknown"),
                    "target_market": company_info.get("target_market", "Unknown"),
                    "products_services": company_info.get("products_services", [])
                },
                "leadership": company_info.get("key_personnel", []),
                "company_description": company_info.get("description", "No description available")
            }
            
        except Exception as e:
            logger.error(f"Error creating company overview: {e}")
            overview = {"error": "Unable to generate company overview"}
        
        return overview
    
    def _create_financial_performance(self, financial_data: Dict, financial_metrics: Dict) -> Dict[str, Any]:
        """Create financial performance section"""
        performance = {}
        
        try:
            # Revenue analysis
            revenue_data = financial_data.get("revenue", {})
            revenue_metrics = financial_metrics.get("growth_metrics", {})
            
            # Funding analysis
            funding_data = financial_data.get("funding", {})
            investment_metrics = financial_metrics.get("investment_metrics", {})
            
            # Valuation analysis
            valuation_data = financial_data.get("valuation", {})
            valuation_metrics = financial_metrics.get("valuation_metrics", {})
            
            performance = {
                "revenue_analysis": {
                    "annual_revenue": revenue_data.get("annual_revenue", {}),
                    "growth_rate": revenue_data.get("revenue_growth", {}),
                    "revenue_sources": revenue_data.get("revenue_sources", []),
                    "growth_category": revenue_metrics.get("growth_category", "Unknown"),
                    "per_employee": financial_metrics.get("performance_metrics", {}).get("revenue_per_employee", "N/A")
                },
                "funding_analysis": {
                    "total_funding": funding_data.get("total_funding", {}),
                    "latest_round": funding_data.get("latest_round", {}),
                    "funding_history": funding_data.get("funding_history", []),
                    "capital_efficiency": investment_metrics.get("capital_efficiency_ratio", "N/A"),
                    "funding_stage": investment_metrics.get("funding_stage", "Unknown")
                },
                "valuation_analysis": {
                    "current_valuation": valuation_data.get("current_valuation", {}),
                    "market_cap": valuation_data.get("market_cap", {}),
                    "price_to_revenue": valuation_metrics.get("price_to_revenue_ratio", "N/A"),
                    "valuation_to_funding": valuation_metrics.get("valuation_to_funding_ratio", "N/A")
                },
                "profitability": {
                    "status": financial_data.get("financial_metrics", {}).get("profitability", {}),
                    "ebitda": financial_data.get("financial_metrics", {}).get("ebitda", {}),
                    "burn_rate": financial_data.get("financial_metrics", {}).get("burn_rate", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating financial performance section: {e}")
            performance = {"error": "Unable to generate financial performance analysis"}
        
        return performance
    
    def _create_market_analysis(self, news_analysis: Dict, financial_metrics: Dict) -> Dict[str, Any]:
        """Create market analysis section"""
        market_analysis = {}
        
        try:
            market_metrics = financial_metrics.get("market_metrics", {})
            market_sentiment = news_analysis.get("market_sentiment", {})
            key_trends = news_analysis.get("key_trends", {})
            
            market_analysis = {
                "market_position": {
                    "current_position": market_metrics.get("market_position", "Unknown"),
                    "position_trend": market_metrics.get("position_trend", "stable"),
                    "competitive_strength": market_metrics.get("competitive_strength", "Unknown"),
                    "competitive_advantages": market_metrics.get("competitive_advantages", 0)
                },
                "market_sentiment": {
                    "overall_sentiment": market_sentiment.get("overall_sentiment", "neutral"),
                    "sentiment_score": market_sentiment.get("sentiment_score", 0.5),
                    "investor_sentiment": market_sentiment.get("investor_sentiment", "neutral"),
                    "media_coverage": market_sentiment.get("media_coverage", "limited")
                },
                "industry_trends": {
                    "growth_indicators": key_trends.get("growth_indicators", []),
                    "innovation_focus": key_trends.get("innovation_focus", []),
                    "market_drivers": news_analysis.get("financial_impact", {}).get("revenue_impact", {}).get("positive_factors", [])
                },
                "strategic_developments": news_analysis.get("strategic_developments", {})
            }
            
        except Exception as e:
            logger.error(f"Error creating market analysis: {e}")
            market_analysis = {"error": "Unable to generate market analysis"}
        
        return market_analysis
    
    def _create_risk_assessment(self, news_analysis: Dict, financial_metrics: Dict) -> Dict[str, Any]:
        """Create risk assessment section"""
        risk_assessment = {}
        
        try:
            risk_metrics = financial_metrics.get("risk_metrics", {})
            news_risks = news_analysis.get("risk_assessment", {})
            
            risk_assessment = {
                "financial_risks": {
                    "cash_runway": risk_metrics.get("cash_runway", "Unknown"),
                    "runway_risk": risk_metrics.get("runway_risk", "Unknown"),
                    "funding_dependency": risk_metrics.get("funding_dependency", "Unknown"),
                    "profitability_timeline": "Assessment based on burn rate and revenue growth"
                },
                "market_risks": {
                    "overall_risk_level": news_risks.get("overall_risk_level", "unknown"),
                    "competitive_threats": news_risks.get("competitive_threats", []),
                    "regulatory_risks": news_risks.get("regulatory_risks", []),
                    "market_sentiment_risk": risk_metrics.get("market_risk_level", "unknown")
                },
                "operational_risks": {
                    "key_person_risk": "Based on leadership concentration",
                    "scalability_risk": "Based on business model and funding",
                    "technology_risk": "Based on industry and innovation focus"
                },
                "investment_risks": {
                    "valuation_risk": "Based on current multiples and market conditions",
                    "liquidity_risk": "Based on funding stage and market access",
                    "dilution_risk": "Based on funding requirements and growth trajectory"
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating risk assessment: {e}")
            risk_assessment = {"error": "Unable to generate risk assessment"}
        
        return risk_assessment
    
    def _create_metrics_dashboard(self, financial_metrics: Dict) -> Dict[str, Any]:
        """Create key metrics dashboard"""
        dashboard = {}
        
        try:
            dashboard = {
                "valuation_metrics": financial_metrics.get("valuation_metrics", {}),
                "growth_metrics": financial_metrics.get("growth_metrics", {}),
                "performance_metrics": financial_metrics.get("performance_metrics", {}),
                "investment_metrics": financial_metrics.get("investment_metrics", {}),
                "health_indicators": financial_metrics.get("health_indicators", {}),
                "overall_assessment": financial_metrics.get("overall_assessment", {})
            }
            
        except Exception as e:
            logger.error(f"Error creating metrics dashboard: {e}")
            dashboard = {"error": "Unable to generate metrics dashboard"}
        
        return dashboard
    
    def _create_investment_analysis(self, financial_data: Dict, financial_metrics: Dict, news_analysis: Dict) -> Dict[str, Any]:
        """Create investment analysis section"""
        investment_analysis = {}
        
        try:
            investment_grade = financial_metrics.get("overall_assessment", {}).get("investment_grade", "N/A")
            health_rating = financial_metrics.get("health_indicators", {}).get("health_rating", "Unknown")
            
            # Investment thesis
            thesis_points = []
            
            # Add positive factors
            strengths = financial_metrics.get("health_indicators", {}).get("key_strengths", [])
            for strength in strengths:
                thesis_points.append(f"Strength: {strength}")
            
            # Add growth factors
            growth_category = financial_metrics.get("growth_metrics", {}).get("growth_category", "Unknown")
            if growth_category not in ["Unknown", "Declining"]:
                thesis_points.append(f"Growth: {growth_category}")
            
            # Add market position
            market_position = financial_metrics.get("market_metrics", {}).get("market_position", "Unknown")
            if market_position not in ["Unknown"]:
                thesis_points.append(f"Market Position: {market_position}")
            
            investment_analysis = {
                "investment_recommendation": self._get_investment_recommendation(financial_metrics),
                "investment_grade": investment_grade,
                "financial_health_rating": health_rating,
                "investment_thesis": thesis_points,
                "key_value_drivers": self._identify_value_drivers(financial_data, financial_metrics, news_analysis),
                "risk_factors": financial_metrics.get("health_indicators", {}).get("key_weaknesses", []),
                "comparable_analysis": "Based on industry standards and similar companies",
                "exit_opportunities": self._assess_exit_opportunities(financial_data, financial_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error creating investment analysis: {e}")
            investment_analysis = {"error": "Unable to generate investment analysis"}
        
        return investment_analysis
    
    def _create_recommendations(self, financial_metrics: Dict, news_analysis: Dict) -> Dict[str, Any]:
        """Create recommendations and outlook section"""
        recommendations = {}
        
        try:
            # Strategic recommendations
            strategic_recs = []
            
            # Based on financial health
            health_score = financial_metrics.get("health_indicators", {}).get("financial_health_score", 0)
            if health_score < 40:
                strategic_recs.append("Focus on improving financial fundamentals and cash flow management")
            elif health_score < 60:
                strategic_recs.append("Strengthen market position and optimize operational efficiency")
            else:
                strategic_recs.append("Consider expansion opportunities and strategic partnerships")
            
            # Based on growth metrics
            growth_category = financial_metrics.get("growth_metrics", {}).get("growth_category", "Unknown")
            if growth_category == "High Growth":
                strategic_recs.append("Maintain growth trajectory while managing scalability challenges")
            elif growth_category == "Moderate Growth":
                strategic_recs.append("Identify new growth drivers and market opportunities")
            elif growth_category == "Slow Growth":
                strategic_recs.append("Reassess strategy and explore new business models")
            
            # Based on market sentiment
            sentiment_score = news_analysis.get("market_sentiment", {}).get("sentiment_score", 0.5)
            if sentiment_score > 0.7:
                strategic_recs.append("Capitalize on positive market sentiment for funding/partnerships")
            elif sentiment_score < 0.4:
                strategic_recs.append("Address negative market perception through improved communication")
            
            recommendations = {
                "strategic_recommendations": strategic_recs,
                "financial_priorities": self._get_financial_priorities(financial_metrics),
                "risk_mitigation": self._get_risk_mitigation_strategies(financial_metrics, news_analysis),
                "growth_opportunities": news_analysis.get("strategic_developments", {}).get("market_expansion", []),
                "outlook": {
                    "short_term": "Next 6 months outlook based on current trends",
                    "medium_term": "12-18 months outlook based on strategic initiatives",
                    "long_term": "2-3 years outlook based on market position and fundamentals"
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating recommendations: {e}")
            recommendations = {"error": "Unable to generate recommendations"}
        
        return recommendations
    
    def _get_investment_recommendation(self, financial_metrics: Dict) -> str:
        """Get investment recommendation based on metrics"""
        try:
            health_score = financial_metrics.get("health_indicators", {}).get("financial_health_score", 0)
            investment_grade = financial_metrics.get("overall_assessment", {}).get("investment_grade", "C")
            
            if health_score >= 80 and investment_grade in ["A", "B+"]:
                return "Strong Buy"
            elif health_score >= 60 and investment_grade in ["A", "B+", "B"]:
                return "Buy"
            elif health_score >= 40 and investment_grade in ["B", "B-"]:
                return "Hold"
            elif health_score >= 20:
                return "Cautious"
            else:
                return "Avoid"
                
        except Exception:
            return "Insufficient Data"
    
    def _identify_value_drivers(self, financial_data: Dict, financial_metrics: Dict, news_analysis: Dict) -> List[str]:
        """Identify key value drivers"""
        drivers = []
        
        try:
            # Revenue growth
            growth_rate = financial_data.get("revenue", {}).get("revenue_growth", {}).get("rate")
            if isinstance(growth_rate, (int, float)) and growth_rate > 20:
                drivers.append("Strong revenue growth")
            
            # Market position
            market_position = financial_metrics.get("market_metrics", {}).get("market_position", "Unknown")
            if market_position in ["market_leader", "strong"]:
                drivers.append("Strong market position")
            
            # Innovation
            innovation_focus = news_analysis.get("key_trends", {}).get("innovation_focus", [])
            if innovation_focus:
                drivers.append("Innovation and technology leadership")
            
            # Scalability
            revenue_per_employee = financial_metrics.get("performance_metrics", {}).get("revenue_per_employee", "N/A")
            if isinstance(revenue_per_employee, (int, float)) and revenue_per_employee > 200000:
                drivers.append("High operational efficiency")
            
        except Exception:
            drivers = ["Analysis pending"]
        
        return drivers
    
    def _assess_exit_opportunities(self, financial_data: Dict, financial_metrics: Dict) -> List[str]:
        """Assess potential exit opportunities"""
        opportunities = []
        
        try:
            valuation = financial_data.get("valuation", {}).get("current_valuation", {}).get("amount")
            health_score = financial_metrics.get("health_indicators", {}).get("financial_health_score", 0)
            
            if isinstance(valuation, (int, float)) and valuation > 1000000000:  # $1B+
                opportunities.append("IPO opportunity - unicorn status achieved")
            elif isinstance(valuation, (int, float)) and valuation > 100000000:  # $100M+
                opportunities.append("Strategic acquisition by larger industry player")
            
            if health_score > 70:
                opportunities.append("Private equity investment")
            
            if health_score > 50:
                opportunities.append("Management buyout potential")
                
        except Exception:
            opportunities = ["Assessment pending"]
        
        return opportunities
    
    def _get_financial_priorities(self, financial_metrics: Dict) -> List[str]:
        """Get financial priorities based on metrics"""
        priorities = []
        
        try:
            # Cash runway priority
            runway_risk = financial_metrics.get("risk_metrics", {}).get("runway_risk", "Unknown")
            if runway_risk in ["High", "Critical"]:
                priorities.append("Urgent: Extend cash runway through funding or revenue growth")
            
            # Profitability priority
            profitability = financial_metrics.get("performance_metrics", {}).get("profitability_status", "Unknown")
            if "loss" in profitability.lower():
                priorities.append("Achieve path to profitability")
            
            # Revenue growth priority
            growth_category = financial_metrics.get("growth_metrics", {}).get("growth_category", "Unknown")
            if growth_category in ["Slow Growth", "Declining"]:
                priorities.append("Accelerate revenue growth")
                
        except Exception:
            priorities = ["Comprehensive financial review needed"]
        
        return priorities
    
    def _get_risk_mitigation_strategies(self, financial_metrics: Dict, news_analysis: Dict) -> List[str]:
        """Get risk mitigation strategies"""
        strategies = []
        
        try:
            # Cash management
            runway_risk = financial_metrics.get("risk_metrics", {}).get("runway_risk", "Unknown")
            if runway_risk in ["High", "Critical"]:
                strategies.append("Implement strict cash management and consider bridge funding")
            
            # Market risks
            overall_risk = news_analysis.get("risk_assessment", {}).get("overall_risk_level", "unknown")
            if overall_risk in ["high", "critical"]:
                strategies.append("Diversify market exposure and strengthen competitive moats")
            
            # Operational risks
            competitive_threats = news_analysis.get("risk_assessment", {}).get("competitive_threats", [])
            if competitive_threats:
                strategies.append("Strengthen competitive position through innovation and partnerships")
                
        except Exception:
            strategies = ["Comprehensive risk assessment needed"]
        
        return strategies
    
    def _extract_data_sources(self, financial_data: Dict, news_analysis: Dict) -> List[str]:
        """Extract data sources used in the report"""
        sources = set()
        
        try:
            # Financial data sources
            fin_sources = financial_data.get("data_sources", [])
            sources.update(fin_sources)
            
            # News analysis sources
            # Inferred from search results and analysis
            sources.add("Web search results")
            sources.add("News analysis")
            sources.add("Financial data aggregation")
            
        except Exception:
            sources = {"Multiple web sources", "Financial databases", "News aggregation"}
        
        return list(sources)
    
    def _extract_confidence_scores(self, financial_data: Dict, news_analysis: Dict, financial_metrics: Dict) -> Dict[str, float]:
        """Extract confidence scores from various analyses"""
        scores = {}
        
        try:
            scores["financial_data"] = financial_data.get("overall_confidence", 0.0)
            scores["news_analysis"] = news_analysis.get("analysis_quality", {}).get("overall_confidence", 0.0)
            scores["company_info"] = financial_data.get("confidence_score", 0.0)  # From company info search
            
            # Calculate overall confidence
            available_scores = [score for score in scores.values() if score > 0]
            if available_scores:
                scores["overall_confidence"] = sum(available_scores) / len(available_scores)
            else:
                scores["overall_confidence"] = 0.0
                
        except Exception:
            scores = {"overall_confidence": 0.0}
        
        return scores
    
    def _assess_data_coverage(self, company_info: Dict, financial_data: Dict, news_analysis: Dict, financial_metrics: Dict) -> Dict[str, str]:
        """Assess coverage of different data categories"""
        coverage = {}
        
        try:
            # Company information coverage
            if company_info and company_info.get("company_name"):
                coverage["company_info"] = "Good" if company_info.get("confidence_score", 0) > 0.7 else "Fair"
            else:
                coverage["company_info"] = "Limited"
            
            # Financial data coverage
            if financial_data and financial_data.get("revenue", {}).get("annual_revenue", {}).get("amount"):
                coverage["financial_data"] = "Good"
            elif financial_data and financial_data.get("funding", {}).get("total_funding", {}).get("amount"):
                coverage["financial_data"] = "Fair"
            else:
                coverage["financial_data"] = "Limited"
            
            # Market analysis coverage
            if news_analysis and news_analysis.get("analysis_quality", {}).get("overall_confidence", 0) > 0.6:
                coverage["market_analysis"] = "Good"
            elif news_analysis:
                coverage["market_analysis"] = "Fair"
            else:
                coverage["market_analysis"] = "Limited"
            
            # Metrics coverage
            if financial_metrics and financial_metrics.get("health_indicators", {}).get("financial_health_score", 0) > 0:
                coverage["financial_metrics"] = "Good"
            else:
                coverage["financial_metrics"] = "Limited"
                
        except Exception:
            coverage = {"overall": "Limited"}
        
        return coverage
    
    def _format_currency(self, amount: float, currency: str = "USD") -> str:
        """Format currency amounts for display"""
        try:
            if amount >= 1_000_000_000:
                return f"${amount/1_000_000_000:.1f}B {currency}"
            elif amount >= 1_000_000:
                return f"${amount/1_000_000:.1f}M {currency}"
            elif amount >= 1_000:
                return f"${amount/1_000:.1f}K {currency}"
            else:
                return f"${amount:.0f} {currency}"
        except:
            return f"{amount} {currency}"
    
    def _generate_executive_summary(self, company_info: Dict, financial_data: Dict, news_analysis: Dict, financial_metrics: Dict) -> Dict[str, Any]:
        """Generate executive summary only report"""
        company_name = company_info.get("company_name", financial_data.get("company_name", "Unknown"))
        
        return {
            "report_type": "executive_summary",
            "company_name": company_name,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "executive_summary": self._create_executive_summary(company_info, financial_data, financial_metrics),
            "key_metrics": {
                "health_score": financial_metrics.get("health_indicators", {}).get("financial_health_score", 0),
                "investment_grade": financial_metrics.get("overall_assessment", {}).get("investment_grade", "N/A"),
                "growth_category": financial_metrics.get("growth_metrics", {}).get("growth_category", "Unknown")
            }
        }
    
    def _generate_metrics_report(self, financial_metrics: Dict, financial_data: Dict) -> Dict[str, Any]:
        """Generate metrics-only report"""
        company_name = financial_metrics.get("company_name", financial_data.get("company_name", "Unknown"))
        
        return {
            "report_type": "metrics_only",
            "company_name": company_name,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "financial_metrics": financial_metrics,
            "summary": {
                "health_score": financial_metrics.get("health_indicators", {}).get("financial_health_score", 0),
                "health_rating": financial_metrics.get("health_indicators", {}).get("health_rating", "Unknown"),
                "investment_grade": financial_metrics.get("overall_assessment", {}).get("investment_grade", "N/A")
            }
        }
    
    def _get_empty_report(self, company_name: str, report_type: str) -> Dict[str, Any]:
        """Return empty report structure"""
        return {
            "report_type": report_type,
            "company_name": company_name,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": "Unable to generate report due to insufficient data",
            "report_sections": {}
        }
    
    def post(self, shared: Dict[str, Any], prep_res: tuple, exec_res: Dict[str, Any]) -> str:
        """Store generated report in shared store"""
        logger.info(f"💾 FinancialReportGeneratorNode: post - Storing report for {exec_res.get('company_name', 'Unknown')}")
        
        shared["financial_report"] = exec_res
        
        # Also store in a more specific key for downstream nodes
        company_name = exec_res.get("company_name", "unknown")
        shared[f"{company_name.lower().replace(' ', '_')}_financial_report"] = exec_res
        
        # Extract report summary for easy access
        if exec_res.get("report_type") == "comprehensive":
            shared["report_summary"] = {
                "report_type": exec_res.get("report_type"),
                "sections_count": len(exec_res.get("report_sections", {})),
                "confidence": exec_res.get("report_metadata", {}).get("confidence_scores", {}).get("overall_confidence", 0.0),
                "data_coverage": exec_res.get("report_metadata", {}).get("data_coverage", {}),
                "investment_recommendation": exec_res.get("report_sections", {}).get("executive_summary", {}).get("investment_recommendation", "Unknown")
            }
        else:
            shared["report_summary"] = {
                "report_type": exec_res.get("report_type"),
                "status": "Generated"
            }
        
        logger.info(f"✅ FinancialReportGeneratorNode: Stored {exec_res.get('report_type', 'unknown')} report")
        
        return "default"