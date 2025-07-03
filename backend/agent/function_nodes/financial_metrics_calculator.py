from pocketflow import Node
from typing import Dict, List, Any, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class FinancialMetricsCalculatorNode(Node):
    """
    Node to calculate financial metrics and ratios from collected financial data.
    Computes key performance indicators, valuation metrics, and growth rates.
    
    Example:
        >>> node = FinancialMetricsCalculatorNode()
        >>> shared = {"financial_data": {...}, "company_info": {...}}
        >>> node.prep(shared)
        # Returns financial data and company context
        >>> node.exec((financial_data, company_info))
        # Returns calculated financial metrics
    """
    
    def prep(self, shared: Dict[str, Any]) -> tuple:
        """Prepare financial data and company information for metrics calculation"""
        financial_data = shared.get("financial_data", {})
        company_info = shared.get("company_info", {})
        news_analysis = shared.get("news_analysis", {})
        
        logger.info(f"🔄 FinancialMetricsCalculatorNode: prep - company='{financial_data.get('company_name', 'Unknown')}'")
        
        if not financial_data:
            logger.warning("⚠️ FinancialMetricsCalculatorNode: No financial data available")
            
        return financial_data, company_info, news_analysis
    
    def exec(self, inputs: tuple) -> Dict[str, Any]:
        """Calculate financial metrics and ratios"""
        financial_data, company_info, news_analysis = inputs
        
        company_name = financial_data.get("company_name", "Unknown")
        logger.info(f"🔄 FinancialMetricsCalculatorNode: exec - calculating metrics for {company_name}")
        
        if not financial_data:
            logger.warning("⚠️ FinancialMetricsCalculatorNode: No financial data to process")
            return self._get_empty_metrics(company_name)
        
        try:
            # Extract key financial data
            revenue_data = financial_data.get("revenue", {})
            funding_data = financial_data.get("funding", {})
            valuation_data = financial_data.get("valuation", {})
            metrics_data = financial_data.get("financial_metrics", {})
            
            # Calculate metrics
            calculated_metrics = {
                "company_name": company_name,
                "calculation_date": datetime.now().strftime("%Y-%m-%d"),
                
                # Valuation Metrics
                "valuation_metrics": self._calculate_valuation_metrics(valuation_data, revenue_data, funding_data),
                
                # Growth Metrics
                "growth_metrics": self._calculate_growth_metrics(revenue_data, funding_data, news_analysis),
                
                # Performance Metrics
                "performance_metrics": self._calculate_performance_metrics(revenue_data, metrics_data, company_info),
                
                # Investment Metrics
                "investment_metrics": self._calculate_investment_metrics(funding_data, valuation_data),
                
                # Risk Metrics
                "risk_metrics": self._calculate_risk_metrics(metrics_data, news_analysis, funding_data),
                
                # Market Position Metrics
                "market_metrics": self._calculate_market_metrics(company_info, news_analysis, valuation_data),
                
                # Financial Health Indicators
                "health_indicators": self._calculate_health_indicators(funding_data, metrics_data, revenue_data),
                
                # Overall Assessment
                "overall_assessment": self._calculate_overall_assessment(financial_data, company_info, news_analysis)
            }
            
            logger.info("✅ FinancialMetricsCalculatorNode: Successfully calculated financial metrics")
            return calculated_metrics
            
        except Exception as e:
            logger.error(f"❌ FinancialMetricsCalculatorNode: Error calculating metrics: {e}")
            return self._get_empty_metrics(company_name)
    
    def _calculate_valuation_metrics(self, valuation_data: Dict, revenue_data: Dict, funding_data: Dict) -> Dict[str, Any]:
        """Calculate valuation-related metrics"""
        metrics = {}
        
        try:
            # Current valuation
            current_val = valuation_data.get("current_valuation", {})
            if isinstance(current_val.get("amount"), (int, float)) and current_val["amount"] > 0:
                valuation_amount = current_val["amount"]
                
                # Price-to-Revenue ratio (if revenue available)
                revenue_amount = revenue_data.get("annual_revenue", {}).get("amount")
                if isinstance(revenue_amount, (int, float)) and revenue_amount > 0:
                    metrics["price_to_revenue_ratio"] = round(valuation_amount / revenue_amount, 2)
                else:
                    metrics["price_to_revenue_ratio"] = "Not Available"
                
                # Valuation per funding dollar
                total_funding = funding_data.get("total_funding", {}).get("amount")
                if isinstance(total_funding, (int, float)) and total_funding > 0:
                    metrics["valuation_to_funding_ratio"] = round(valuation_amount / total_funding, 2)
                else:
                    metrics["valuation_to_funding_ratio"] = "Not Available"
                
                metrics["current_valuation"] = valuation_amount
            else:
                metrics["current_valuation"] = "Not Available"
                metrics["price_to_revenue_ratio"] = "Not Available"
                metrics["valuation_to_funding_ratio"] = "Not Available"
                
        except Exception as e:
            logger.error(f"Error calculating valuation metrics: {e}")
            metrics = {"current_valuation": "Error", "price_to_revenue_ratio": "Error"}
        
        return metrics
    
    def _calculate_growth_metrics(self, revenue_data: Dict, funding_data: Dict, news_analysis: Dict) -> Dict[str, Any]:
        """Calculate growth-related metrics"""
        metrics = {}
        
        try:
            # Revenue growth rate
            growth_rate = revenue_data.get("revenue_growth", {}).get("rate")
            if isinstance(growth_rate, (int, float)):
                metrics["revenue_growth_rate"] = f"{growth_rate}%"
                metrics["growth_category"] = (
                    "High Growth" if growth_rate > 50 else
                    "Moderate Growth" if growth_rate > 20 else
                    "Slow Growth" if growth_rate > 0 else
                    "Declining"
                )
            else:
                metrics["revenue_growth_rate"] = "Not Available"
                metrics["growth_category"] = "Unknown"
            
            # Funding momentum
            funding_history = funding_data.get("funding_history", [])
            if len(funding_history) >= 2:
                recent_rounds = sorted(funding_history, key=lambda x: x.get("date", ""), reverse=True)[:2]
                if len(recent_rounds) == 2:
                    latest_amount = recent_rounds[0].get("amount", 0)
                    previous_amount = recent_rounds[1].get("amount", 0)
                    if isinstance(latest_amount, (int, float)) and isinstance(previous_amount, (int, float)) and previous_amount > 0:
                        funding_growth = ((latest_amount - previous_amount) / previous_amount) * 100
                        metrics["funding_round_growth"] = f"{round(funding_growth, 1)}%"
                    else:
                        metrics["funding_round_growth"] = "Not Available"
                else:
                    metrics["funding_round_growth"] = "Insufficient Data"
            else:
                metrics["funding_round_growth"] = "Limited Funding History"
            
            # Market momentum from news
            news_impact = news_analysis.get("financial_impact", {}).get("revenue_impact", {}).get("impact_score", 0.5)
            metrics["market_momentum_score"] = round(news_impact * 100, 1)
            
        except Exception as e:
            logger.error(f"Error calculating growth metrics: {e}")
            metrics = {"revenue_growth_rate": "Error", "growth_category": "Error"}
        
        return metrics
    
    def _calculate_performance_metrics(self, revenue_data: Dict, metrics_data: Dict, company_info: Dict) -> Dict[str, Any]:
        """Calculate performance-related metrics"""
        metrics = {}
        
        try:
            # Revenue efficiency
            revenue_amount = revenue_data.get("annual_revenue", {}).get("amount")
            employee_count = company_info.get("employee_count")
            
            if isinstance(revenue_amount, (int, float)) and isinstance(employee_count, (int, float)) and employee_count > 0:
                revenue_per_employee = revenue_amount / employee_count
                metrics["revenue_per_employee"] = round(revenue_per_employee, 0)
            else:
                metrics["revenue_per_employee"] = "Not Available"
            
            # Profitability status
            profitability = metrics_data.get("profitability", {}).get("status", "Unknown")
            metrics["profitability_status"] = profitability
            
            # Revenue diversification (based on revenue sources)
            revenue_sources = revenue_data.get("revenue_sources", [])
            metrics["revenue_diversification"] = (
                "High" if len(revenue_sources) >= 3 else
                "Moderate" if len(revenue_sources) == 2 else
                "Low" if len(revenue_sources) == 1 else
                "Unknown"
            )
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            metrics = {"revenue_per_employee": "Error", "profitability_status": "Error"}
        
        return metrics
    
    def _calculate_investment_metrics(self, funding_data: Dict, valuation_data: Dict) -> Dict[str, Any]:
        """Calculate investment-related metrics"""
        metrics = {}
        
        try:
            total_funding = funding_data.get("total_funding", {}).get("amount")
            current_valuation = valuation_data.get("current_valuation", {}).get("amount")
            
            # Capital efficiency
            if isinstance(total_funding, (int, float)) and isinstance(current_valuation, (int, float)) and total_funding > 0:
                capital_efficiency = current_valuation / total_funding
                metrics["capital_efficiency_ratio"] = round(capital_efficiency, 2)
                metrics["capital_efficiency_rating"] = (
                    "Excellent" if capital_efficiency > 10 else
                    "Good" if capital_efficiency > 5 else
                    "Average" if capital_efficiency > 2 else
                    "Poor"
                )
            else:
                metrics["capital_efficiency_ratio"] = "Not Available"
                metrics["capital_efficiency_rating"] = "Unknown"
            
            # Funding stage analysis
            latest_round = funding_data.get("latest_round", {})
            round_type = latest_round.get("type", "Unknown")
            metrics["funding_stage"] = round_type
            
            # Investment attractiveness
            funding_history = funding_data.get("funding_history", [])
            metrics["total_funding_rounds"] = len(funding_history)
            metrics["investment_track_record"] = (
                "Strong" if len(funding_history) >= 3 else
                "Moderate" if len(funding_history) == 2 else
                "Early Stage" if len(funding_history) == 1 else
                "Unknown"
            )
            
        except Exception as e:
            logger.error(f"Error calculating investment metrics: {e}")
            metrics = {"capital_efficiency_ratio": "Error", "funding_stage": "Error"}
        
        return metrics
    
    def _calculate_risk_metrics(self, metrics_data: Dict, news_analysis: Dict, funding_data: Dict) -> Dict[str, Any]:
        """Calculate risk-related metrics"""
        metrics = {}
        
        try:
            # Burn rate analysis
            burn_rate = metrics_data.get("burn_rate", {})
            monthly_burn = burn_rate.get("monthly_burn")
            runway_months = burn_rate.get("runway_months")
            
            if runway_months and isinstance(runway_months, (int, float)):
                metrics["cash_runway"] = f"{runway_months} months"
                metrics["runway_risk"] = (
                    "Low" if runway_months > 24 else
                    "Moderate" if runway_months > 12 else
                    "High" if runway_months > 6 else
                    "Critical"
                )
            else:
                metrics["cash_runway"] = "Not Available"
                metrics["runway_risk"] = "Unknown"
            
            # Market risk from news analysis
            overall_risk = news_analysis.get("risk_assessment", {}).get("overall_risk_level", "unknown")
            metrics["market_risk_level"] = overall_risk
            
            # Funding dependency
            total_funding = funding_data.get("total_funding", {}).get("amount", 0)
            if isinstance(total_funding, (int, float)):
                if total_funding > 100000000:  # $100M+
                    metrics["funding_dependency"] = "High"
                elif total_funding > 10000000:  # $10M+
                    metrics["funding_dependency"] = "Moderate"
                else:
                    metrics["funding_dependency"] = "Low"
            else:
                metrics["funding_dependency"] = "Unknown"
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            metrics = {"cash_runway": "Error", "market_risk_level": "Error"}
        
        return metrics
    
    def _calculate_market_metrics(self, company_info: Dict, news_analysis: Dict, valuation_data: Dict) -> Dict[str, Any]:
        """Calculate market-related metrics"""
        metrics = {}
        
        try:
            # Market position
            market_position = news_analysis.get("key_trends", {}).get("market_position", {})
            metrics["market_position"] = market_position.get("current_position", "Unknown")
            metrics["position_trend"] = market_position.get("position_trend", "stable")
            
            # Industry assessment
            industry = company_info.get("industry", "Unknown")
            metrics["industry"] = industry
            
            # Competitive strength
            key_differentiators = market_position.get("key_differentiators", [])
            metrics["competitive_advantages"] = len(key_differentiators)
            metrics["competitive_strength"] = (
                "Strong" if len(key_differentiators) >= 3 else
                "Moderate" if len(key_differentiators) >= 2 else
                "Weak" if len(key_differentiators) >= 1 else
                "Unknown"
            )
            
            # Market sentiment
            sentiment_score = news_analysis.get("market_sentiment", {}).get("sentiment_score", 0.5)
            metrics["market_sentiment_score"] = round(sentiment_score * 100, 1)
            
        except Exception as e:
            logger.error(f"Error calculating market metrics: {e}")
            metrics = {"market_position": "Error", "industry": "Error"}
        
        return metrics
    
    def _calculate_health_indicators(self, funding_data: Dict, metrics_data: Dict, revenue_data: Dict) -> Dict[str, Any]:
        """Calculate overall financial health indicators"""
        indicators = {}
        
        try:
            # Overall health score (0-100)
            health_factors = []
            
            # Factor 1: Revenue availability and growth
            revenue_amount = revenue_data.get("annual_revenue", {}).get("amount")
            if isinstance(revenue_amount, (int, float)) and revenue_amount > 0:
                health_factors.append(25)  # Has revenue
                growth_rate = revenue_data.get("revenue_growth", {}).get("rate", 0)
                if isinstance(growth_rate, (int, float)) and growth_rate > 0:
                    health_factors.append(15)  # Positive growth
            
            # Factor 2: Funding status
            total_funding = funding_data.get("total_funding", {}).get("amount")
            if isinstance(total_funding, (int, float)) and total_funding > 0:
                health_factors.append(20)  # Has funding
            
            # Factor 3: Profitability
            profitability = metrics_data.get("profitability", {}).get("status", "Unknown")
            if "profitable" in profitability.lower():
                health_factors.append(25)
            elif "break-even" in profitability.lower():
                health_factors.append(15)
            
            # Factor 4: Cash runway
            runway_months = metrics_data.get("burn_rate", {}).get("runway_months")
            if isinstance(runway_months, (int, float)):
                if runway_months > 18:
                    health_factors.append(15)
                elif runway_months > 6:
                    health_factors.append(10)
            
            health_score = sum(health_factors)
            indicators["financial_health_score"] = health_score
            indicators["health_rating"] = (
                "Excellent" if health_score >= 80 else
                "Good" if health_score >= 60 else
                "Fair" if health_score >= 40 else
                "Poor" if health_score >= 20 else
                "Critical"
            )
            
            # Key strengths and weaknesses
            strengths = []
            weaknesses = []
            
            if revenue_amount and isinstance(revenue_amount, (int, float)) and revenue_amount > 0:
                strengths.append("Revenue generating")
            else:
                weaknesses.append("No clear revenue")
            
            if profitability and "profitable" in profitability.lower():
                strengths.append("Profitable operations")
            else:
                weaknesses.append("Not yet profitable")
            
            if total_funding and isinstance(total_funding, (int, float)) and total_funding > 50000000:
                strengths.append("Well-funded")
            elif not total_funding:
                weaknesses.append("Limited funding information")
            
            indicators["key_strengths"] = strengths
            indicators["key_weaknesses"] = weaknesses
            
        except Exception as e:
            logger.error(f"Error calculating health indicators: {e}")
            indicators = {"financial_health_score": 0, "health_rating": "Error"}
        
        return indicators
    
    def _calculate_overall_assessment(self, financial_data: Dict, company_info: Dict, news_analysis: Dict) -> Dict[str, Any]:
        """Calculate overall financial assessment"""
        assessment = {}
        
        try:
            # Investment grade
            valuation = financial_data.get("valuation", {}).get("current_valuation", {}).get("amount")
            revenue = financial_data.get("revenue", {}).get("annual_revenue", {}).get("amount")
            funding = financial_data.get("funding", {}).get("total_funding", {}).get("amount")
            
            grade_factors = 0
            if isinstance(valuation, (int, float)) and valuation > 1000000000:  # $1B+ valuation
                grade_factors += 2
            elif isinstance(valuation, (int, float)) and valuation > 100000000:  # $100M+ valuation
                grade_factors += 1
            
            if isinstance(revenue, (int, float)) and revenue > 100000000:  # $100M+ revenue
                grade_factors += 2
            elif isinstance(revenue, (int, float)) and revenue > 10000000:  # $10M+ revenue
                grade_factors += 1
            
            if isinstance(funding, (int, float)) and funding > 100000000:  # $100M+ funding
                grade_factors += 1
            
            # Market sentiment factor
            sentiment_score = news_analysis.get("market_sentiment", {}).get("sentiment_score", 0.5)
            if sentiment_score > 0.7:
                grade_factors += 1
            elif sentiment_score < 0.3:
                grade_factors -= 1
            
            investment_grade = (
                "A" if grade_factors >= 5 else
                "B+" if grade_factors >= 4 else
                "B" if grade_factors >= 3 else
                "B-" if grade_factors >= 2 else
                "C+" if grade_factors >= 1 else
                "C"
            )
            
            assessment["investment_grade"] = investment_grade
            assessment["grade_factors_score"] = grade_factors
            
            # Key insights
            insights = []
            if isinstance(revenue, (int, float)) and revenue > 0:
                growth_rate = financial_data.get("revenue", {}).get("revenue_growth", {}).get("rate", 0)
                if isinstance(growth_rate, (int, float)) and growth_rate > 30:
                    insights.append("Strong revenue growth momentum")
                elif isinstance(growth_rate, (int, float)) and growth_rate > 0:
                    insights.append("Positive revenue growth")
                else:
                    insights.append("Revenue growth data limited")
            else:
                insights.append("Revenue data not available")
            
            if isinstance(valuation, (int, float)) and isinstance(revenue, (int, float)) and revenue > 0:
                p_r_ratio = valuation / revenue
                if p_r_ratio > 20:
                    insights.append("High valuation multiple")
                elif p_r_ratio > 10:
                    insights.append("Moderate valuation multiple")
                else:
                    insights.append("Conservative valuation")
            
            assessment["key_insights"] = insights[:5]  # Limit to top 5 insights
            
        except Exception as e:
            logger.error(f"Error calculating overall assessment: {e}")
            assessment = {"investment_grade": "Error", "grade_factors_score": 0}
        
        return assessment
    
    def _get_empty_metrics(self, company_name: str) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            "company_name": company_name,
            "calculation_date": datetime.now().strftime("%Y-%m-%d"),
            "valuation_metrics": {"current_valuation": "Not Available"},
            "growth_metrics": {"revenue_growth_rate": "Not Available"},
            "performance_metrics": {"profitability_status": "Unknown"},
            "investment_metrics": {"funding_stage": "Unknown"},
            "risk_metrics": {"market_risk_level": "Unknown"},
            "market_metrics": {"market_position": "Unknown"},
            "health_indicators": {"financial_health_score": 0, "health_rating": "Unknown"},
            "overall_assessment": {"investment_grade": "N/A", "key_insights": []}
        }
    
    def post(self, shared: Dict[str, Any], prep_res: tuple, exec_res: Dict[str, Any]) -> str:
        """Store calculated metrics in shared store"""
        logger.info(f"💾 FinancialMetricsCalculatorNode: post - Storing metrics for {exec_res.get('company_name', 'Unknown')}")
        
        shared["financial_metrics_calculated"] = exec_res
        
        # Also store in a more specific key for downstream nodes
        company_name = exec_res.get("company_name", "unknown")
        shared[f"{company_name.lower().replace(' ', '_')}_financial_metrics"] = exec_res
        
        # Extract summary metrics for easy access
        shared["financial_summary"] = {
            "health_score": exec_res.get("health_indicators", {}).get("financial_health_score", 0),
            "health_rating": exec_res.get("health_indicators", {}).get("health_rating", "Unknown"),
            "investment_grade": exec_res.get("overall_assessment", {}).get("investment_grade", "N/A"),
            "growth_category": exec_res.get("growth_metrics", {}).get("growth_category", "Unknown"),
            "market_position": exec_res.get("market_metrics", {}).get("market_position", "Unknown")
        }
        
        health_score = exec_res.get("health_indicators", {}).get("financial_health_score", 0)
        logger.info(f"✅ FinancialMetricsCalculatorNode: Stored metrics with health score: {health_score}")
        
        return "default"