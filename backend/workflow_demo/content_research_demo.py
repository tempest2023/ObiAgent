#!/usr/bin/env python3
"""
Content Research Workflow Demo

This demo showcases content research and gathering using Google Arcade nodes:
1. Search Gmail for industry insights and discussions
2. Gather social media trends from LinkedIn and Twitter
3. Analyze and categorize findings
4. Generate research summary
5. Create content recommendations

Usage:
    python content_research_demo.py
    python content_research_demo.py --demo  # Demo mode (no real API calls)
"""

import sys
import os
import logging
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pocketflow import Flow, Node
from agent.function_nodes.gmail_arcade import GmailSearchEmailsNode, GmailAuthNode
from agent.function_nodes.x_arcade import XGetTweetsNode, XAuthNode
from agent.function_nodes.linkedin_arcade import LinkedInGetProfileNode, LinkedInAuthNode
from agent.function_nodes.gmail_arcade import GmailSendEmailNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Demo mode flag
DEMO_MODE = '--demo' in sys.argv

class ResearchTopicSetupNode(Node):
    """Set up research topic and parameters"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare research parameters"""
        return {
            "research_topic": shared.get("research_topic", "AI and Machine Learning"),
            "research_keywords": shared.get("research_keywords", ["AI", "machine learning", "artificial intelligence", "ML"]),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Set up research topic and search parameters"""
        logger.info(f"🔍 Setting up research for topic: {prep_res['research_topic']}")
        
        research_config = {
            "topic": prep_res["research_topic"],
            "keywords": prep_res["research_keywords"],
            "search_queries": {
                "gmail": f"subject:({' OR '.join(prep_res['research_keywords'])})",
                "twitter": f"#{prep_res['research_keywords'][0].replace(' ', '')}",
                "linkedin": prep_res["research_keywords"][0]
            },
            "research_scope": "industry_trends",
            "time_range": "last_30_days"
        }
        
        if prep_res["demo_mode"]:
            logger.info("🎭 DEMO: Research configuration set up")
        
        return research_config
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store research configuration"""
        shared["research_config"] = exec_res
        shared["search_query"] = exec_res["search_queries"]["gmail"]
        logger.info(f"📝 Research configured for: {exec_res['topic']}")
        return "research_configured"

class DemoGmailSearchEmailsNode(GmailSearchEmailsNode):
    """Gmail Search Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute email search with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, search_params = inputs
            logger.info(f"🎭 DEMO: Simulating Gmail search for '{search_params['query']}'")
            return [
                {
                    "id": "email_research_001",
                    "subject": "AI Industry Report Q4 2024",
                    "sender": "research@techreport.com",
                    "snippet": "The latest AI industry report shows significant growth in machine learning applications...",
                    "date": "2024-01-10",
                    "content": "AI market size reached $150B in 2024, with 45% growth in ML adoption...",
                    "demo": True
                },
                {
                    "id": "email_research_002",
                    "subject": "Machine Learning Conference Insights",
                    "sender": "conference@mlsummit.com",
                    "snippet": "Key takeaways from the ML Summit 2024 conference...",
                    "date": "2024-01-08",
                    "content": "Major breakthroughs in neural network architectures and transformer models...",
                    "demo": True
                },
                {
                    "id": "email_research_003",
                    "subject": "AI Ethics Discussion Panel",
                    "sender": "ethics@aiorganization.org",
                    "snippet": "Discussion on responsible AI development and ethical considerations...",
                    "date": "2024-01-05",
                    "content": "Important considerations for AI bias mitigation and fairness in algorithms...",
                    "demo": True
                }
            ]
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class DemoXGetTweetsNode(XGetTweetsNode):
    """X/Twitter Get Tweets Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute tweet retrieval with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, tweet_params = inputs
            logger.info(f"🎭 DEMO: Simulating Twitter search for AI trends")
            return [
                {
                    "id": "tweet_001",
                    "text": "🚀 Exciting developments in #AI this week! New transformer architecture shows 40% improvement in efficiency. The future of ML is here! #MachineLearning #TechNews",
                    "author": "ai_researcher",
                    "date": "2024-01-14",
                    "likes": 324,
                    "retweets": 156,
                    "demo": True
                },
                {
                    "id": "tweet_002",
                    "text": "Just published our latest paper on neural network optimization! 📊 Check out these amazing results in computer vision applications. #AI #Research #ComputerVision",
                    "author": "tech_labs",
                    "date": "2024-01-12",
                    "likes": 892,
                    "retweets": 234,
                    "demo": True
                },
                {
                    "id": "tweet_003",
                    "text": "The AI ethics debate is heating up! 🔥 Important discussions on bias, fairness, and responsible AI development. We need more diverse voices in this space. #AIEthics",
                    "author": "ethics_advocate",
                    "date": "2024-01-11",
                    "likes": 567,
                    "retweets": 189,
                    "demo": True
                }
            ]
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class DemoLinkedInGetProfileNode(LinkedInGetProfileNode):
    """LinkedIn Profile Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute LinkedIn profile retrieval with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, profile_params = inputs
            logger.info(f"🎭 DEMO: Simulating LinkedIn industry insights")
            return [
                {
                    "id": "linkedin_insight_001",
                    "author": "Dr. Sarah Chen",
                    "title": "AI Research Director at TechCorp",
                    "post": "Thrilled to share our latest breakthrough in natural language processing! Our new model achieves state-of-the-art results on multiple benchmarks. The implications for conversational AI are enormous.",
                    "date": "2024-01-13",
                    "likes": 1247,
                    "comments": 89,
                    "industry": "Technology",
                    "demo": True
                },
                {
                    "id": "linkedin_insight_002",
                    "author": "Michael Rodriguez",
                    "title": "ML Engineer at StartupAI",
                    "post": "Amazing conference at AI Summit 2024! Key trends I observed: 1) Multimodal AI is becoming mainstream 2) Edge computing for ML is gaining traction 3) Responsible AI practices are now table stakes",
                    "date": "2024-01-11",
                    "likes": 892,
                    "comments": 156,
                    "industry": "Technology",
                    "demo": True
                },
                {
                    "id": "linkedin_insight_003",
                    "author": "Lisa Wang",
                    "title": "AI Product Manager at InnovateTech",
                    "post": "The ROI of AI implementation is becoming clearer. Our latest study shows 60% of companies see positive returns within 12 months. The key is starting with well-defined use cases.",
                    "date": "2024-01-09",
                    "likes": 2156,
                    "comments": 234,
                    "industry": "Technology",
                    "demo": True
                }
            ]
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class ContentAnalysisNode(Node):
    """Analyze and categorize research findings"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare analysis parameters"""
        return {
            "gmail_results": shared.get("gmail_search_results", []),
            "twitter_results": shared.get("x_tweets_result", []),
            "linkedin_results": shared.get("linkedin_profile_result", []),
            "research_config": shared.get("research_config", {}),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Analyze content and extract insights"""
        logger.info("📊 Analyzing research findings...")
        
        analysis = {
            "topic": prep_res["research_config"].get("topic", "Unknown"),
            "total_sources": len(prep_res["gmail_results"]) + len(prep_res["twitter_results"]) + len(prep_res["linkedin_results"]),
            "sources_breakdown": {
                "email": len(prep_res["gmail_results"]),
                "twitter": len(prep_res["twitter_results"]),
                "linkedin": len(prep_res["linkedin_results"])
            },
            "key_themes": [],
            "trending_topics": [],
            "expert_opinions": [],
            "industry_insights": [],
            "content_opportunities": []
        }
        
        # Analyze email content
        for email in prep_res["gmail_results"]:
            if "industry report" in email.get("subject", "").lower():
                analysis["industry_insights"].append({
                    "source": "email",
                    "type": "industry_report",
                    "title": email.get("subject", ""),
                    "summary": email.get("snippet", "")
                })
            elif "conference" in email.get("subject", "").lower():
                analysis["expert_opinions"].append({
                    "source": "email",
                    "type": "conference_insights",
                    "title": email.get("subject", ""),
                    "summary": email.get("snippet", "")
                })
        
        # Analyze Twitter content
        for tweet in prep_res["twitter_results"]:
            if tweet.get("likes", 0) > 500:  # High engagement tweets
                analysis["trending_topics"].append({
                    "source": "twitter",
                    "content": tweet.get("text", ""),
                    "engagement": tweet.get("likes", 0),
                    "author": tweet.get("author", "")
                })
        
        # Analyze LinkedIn content
        for post in prep_res["linkedin_results"]:
            if post.get("likes", 0) > 1000:  # High engagement posts
                analysis["expert_opinions"].append({
                    "source": "linkedin",
                    "author": post.get("author", ""),
                    "title": post.get("title", ""),
                    "content": post.get("post", ""),
                    "engagement": post.get("likes", 0)
                })
        
        # Extract key themes
        common_themes = ["AI breakthrough", "machine learning", "neural networks", "ethics", "industry growth"]
        analysis["key_themes"] = [{"theme": theme, "frequency": "high"} for theme in common_themes[:3]]
        
        # Generate content opportunities
        analysis["content_opportunities"] = [
            {
                "type": "blog_post",
                "title": f"The Future of {prep_res['research_config'].get('topic', 'AI')}: 2024 Insights",
                "description": "Comprehensive analysis of current trends and future predictions",
                "priority": "high"
            },
            {
                "type": "whitepaper",
                "title": f"{prep_res['research_config'].get('topic', 'AI')} Industry Report",
                "description": "In-depth research findings and expert opinions",
                "priority": "medium"
            },
            {
                "type": "social_media_series",
                "title": "Weekly AI Insights",
                "description": "Regular updates on trending topics and breakthroughs",
                "priority": "high"
            }
        ]
        
        if prep_res["demo_mode"]:
            logger.info("🎭 DEMO: Content analysis completed")
        
        return analysis
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store analysis results"""
        shared["content_analysis"] = exec_res
        
        # Log analysis summary
        logger.info("📈 Content Analysis Summary:")
        logger.info(f"   Total Sources: {exec_res['total_sources']}")
        logger.info(f"   Key Themes: {len(exec_res['key_themes'])}")
        logger.info(f"   Trending Topics: {len(exec_res['trending_topics'])}")
        logger.info(f"   Expert Opinions: {len(exec_res['expert_opinions'])}")
        logger.info(f"   Content Opportunities: {len(exec_res['content_opportunities'])}")
        
        return "analysis_complete"

class ResearchReportGeneratorNode(Node):
    """Generate comprehensive research report"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare report generation parameters"""
        return {
            "content_analysis": shared.get("content_analysis", {}),
            "research_config": shared.get("research_config", {}),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Generate comprehensive research report"""
        logger.info("📋 Generating research report...")
        
        analysis = prep_res["content_analysis"]
        config = prep_res["research_config"]
        
        report = {
            "title": f"Content Research Report: {config.get('topic', 'Unknown Topic')}",
            "date": "2024-01-15",
            "executive_summary": f"""
This report presents comprehensive research findings on {config.get('topic', 'the specified topic')} 
based on analysis of {analysis.get('total_sources', 0)} sources across email, social media, 
and industry platforms.

Key findings indicate strong growth and innovation in this space, with significant opportunities 
for content creation and thought leadership.
""",
            "methodology": {
                "data_sources": ["Gmail search", "Twitter analysis", "LinkedIn insights"],
                "search_keywords": config.get("keywords", []),
                "time_range": config.get("time_range", "last_30_days"),
                "total_sources_analyzed": analysis.get("total_sources", 0)
            },
            "key_findings": {
                "trending_themes": analysis.get("key_themes", []),
                "industry_insights": analysis.get("industry_insights", []),
                "expert_opinions": analysis.get("expert_opinions", []),
                "social_media_trends": analysis.get("trending_topics", [])
            },
            "recommendations": {
                "content_opportunities": analysis.get("content_opportunities", []),
                "next_steps": [
                    "Develop content calendar based on trending topics",
                    "Reach out to identified experts for interviews",
                    "Monitor social media for emerging trends",
                    "Schedule follow-up research in 30 days"
                ]
            },
            "appendices": {
                "sources_breakdown": analysis.get("sources_breakdown", {}),
                "research_configuration": config
            }
        }
        
        if prep_res["demo_mode"]:
            logger.info("🎭 DEMO: Research report generated")
        
        return report
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store research report"""
        shared["research_report"] = exec_res
        
        # Prepare email summary
        shared["recipient"] = "research-team@company.com"
        shared["subject"] = exec_res["title"]
        shared["body"] = f"""Dear Research Team,

I've completed the content research analysis for {exec_res['title']}.

## Executive Summary
{exec_res['executive_summary']}

## Key Metrics
- Total Sources Analyzed: {exec_res['methodology']['total_sources_analyzed']}
- Key Themes Identified: {len(exec_res['key_findings']['trending_themes'])}
- Content Opportunities: {len(exec_res['recommendations']['content_opportunities'])}

## Top Recommendations
{chr(10).join(['• ' + opp['title'] for opp in exec_res['recommendations']['content_opportunities'][:3]])}

## Next Steps
{chr(10).join(['• ' + step for step in exec_res['recommendations']['next_steps']])}

The complete research report is attached for your review.

Best regards,
Content Research Team

---
This report was generated through our automated content research workflow.
"""
        
        logger.info("🎉 Content Research Workflow completed successfully!")
        return "report_complete"

class DemoGmailSendEmailNode(GmailSendEmailNode):
    """Gmail Send Email Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute email sending with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, email_params = inputs
            logger.info(f"🎭 DEMO: Simulating research report email to {email_params['recipient']}")
            return {
                "message_id": "demo_research_report_email",
                "status": "sent",
                "demo": True
            }
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

def create_content_research_workflow():
    """Create and return the content research workflow"""
    
    # Create nodes
    research_setup = ResearchTopicSetupNode()
    gmail_search = DemoGmailSearchEmailsNode()
    twitter_search = DemoXGetTweetsNode()
    linkedin_search = DemoLinkedInGetProfileNode()
    content_analysis = ContentAnalysisNode()
    report_generator = ResearchReportGeneratorNode()
    email_sender = DemoGmailSendEmailNode()
    
    # Connect nodes - setup first, then parallel searches, then analysis, then report
    research_setup >> gmail_search
    research_setup >> twitter_search
    research_setup >> linkedin_search
    
    # All searches connect to content analysis
    gmail_search >> content_analysis
    twitter_search >> content_analysis
    linkedin_search >> content_analysis
    
    # Analysis connects to report generation, then email
    content_analysis >> report_generator >> email_sender
    
    # Create flow
    return Flow(start=research_setup)

def main():
    """Main function to run the content research demo"""
    print("🎭 Content Research Workflow Demo")
    print("=" * 50)
    
    if DEMO_MODE:
        print("🎪 Running in DEMO MODE")
        print("   No real API calls will be made")
    else:
        print("🔴 Running in LIVE MODE")
        print("   Real research API calls will be made")
        print("   Make sure ARCADE_API_KEY is set!")
    
    print()
    
    # Create shared store
    shared = {
        "demo_mode": DEMO_MODE,
        "user_id": "research_agent_123",
        "research_topic": "Artificial Intelligence and Machine Learning",
        "research_keywords": ["AI", "machine learning", "artificial intelligence", "ML", "neural networks"],
        # These will be populated by the workflow
        "research_config": {},
        "search_query": "",
        "gmail_search_results": [],
        "x_tweets_result": [],
        "linkedin_profile_result": [],
        "content_analysis": {},
        "research_report": {}
    }
    
    try:
        # Create and run the workflow
        workflow = create_content_research_workflow()
        result = workflow.run(shared)
        
        print("\n📋 Final Results:")
        print(f"   Workflow Action: {result}")
        
        if "research_report" in shared:
            report = shared["research_report"]
            print(f"   Report Title: {report['title']}")
            print(f"   Sources Analyzed: {report['methodology']['total_sources_analyzed']}")
            print(f"   Key Themes: {len(report['key_findings']['trending_themes'])}")
            print(f"   Content Opportunities: {len(report['recommendations']['content_opportunities'])}")
            
            # Show top content opportunities
            if report['recommendations']['content_opportunities']:
                print("\n📊 Top Content Opportunities:")
                for i, opp in enumerate(report['recommendations']['content_opportunities'][:3], 1):
                    print(f"   {i}. {opp['title']} ({opp['type']})")
            
            # Show next steps
            if report['recommendations']['next_steps']:
                print("\n🎯 Next Steps:")
                for i, step in enumerate(report['recommendations']['next_steps'][:3], 1):
                    print(f"   {i}. {step}")
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())