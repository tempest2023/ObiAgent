from pocketflow import Node
from typing import Dict, List, Any, Optional
from agent.utils.stream_llm import call_llm
import logging
import json
import re
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class CitationManagerNode(Node):
    """
    Node to manage citations and source attribution for research findings.
    Creates proper academic citations and tracks source credibility throughout research.
    
    Example:
        >>> node = CitationManagerNode()
        >>> shared = {"research_findings": {...}, "search_results": [...]}
        >>> node.prep(shared)
        # Returns (research_findings, search_results, citation_style)
        >>> node.exec((...))
        # Returns comprehensive citation database with proper academic formatting
    """
    
    def prep(self, shared: Dict[str, Any]) -> tuple:
        """Prepare research findings and sources for citation management"""
        research_findings = shared.get("research_findings", {})
        search_results = shared.get("search_results", [])
        existing_citations = shared.get("citations", {})
        citation_style = shared.get("citation_style", "apa")  # apa, mla, chicago, harvard
        research_metadata = shared.get("research_metadata", {})
        
        logger.info(f"🔄 CitationManagerNode: prep - managing citations for {len(research_findings)} research findings")
        
        if not research_findings and not search_results:
            logger.warning("⚠️ CitationManagerNode: No research findings or search results provided")
            
        return research_findings, search_results, existing_citations, citation_style, research_metadata
    
    def exec(self, inputs: tuple) -> Dict[str, Any]:
        """Generate comprehensive citation database from research sources"""
        research_findings, search_results, existing_citations, citation_style, research_metadata = inputs
        
        logger.info(f"🔄 CitationManagerNode: exec - generating citations in {citation_style} style")
        
        if not research_findings and not search_results:
            logger.warning("⚠️ CitationManagerNode: No sources to cite")
            return self._get_empty_citations(citation_style)
        
        # Extract all sources from research findings and search results
        all_sources = self._extract_all_sources(research_findings, search_results)
        
        if not all_sources:
            logger.warning("⚠️ CitationManagerNode: No sources found in research data")
            return self._get_no_sources_citations(citation_style)
        
        # Prepare sources for citation formatting
        sources_text = self._format_sources_for_citation(all_sources, citation_style)
        
        prompt = f"""
You are a research citation specialist. Your task is to create proper academic citations and manage source attribution for a research project.

Citation Style: {citation_style.upper()}
Total Sources: {len(all_sources)}

Sources to Citation:
{sources_text}

Please create a comprehensive citation database:

1. Format each source according to the specified citation style
2. Assign unique citation IDs for easy referencing
3. Assess source credibility and academic value
4. Group sources by type and quality
5. Create in-text citation examples
6. Identify and flag potential issues (missing information, unreliable sources)

Output your citation analysis in JSON format:
```json
{{
    "citation_style": "{citation_style}",
    "citation_database": [
        {{
            "citation_id": "unique_id",
            "formatted_citation": "Full citation in {citation_style} format",
            "in_text_citation": "In-text citation format",
            "source_type": "web|academic|news|book|report|other",
            "url": "Original URL if available",
            "title": "Source title",
            "author": "Author name(s)",
            "publication_date": "Publication date if available",
            "publisher": "Publisher or website name",
            "access_date": "Date accessed",
            "credibility_assessment": {{
                "credibility_score": 0.0-1.0,
                "credibility_level": "high|medium|low",
                "credibility_factors": ["Factor 1", "Factor 2"],
                "potential_biases": ["Bias 1", "Bias 2"],
                "reliability_notes": "Assessment notes"
            }},
            "usage_tracking": {{
                "times_cited": 0,
                "sub_questions_referenced": ["q1", "q2"],
                "key_findings_supported": ["finding_1", "finding_2"],
                "importance_weight": 0.0-1.0
            }}
        }}
    ],
    "citation_summary": {{
        "total_sources": 0,
        "source_type_breakdown": {{
            "academic": 0,
            "news": 0,
            "web": 0,
            "official": 0,
            "other": 0
        }},
        "credibility_distribution": {{
            "high_credibility": 0,
            "medium_credibility": 0,
            "low_credibility": 0
        }},
        "temporal_distribution": {{
            "very_recent": 0,
            "recent": 0,
            "older": 0,
            "undated": 0
        }}
    }},
    "citation_quality_assessment": {{
        "overall_quality": "excellent|good|fair|poor",
        "source_diversity": "high|medium|low",
        "academic_rigor": "high|medium|low",
        "potential_issues": [
            {{
                "issue": "Description of potential issue",
                "severity": "high|medium|low",
                "affected_sources": ["citation_id_1", "citation_id_2"],
                "recommendations": "How to address this issue"
            }}
        ],
        "missing_information": [
            {{
                "missing_field": "author|date|publisher|etc",
                "affected_sources": ["citation_id_1"],
                "impact": "How this affects citation quality"
            }}
        ]
    }},
    "bibliography": {{
        "formatted_bibliography": "Complete bibliography in {citation_style} format",
        "grouped_by_type": {{
            "academic_sources": ["Citation 1", "Citation 2"],
            "news_sources": ["Citation 3", "Citation 4"],
            "web_sources": ["Citation 5", "Citation 6"],
            "other_sources": ["Citation 7", "Citation 8"]
        }}
    }},
    "citation_guidelines": {{
        "in_text_usage": "How to use in-text citations",
        "common_patterns": ["Pattern 1", "Pattern 2"],
        "style_notes": "Important notes about {citation_style} style",
        "example_usage": "Example of proper citation usage"
    }},
    "metadata": {{
        "generated_date": "{datetime.now().isoformat()}",
        "citation_count": 0,
        "style_version": "{citation_style} style guide",
        "last_updated": "{datetime.now().isoformat()}"
    }}
}}
```

Ensure all citations follow proper {citation_style.upper()} formatting guidelines and include credibility assessments.
"""
        
        try:
            logger.info("🤖 CitationManagerNode: Calling LLM for citation generation")
            response = call_llm(prompt)
            
            # Extract JSON from response
            json_str = response.split("```json")[1].split("```")[0].strip()
            citations = json.loads(json_str)
            
            logger.info("✅ CitationManagerNode: Successfully parsed citations")
            
            # Validate and enhance the citations
            citations = self._validate_citations(citations, all_sources, citation_style)
            
            return citations
            
        except (IndexError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ CitationManagerNode: Error parsing LLM response: {e}")
            logger.error(f"📄 CitationManagerNode: Raw response: {response}")
            
            # Return fallback citations
            return self._get_fallback_citations(all_sources, citation_style)
        
        except Exception as e:
            logger.error(f"❌ CitationManagerNode: Unexpected error: {e}")
            raise
    
    def _extract_all_sources(self, research_findings: Dict[str, Any], search_results: List[Dict]) -> List[Dict]:
        """Extract all unique sources from research findings and search results"""
        sources = []
        seen_urls = set()
        
        # Extract sources from search results
        for result in search_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                sources.append({
                    "url": url,
                    "title": result.get("title", "Unknown Title"),
                    "snippet": result.get("snippet", ""),
                    "source_type": result.get("source_type", "web"),
                    "access_date": datetime.now().strftime("%Y-%m-%d"),
                    "from_search": True
                })
                seen_urls.add(url)
        
        # Extract sources from research findings
        for finding_data in research_findings.values():
            info_gathered = finding_data.get("information_gathered", {})
            
            # Extract from key findings
            for finding in info_gathered.get("key_findings", []):
                source = finding.get("source", "")
                if source and source not in seen_urls:
                    sources.append({
                        "url": source,
                        "title": finding.get("supporting_evidence", "Research Finding"),
                        "content": finding.get("finding", ""),
                        "source_type": finding.get("source_type", "web"),
                        "credibility_score": finding.get("credibility_score", 0.5),
                        "access_date": finding.get("extracted_date", datetime.now().isoformat())[:10],
                        "from_research": True
                    })
                    seen_urls.add(source)
            
            # Extract from expert opinions
            for opinion in info_gathered.get("expert_opinions", []):
                source = opinion.get("source", "")
                if source and source not in seen_urls:
                    sources.append({
                        "url": source,
                        "title": f"Expert Opinion: {opinion.get('expert', 'Unknown Expert')}",
                        "content": opinion.get("opinion", ""),
                        "source_type": "expert",
                        "author": opinion.get("expert", ""),
                        "expertise_area": opinion.get("expertise_area", ""),
                        "credibility": opinion.get("credibility", "medium"),
                        "access_date": datetime.now().strftime("%Y-%m-%d"),
                        "from_research": True
                    })
                    seen_urls.add(source)
        
        return sources
    
    def _format_sources_for_citation(self, sources: List[Dict], citation_style: str) -> str:
        """Format sources for LLM citation processing"""
        if not sources:
            return "No sources available"
        
        formatted_sources = []
        for i, source in enumerate(sources[:20], 1):  # Limit to top 20 sources
            url = source.get("url", "Unknown URL")
            title = source.get("title", "Unknown Title")
            content = source.get("content", source.get("snippet", ""))[:200] + "..." if source.get("content", source.get("snippet", "")) else ""
            source_type = source.get("source_type", "web")
            author = source.get("author", "")
            access_date = source.get("access_date", "")
            
            # Extract domain for publisher
            try:
                domain = urlparse(url).netloc if url.startswith("http") else ""
            except:
                domain = ""
            
            formatted_sources.append(f"""
Source {i}:
URL: {url}
Title: {title}
Author: {author if author else "Unknown"}
Publisher/Domain: {domain}
Type: {source_type}
Access Date: {access_date}
Content Preview: {content}
""")
        
        return "\n".join(formatted_sources)
    
    def _get_empty_citations(self, citation_style: str) -> Dict[str, Any]:
        """Return empty citation structure"""
        return {
            "citation_style": citation_style,
            "citation_database": [],
            "citation_summary": {
                "total_sources": 0,
                "source_type_breakdown": {"academic": 0, "news": 0, "web": 0, "official": 0, "other": 0},
                "credibility_distribution": {"high_credibility": 0, "medium_credibility": 0, "low_credibility": 0},
                "temporal_distribution": {"very_recent": 0, "recent": 0, "older": 0, "undated": 0}
            },
            "citation_quality_assessment": {
                "overall_quality": "poor",
                "source_diversity": "low",
                "academic_rigor": "low",
                "potential_issues": [{"issue": "No sources available", "severity": "high", "affected_sources": [], "recommendations": "Conduct research to gather sources"}],
                "missing_information": []
            },
            "bibliography": {
                "formatted_bibliography": "No sources available for citation",
                "grouped_by_type": {"academic_sources": [], "news_sources": [], "web_sources": [], "other_sources": []}
            },
            "citation_guidelines": {
                "in_text_usage": f"Follow {citation_style.upper()} guidelines",
                "common_patterns": [],
                "style_notes": f"No sources available to cite in {citation_style.upper()} format",
                "example_usage": "No examples available"
            },
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "citation_count": 0,
                "style_version": f"{citation_style} style guide",
                "last_updated": datetime.now().isoformat()
            },
            "status": "no_sources"
        }
    
    def _get_no_sources_citations(self, citation_style: str) -> Dict[str, Any]:
        """Return citation structure when no sources found in data"""
        return {
            "citation_style": citation_style,
            "citation_database": [],
            "citation_summary": {
                "total_sources": 0,
                "source_type_breakdown": {"academic": 0, "news": 0, "web": 0, "official": 0, "other": 0},
                "credibility_distribution": {"high_credibility": 0, "medium_credibility": 0, "low_credibility": 0},
                "temporal_distribution": {"very_recent": 0, "recent": 0, "older": 0, "undated": 0}
            },
            "citation_quality_assessment": {
                "overall_quality": "poor",
                "source_diversity": "low",
                "academic_rigor": "low",
                "potential_issues": [{"issue": "No extractable sources in research data", "severity": "high", "affected_sources": [], "recommendations": "Review search results and research findings for source URLs"}],
                "missing_information": []
            },
            "bibliography": {
                "formatted_bibliography": "No sources found in research data",
                "grouped_by_type": {"academic_sources": [], "news_sources": [], "web_sources": [], "other_sources": []}
            },
            "citation_guidelines": {
                "in_text_usage": f"Follow {citation_style.upper()} guidelines when sources become available",
                "common_patterns": [],
                "style_notes": f"No sources found to format in {citation_style.upper()} style",
                "example_usage": "Sources needed for citation examples"
            },
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "citation_count": 0,
                "style_version": f"{citation_style} style guide",
                "last_updated": datetime.now().isoformat()
            },
            "status": "no_sources_found"
        }
    
    def _get_fallback_citations(self, sources: List[Dict], citation_style: str) -> Dict[str, Any]:
        """Return fallback citations when LLM parsing fails"""
        logger.info("🔄 CitationManagerNode: Creating fallback citations")
        
        # Create basic citations manually
        citation_database = []
        for i, source in enumerate(sources[:10], 1):  # Limit to top 10
            url = source.get("url", "")
            title = source.get("title", f"Source {i}")
            domain = ""
            
            try:
                if url.startswith("http"):
                    domain = urlparse(url).netloc
            except:
                pass
            
            # Create basic citation
            if citation_style.lower() == "apa":
                formatted_citation = f"{title}. Retrieved from {url}"
            elif citation_style.lower() == "mla":
                formatted_citation = f'"{title}." Web. {source.get("access_date", "n.d.")}.'
            else:
                formatted_citation = f"{title}. {url}. Accessed {source.get('access_date', 'date unknown')}."
            
            citation_database.append({
                "citation_id": f"source_{i}",
                "formatted_citation": formatted_citation,
                "in_text_citation": f"(Source {i})",
                "source_type": source.get("source_type", "web"),
                "url": url,
                "title": title,
                "author": source.get("author", "Unknown"),
                "publication_date": "Unknown",
                "publisher": domain,
                "access_date": source.get("access_date", datetime.now().strftime("%Y-%m-%d")),
                "credibility_assessment": {
                    "credibility_score": source.get("credibility_score", 0.5),
                    "credibility_level": "medium",
                    "credibility_factors": ["Domain assessment"],
                    "potential_biases": ["Unknown"],
                    "reliability_notes": "Automated assessment"
                },
                "usage_tracking": {
                    "times_cited": 1,
                    "sub_questions_referenced": [],
                    "key_findings_supported": [],
                    "importance_weight": 0.5
                }
            })
        
        return {
            "citation_style": citation_style,
            "citation_database": citation_database,
            "citation_summary": {
                "total_sources": len(citation_database),
                "source_type_breakdown": {"academic": 0, "news": 0, "web": len(citation_database), "official": 0, "other": 0},
                "credibility_distribution": {"high_credibility": 0, "medium_credibility": len(citation_database), "low_credibility": 0},
                "temporal_distribution": {"very_recent": 0, "recent": len(citation_database), "older": 0, "undated": 0}
            },
            "citation_quality_assessment": {
                "overall_quality": "fair",
                "source_diversity": "medium",
                "academic_rigor": "low",
                "potential_issues": [{"issue": "LLM citation formatting failed", "severity": "medium", "affected_sources": [], "recommendations": "Manual review of citation formatting recommended"}],
                "missing_information": [{"missing_field": "publication_date", "affected_sources": [c["citation_id"] for c in citation_database], "impact": "Reduces citation quality"}]
            },
            "bibliography": {
                "formatted_bibliography": "\n".join([c["formatted_citation"] for c in citation_database]),
                "grouped_by_type": {
                    "academic_sources": [],
                    "news_sources": [],
                    "web_sources": [c["formatted_citation"] for c in citation_database],
                    "other_sources": []
                }
            },
            "citation_guidelines": {
                "in_text_usage": f"Use {citation_style.upper()} format for in-text citations",
                "common_patterns": ["(Source 1)", "(Source 2)"],
                "style_notes": f"Basic {citation_style.upper()} formatting applied",
                "example_usage": "According to research (Source 1), ..."
            },
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "citation_count": len(citation_database),
                "style_version": f"{citation_style} style guide",
                "last_updated": datetime.now().isoformat()
            },
            "status": "fallback_citations"
        }
    
    def _validate_citations(self, citations: Dict[str, Any], sources: List[Dict], citation_style: str) -> Dict[str, Any]:
        """Validate and clean the citations structure"""
        # Ensure required sections exist
        required_sections = ["citation_database", "citation_summary", "citation_quality_assessment", "bibliography", "citation_guidelines", "metadata"]
        for section in required_sections:
            if section not in citations:
                citations[section] = {}
        
        # Validate citation database
        if not isinstance(citations.get("citation_database"), list):
            citations["citation_database"] = []
        
        # Ensure citation style is preserved
        citations["citation_style"] = citation_style
        
        # Add validation metadata
        citations["validation_status"] = "validated"
        citations["total_sources_processed"] = len(sources)
        citations["citation_generation_date"] = datetime.now().isoformat()
        
        # Update metadata
        if "metadata" not in citations:
            citations["metadata"] = {}
        
        citations["metadata"]["citation_count"] = len(citations.get("citation_database", []))
        citations["metadata"]["validation_timestamp"] = datetime.now().isoformat()
        
        return citations
    
    def post(self, shared: Dict[str, Any], prep_res: tuple, exec_res: Dict[str, Any]) -> str:
        """Store citation database in shared store"""
        logger.info(f"💾 CitationManagerNode: post - Storing {len(exec_res.get('citation_database', []))} citations")
        
        shared["citations"] = exec_res
        
        # Extract key citation information for easy access
        shared["citation_database"] = exec_res.get("citation_database", [])
        shared["bibliography"] = exec_res.get("bibliography", {})
        shared["citation_style"] = exec_res.get("citation_style", "apa")
        
        # Create citation lookup for easy referencing
        citation_lookup = {}
        for citation in exec_res.get("citation_database", []):
            citation_id = citation.get("citation_id", "")
            if citation_id:
                citation_lookup[citation_id] = {
                    "formatted_citation": citation.get("formatted_citation", ""),
                    "in_text_citation": citation.get("in_text_citation", ""),
                    "url": citation.get("url", ""),
                    "credibility_score": citation.get("credibility_assessment", {}).get("credibility_score", 0.5)
                }
        
        shared["citation_lookup"] = citation_lookup
        
        # Update research metadata with citation info
        if "research_metadata" not in shared:
            shared["research_metadata"] = {}
        
        citation_summary = exec_res.get("citation_summary", {})
        shared["research_metadata"]["citations_generated"] = True
        shared["research_metadata"]["total_citations"] = citation_summary.get("total_sources", 0)
        shared["research_metadata"]["citation_quality"] = exec_res.get("citation_quality_assessment", {}).get("overall_quality", "unknown")
        shared["research_metadata"]["citation_style"] = exec_res.get("citation_style", "apa")
        
        # Create formatted bibliography for easy access
        formatted_bibliography = exec_res.get("bibliography", {}).get("formatted_bibliography", "")
        shared["formatted_bibliography"] = formatted_bibliography
        
        logger.info(f"✅ CitationManagerNode: Stored {len(exec_res.get('citation_database', []))} citations in {exec_res.get('citation_style', 'unknown')} format")
        
        return "default"