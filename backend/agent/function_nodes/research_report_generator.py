from pocketflow import Node
from typing import Dict, List, Any, Optional
from agent.utils.stream_llm import call_llm
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ResearchReportGeneratorNode(Node):
    """
    Node to generate structured research reports from synthesized findings with proper citations.
    Creates comprehensive, well-formatted reports suitable for various audiences and purposes.
    
    Example:
        >>> node = ResearchReportGeneratorNode()
        >>> shared = {"research_synthesis": {...}, "citations": {...}}
        >>> node.prep(shared)
        # Returns (synthesis, citations, report_config)
        >>> node.exec((...))
        # Returns comprehensive research report with citations and recommendations
    """
    
    def prep(self, shared: Dict[str, Any]) -> tuple:
        """Prepare synthesis results and citations for report generation"""
        research_synthesis = shared.get("research_synthesis", {})
        citations = shared.get("citations", {})
        research_metadata = shared.get("research_metadata", {})
        report_config = shared.get("report_config", {})
        main_question = shared.get("research_question", "")
        
        # Set default report configuration
        default_config = {
            "report_type": "comprehensive",  # comprehensive, executive, academic, brief
            "target_audience": "general",    # general, academic, executive, technical
            "include_methodology": True,
            "include_limitations": True,
            "include_recommendations": True,
            "citation_style": "apa",
            "max_length": "standard"         # brief, standard, extended
        }
        
        # Merge with provided config
        report_config = {**default_config, **report_config}
        
        logger.info(f"🔄 ResearchReportGeneratorNode: prep - generating {report_config['report_type']} report")
        
        if not research_synthesis:
            logger.warning("⚠️ ResearchReportGeneratorNode: No research synthesis provided")
            
        return research_synthesis, citations, research_metadata, report_config, main_question
    
    def exec(self, inputs: tuple) -> Dict[str, Any]:
        """Generate comprehensive research report from synthesis and citations"""
        research_synthesis, citations, research_metadata, report_config, main_question = inputs
        
        report_type = report_config.get("report_type", "comprehensive")
        target_audience = report_config.get("target_audience", "general")
        
        logger.info(f"🔄 ResearchReportGeneratorNode: exec - generating {report_type} report for {target_audience} audience")
        
        if not research_synthesis:
            logger.warning("⚠️ ResearchReportGeneratorNode: No synthesis data for report generation")
            return self._get_empty_report(main_question, report_config)
        
        # Prepare citation lookup for easy referencing
        citation_lookup = self._prepare_citation_lookup(citations)
        
        # Prepare structured data for report generation
        structured_content = self._prepare_structured_content(research_synthesis, citations, research_metadata)
        
        # Generate report based on type and audience
        prompt = f"""
You are a research report writer specializing in creating comprehensive, well-structured reports from research findings.

Research Question: "{main_question}"
Report Type: {report_type}
Target Audience: {target_audience}
Citation Style: {report_config.get('citation_style', 'apa')}

Research Data:
{structured_content}

Available Citations: {len(citation_lookup)} sources available for referencing

Please generate a comprehensive research report:

1. Create a well-structured report appropriate for the target audience
2. Include proper in-text citations using available sources
3. Organize content logically with clear sections and subsections
4. Provide evidence-based conclusions and insights
5. Include methodology, limitations, and recommendations as configured
6. Ensure academic rigor and professional presentation

Report Configuration:
- Include Methodology: {report_config.get('include_methodology', True)}
- Include Limitations: {report_config.get('include_limitations', True)}
- Include Recommendations: {report_config.get('include_recommendations', True)}
- Length: {report_config.get('max_length', 'standard')}

Output your report in JSON format:
```json
{{
    "report_metadata": {{
        "title": "Research Report Title",
        "research_question": "{main_question}",
        "report_type": "{report_type}",
        "target_audience": "{target_audience}",
        "generation_date": "{datetime.now().isoformat()}",
        "word_count_estimate": 0,
        "section_count": 0,
        "citation_count": 0
    }},
    "executive_summary": {{
        "key_question": "{main_question}",
        "primary_findings": "Main findings summary",
        "key_insights": ["Insight 1", "Insight 2", "Insight 3"],
        "main_conclusions": "Primary conclusions",
        "recommendations_summary": "Brief recommendations overview",
        "confidence_assessment": "high|medium|low"
    }},
    "report_sections": [
        {{
            "section_id": "introduction",
            "section_title": "Introduction",
            "section_number": 1,
            "content": "Section content with proper citations",
            "subsections": [
                {{
                    "subsection_title": "Background",
                    "content": "Subsection content"
                }}
            ],
            "citations_used": ["citation_id_1", "citation_id_2"],
            "word_count": 0
        }},
        {{
            "section_id": "methodology",
            "section_title": "Research Methodology",
            "section_number": 2,
            "content": "Methodology description",
            "subsections": [],
            "citations_used": [],
            "word_count": 0
        }},
        {{
            "section_id": "findings",
            "section_title": "Research Findings",
            "section_number": 3,
            "content": "Detailed findings with citations",
            "subsections": [
                {{
                    "subsection_title": "Key Finding 1",
                    "content": "Finding details with evidence"
                }}
            ],
            "citations_used": ["citation_id_3", "citation_id_4"],
            "word_count": 0
        }},
        {{
            "section_id": "analysis",
            "section_title": "Analysis and Discussion",
            "section_number": 4,
            "content": "Analysis of findings",
            "subsections": [],
            "citations_used": [],
            "word_count": 0
        }},
        {{
            "section_id": "conclusions",
            "section_title": "Conclusions",
            "section_number": 5,
            "content": "Conclusions and implications",
            "subsections": [],
            "citations_used": [],
            "word_count": 0
        }},
        {{
            "section_id": "recommendations",
            "section_title": "Recommendations",
            "section_number": 6,
            "content": "Actionable recommendations",
            "subsections": [],
            "citations_used": [],
            "word_count": 0
        }},
        {{
            "section_id": "limitations",
            "section_title": "Limitations and Future Research",
            "section_number": 7,
            "content": "Research limitations and suggestions",
            "subsections": [],
            "citations_used": [],
            "word_count": 0
        }}
    ],
    "appendices": [
        {{
            "appendix_id": "bibliography",
            "title": "References",
            "content": "Complete bibliography",
            "type": "bibliography"
        }},
        {{
            "appendix_id": "methodology_details",
            "title": "Detailed Methodology",
            "content": "Extended methodology information",
            "type": "methodology"
        }}
    ],
    "quality_assessment": {{
        "content_quality": "excellent|good|fair|poor",
        "citation_quality": "excellent|good|fair|poor",
        "structure_quality": "excellent|good|fair|poor",
        "audience_appropriateness": "high|medium|low",
        "completeness": "comprehensive|adequate|limited",
        "areas_for_improvement": ["Area 1", "Area 2"]
    }},
    "report_statistics": {{
        "total_word_count": 0,
        "total_sections": 0,
        "total_citations": 0,
        "unique_sources": 0,
        "research_depth_score": 0.0-1.0,
        "evidence_strength": "strong|moderate|weak"
    }}
}}
```

Ensure the report is professional, well-structured, and appropriate for the specified audience while maintaining academic rigor.
"""
        
        try:
            logger.info("🤖 ResearchReportGeneratorNode: Calling LLM for report generation")
            response = call_llm(prompt)
            
            # Extract JSON from response
            json_str = response.split("```json")[1].split("```")[0].strip()
            report = json.loads(json_str)
            
            logger.info("✅ ResearchReportGeneratorNode: Successfully parsed report")
            
            # Validate and enhance the report
            report = self._validate_report(report, main_question, report_config, citations)
            
            return report
            
        except (IndexError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ ResearchReportGeneratorNode: Error parsing LLM response: {e}")
            logger.error(f"📄 ResearchReportGeneratorNode: Raw response: {response}")
            
            # Return fallback report
            return self._get_fallback_report(main_question, research_synthesis, report_config)
        
        except Exception as e:
            logger.error(f"❌ ResearchReportGeneratorNode: Unexpected error: {e}")
            raise
    
    def _prepare_citation_lookup(self, citations: Dict[str, Any]) -> Dict[str, str]:
        """Prepare citation lookup for easy referencing"""
        citation_lookup = {}
        
        if citations and "citation_database" in citations:
            for citation in citations["citation_database"]:
                citation_id = citation.get("citation_id", "")
                in_text = citation.get("in_text_citation", "")
                if citation_id and in_text:
                    citation_lookup[citation_id] = in_text
        
        return citation_lookup
    
    def _prepare_structured_content(self, research_synthesis: Dict[str, Any], citations: Dict[str, Any], research_metadata: Dict[str, Any]) -> str:
        """Prepare structured content for report generation"""
        content_parts = []
        
        # Add synthesis overview
        synthesis_overview = research_synthesis.get("synthesis_overview", {})
        content_parts.append(f"""
Research Synthesis Overview:
Primary Answer: {synthesis_overview.get('primary_answer', 'Not available')}
Confidence Level: {synthesis_overview.get('confidence_level', 'Unknown')}
Evidence Strength: {synthesis_overview.get('evidence_strength', 'Unknown')}
""")
        
        # Add key insights
        key_insights = research_synthesis.get("key_insights", [])
        if key_insights:
            content_parts.append(f"\nKey Insights ({len(key_insights)} total):")
            for i, insight in enumerate(key_insights[:5], 1):  # Limit to top 5
                content_parts.append(f"  {i}. {insight.get('insight', 'No insight')} (Confidence: {insight.get('confidence', 'Unknown')})")
        
        # Add thematic analysis
        thematic_analysis = research_synthesis.get("thematic_analysis", {})
        major_themes = thematic_analysis.get("major_themes", [])
        if major_themes:
            content_parts.append(f"\nMajor Themes ({len(major_themes)} total):")
            for theme in major_themes[:3]:  # Limit to top 3
                content_parts.append(f"  - {theme.get('theme', 'Unknown')}: {theme.get('description', 'No description')}")
        
        # Add conclusions
        conclusions = research_synthesis.get("conclusions", {})
        primary_conclusions = conclusions.get("primary_conclusions", [])
        if primary_conclusions:
            content_parts.append(f"\nPrimary Conclusions ({len(primary_conclusions)} total):")
            for conclusion in primary_conclusions[:3]:  # Limit to top 3
                content_parts.append(f"  - {conclusion.get('conclusion', 'No conclusion')} (Confidence: {conclusion.get('confidence_level', 'Unknown')})")
        
        # Add research gaps
        research_gaps = research_synthesis.get("research_gaps", [])
        if research_gaps:
            content_parts.append(f"\nResearch Gaps ({len(research_gaps)} total):")
            for gap in research_gaps[:3]:  # Limit to top 3
                content_parts.append(f"  - {gap.get('gap_description', 'Unknown gap')}")
        
        # Add citation information
        if citations:
            citation_summary = citations.get("citation_summary", {})
            content_parts.append(f"""
Citation Information:
Total Sources: {citation_summary.get('total_sources', 0)}
Source Quality: {citations.get('citation_quality_assessment', {}).get('overall_quality', 'Unknown')}
""")
        
        return "\n".join(content_parts)
    
    def _get_empty_report(self, main_question: str, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Return empty report structure"""
        return {
            "report_metadata": {
                "title": "Research Report - Insufficient Data",
                "research_question": main_question,
                "report_type": report_config.get("report_type", "comprehensive"),
                "target_audience": report_config.get("target_audience", "general"),
                "generation_date": datetime.now().isoformat(),
                "word_count_estimate": 0,
                "section_count": 0,
                "citation_count": 0
            },
            "executive_summary": {
                "key_question": main_question,
                "primary_findings": "Insufficient data to generate findings",
                "key_insights": [],
                "main_conclusions": "Cannot draw conclusions without research data",
                "recommendations_summary": "Research data needed",
                "confidence_assessment": "low"
            },
            "report_sections": [
                {
                    "section_id": "notice",
                    "section_title": "Data Availability Notice",
                    "section_number": 1,
                    "content": "This report could not be generated due to insufficient research data. Please ensure research synthesis is completed before generating reports.",
                    "subsections": [],
                    "citations_used": [],
                    "word_count": 25
                }
            ],
            "appendices": [],
            "quality_assessment": {
                "content_quality": "poor",
                "citation_quality": "poor",
                "structure_quality": "poor",
                "audience_appropriateness": "low",
                "completeness": "limited",
                "areas_for_improvement": ["Need research data", "Complete synthesis first"]
            },
            "report_statistics": {
                "total_word_count": 25,
                "total_sections": 1,
                "total_citations": 0,
                "unique_sources": 0,
                "research_depth_score": 0.0,
                "evidence_strength": "weak"
            },
            "status": "insufficient_data"
        }
    
    def _get_fallback_report(self, main_question: str, research_synthesis: Dict[str, Any], report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Return fallback report when LLM parsing fails"""
        logger.info("🔄 ResearchReportGeneratorNode: Creating fallback report")
        
        # Extract basic information from synthesis
        synthesis_overview = research_synthesis.get("synthesis_overview", {})
        key_insights = research_synthesis.get("key_insights", [])
        conclusions = research_synthesis.get("conclusions", {})
        
        # Create basic report structure
        report_sections = [
            {
                "section_id": "summary",
                "section_title": "Research Summary",
                "section_number": 1,
                "content": f"Research Question: {main_question}\n\nPrimary Answer: {synthesis_overview.get('primary_answer', 'See research synthesis for details')}\n\nThis report was generated using fallback methods due to processing limitations.",
                "subsections": [],
                "citations_used": [],
                "word_count": 50
            }
        ]
        
        if key_insights:
            insights_content = "Key Research Insights:\n"
            for i, insight in enumerate(key_insights[:5], 1):
                insights_content += f"{i}. {insight.get('insight', 'No insight available')}\n"
            
            report_sections.append({
                "section_id": "insights",
                "section_title": "Key Insights",
                "section_number": 2,
                "content": insights_content,
                "subsections": [],
                "citations_used": [],
                "word_count": len(insights_content.split())
            })
        
        primary_conclusions = conclusions.get("primary_conclusions", [])
        if primary_conclusions:
            conclusions_content = "Research Conclusions:\n"
            for i, conclusion in enumerate(primary_conclusions[:3], 1):
                conclusions_content += f"{i}. {conclusion.get('conclusion', 'No conclusion available')}\n"
            
            report_sections.append({
                "section_id": "conclusions",
                "section_title": "Conclusions",
                "section_number": 3,
                "content": conclusions_content,
                "subsections": [],
                "citations_used": [],
                "word_count": len(conclusions_content.split())
            })
        
        total_word_count = sum(section.get("word_count", 0) for section in report_sections)
        
        return {
            "report_metadata": {
                "title": f"Research Report: {main_question[:50]}{'...' if len(main_question) > 50 else ''}",
                "research_question": main_question,
                "report_type": report_config.get("report_type", "comprehensive"),
                "target_audience": report_config.get("target_audience", "general"),
                "generation_date": datetime.now().isoformat(),
                "word_count_estimate": total_word_count,
                "section_count": len(report_sections),
                "citation_count": 0
            },
            "executive_summary": {
                "key_question": main_question,
                "primary_findings": synthesis_overview.get("primary_answer", "See report sections for details"),
                "key_insights": [insight.get("insight", "") for insight in key_insights[:3]],
                "main_conclusions": "See conclusions section for details",
                "recommendations_summary": "Manual review recommended",
                "confidence_assessment": synthesis_overview.get("confidence_level", "medium")
            },
            "report_sections": report_sections,
            "appendices": [
                {
                    "appendix_id": "notice",
                    "title": "Generation Notice",
                    "content": "This report was generated using fallback methods. Manual review and formatting improvements are recommended.",
                    "type": "notice"
                }
            ],
            "quality_assessment": {
                "content_quality": "fair",
                "citation_quality": "poor",
                "structure_quality": "fair",
                "audience_appropriateness": "medium",
                "completeness": "limited",
                "areas_for_improvement": ["Add proper citations", "Improve formatting", "Expand analysis"]
            },
            "report_statistics": {
                "total_word_count": total_word_count,
                "total_sections": len(report_sections),
                "total_citations": 0,
                "unique_sources": 0,
                "research_depth_score": 0.3,
                "evidence_strength": "moderate"
            },
            "status": "fallback_report"
        }
    
    def _validate_report(self, report: Dict[str, Any], main_question: str, report_config: Dict[str, Any], citations: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the report structure"""
        # Ensure required sections exist
        required_sections = ["report_metadata", "executive_summary", "report_sections", "appendices", "quality_assessment", "report_statistics"]
        for section in required_sections:
            if section not in report:
                report[section] = {}
        
        # Validate arrays exist
        array_sections = ["report_sections", "appendices"]
        for section in array_sections:
            if section not in report:
                report[section] = []
            elif not isinstance(report[section], list):
                report[section] = []
        
        # Ensure metadata is correct
        if "report_metadata" not in report:
            report["report_metadata"] = {}
        
        report["report_metadata"]["research_question"] = main_question
        report["report_metadata"]["generation_date"] = datetime.now().isoformat()
        report["report_metadata"]["validation_status"] = "validated"
        
        # Calculate statistics
        total_sections = len(report.get("report_sections", []))
        total_word_count = sum(section.get("word_count", 0) for section in report.get("report_sections", []))
        
        # Count citations used
        total_citations = 0
        for section in report.get("report_sections", []):
            total_citations += len(section.get("citations_used", []))
        
        if "report_statistics" not in report:
            report["report_statistics"] = {}
        
        report["report_statistics"]["total_sections"] = total_sections
        report["report_statistics"]["total_word_count"] = total_word_count
        report["report_statistics"]["total_citations"] = total_citations
        
        # Add citation information
        if citations:
            report["report_statistics"]["unique_sources"] = len(citations.get("citation_database", []))
        
        return report
    
    def post(self, shared: Dict[str, Any], prep_res: tuple, exec_res: Dict[str, Any]) -> str:
        """Store research report in shared store"""
        logger.info(f"💾 ResearchReportGeneratorNode: post - Storing research report")
        
        shared["research_report"] = exec_res
        
        # Extract key report information for easy access
        shared["report_metadata"] = exec_res.get("report_metadata", {})
        shared["executive_summary"] = exec_res.get("executive_summary", {})
        shared["report_sections"] = exec_res.get("report_sections", [])
        shared["report_statistics"] = exec_res.get("report_statistics", {})
        
        # Create formatted report text for easy viewing
        formatted_report = self._create_formatted_report_text(exec_res)
        shared["formatted_report"] = formatted_report
        
        # Update research metadata with report info
        if "research_metadata" not in shared:
            shared["research_metadata"] = {}
        
        shared["research_metadata"]["report_generated"] = True
        shared["research_metadata"]["report_type"] = exec_res.get("report_metadata", {}).get("report_type", "unknown")
        shared["research_metadata"]["report_word_count"] = exec_res.get("report_statistics", {}).get("total_word_count", 0)
        shared["research_metadata"]["report_quality"] = exec_res.get("quality_assessment", {}).get("content_quality", "unknown")
        
        # Create report summary for easy access
        report_summary = {
            "title": exec_res.get("report_metadata", {}).get("title", "Research Report"),
            "word_count": exec_res.get("report_statistics", {}).get("total_word_count", 0),
            "section_count": exec_res.get("report_statistics", {}).get("total_sections", 0),
            "citation_count": exec_res.get("report_statistics", {}).get("total_citations", 0),
            "quality": exec_res.get("quality_assessment", {}).get("content_quality", "unknown"),
            "generation_date": exec_res.get("report_metadata", {}).get("generation_date", ""),
            "report_status": exec_res.get("status", "success")
        }
        
        shared["report_summary"] = report_summary
        
        logger.info(f"✅ ResearchReportGeneratorNode: Stored report with {exec_res.get('report_statistics', {}).get('total_sections', 0)} sections")
        
        return "default"
    
    def _create_formatted_report_text(self, report: Dict[str, Any]) -> str:
        """Create formatted text version of the report"""
        lines = []
        
        # Add title
        metadata = report.get("report_metadata", {})
        title = metadata.get("title", "Research Report")
        lines.append(f"# {title}")
        lines.append(f"Research Question: {metadata.get('research_question', 'Unknown')}")
        lines.append(f"Generated: {metadata.get('generation_date', 'Unknown')}")
        lines.append("")
        
        # Add executive summary
        exec_summary = report.get("executive_summary", {})
        lines.append("## Executive Summary")
        lines.append(exec_summary.get("primary_findings", "No summary available"))
        lines.append("")
        
        # Add main sections
        for section in report.get("report_sections", []):
            section_title = section.get("section_title", "Unknown Section")
            section_number = section.get("section_number", "")
            
            if section_number:
                lines.append(f"## {section_number}. {section_title}")
            else:
                lines.append(f"## {section_title}")
            
            lines.append(section.get("content", "No content available"))
            
            # Add subsections
            for subsection in section.get("subsections", []):
                lines.append(f"### {subsection.get('subsection_title', 'Untitled')}")
                lines.append(subsection.get("content", "No content"))
            
            lines.append("")
        
        # Add statistics
        stats = report.get("report_statistics", {})
        lines.append("---")
        lines.append(f"Word Count: {stats.get('total_word_count', 0)}")
        lines.append(f"Sections: {stats.get('total_sections', 0)}")
        lines.append(f"Citations: {stats.get('total_citations', 0)}")
        
        return "\n".join(lines)