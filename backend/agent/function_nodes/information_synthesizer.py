from pocketflow import Node
from typing import Dict, List, Any, Optional
from agent.utils.stream_llm import call_llm
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class InformationSynthesizerNode(Node):
    """
    Node to synthesize information from multiple research sources and sub-questions
    into coherent insights, identify patterns, and resolve conflicting information.
    
    Example:
        >>> node = InformationSynthesizerNode()
        >>> shared = {"research_findings": {...}, "research_scope": {...}}
        >>> node.prep(shared)
        # Returns (research_findings, research_scope, main_question)
        >>> node.exec((...))
        # Returns synthesized analysis with key insights, patterns, and conclusions
    """
    
    def prep(self, shared: Dict[str, Any]) -> tuple:
        """Prepare research findings and scope for synthesis"""
        research_findings = shared.get("research_findings", {})
        research_scope = shared.get("research_scope", {})
        main_question = shared.get("research_question", "")
        research_metadata = shared.get("research_metadata", {})
        
        logger.info(f"🔄 InformationSynthesizerNode: prep - synthesizing {len(research_findings)} research findings")
        
        if not research_findings:
            logger.warning("⚠️ InformationSynthesizerNode: No research findings provided")
            
        return research_findings, research_scope, main_question, research_metadata
    
    def exec(self, inputs: tuple) -> Dict[str, Any]:
        """Synthesize information from multiple research findings"""
        research_findings, research_scope, main_question, research_metadata = inputs
        
        logger.info(f"🔄 InformationSynthesizerNode: exec - synthesizing findings for '{main_question[:50]}...'")
        
        if not research_findings:
            logger.warning("⚠️ InformationSynthesizerNode: No research findings to synthesize")
            return self._get_empty_synthesis(main_question)
        
        # Prepare structured research data for analysis
        structured_findings = self._structure_research_findings(research_findings)
        
        prompt = f"""
You are a research synthesis expert. Your task is to analyze and synthesize information from multiple research sub-questions to provide comprehensive insights and answer the main research question.

Main Research Question: "{main_question}"

Research Scope:
- Primary Focus: {research_scope.get('primary_focus', 'Unknown')}
- Secondary Aspects: {research_scope.get('secondary_aspects', [])}
- Research Boundaries: {research_scope.get('research_boundaries', 'None specified')}

Research Findings from Sub-Questions:
{structured_findings}

Please synthesize this information to provide a comprehensive analysis:

1. Identify key themes and patterns across all research findings
2. Synthesize insights that directly answer the main research question
3. Resolve any conflicting information by evaluating source credibility
4. Identify knowledge gaps and areas needing further research
5. Draw evidence-based conclusions with proper source attribution
6. Assess the overall quality and completeness of the research

Output your synthesis in JSON format:
```json
{{
    "main_question": "{main_question}",
    "synthesis_overview": {{
        "primary_answer": "Direct, comprehensive answer to the main research question",
        "confidence_level": "high|medium|low",
        "evidence_strength": "strong|moderate|weak",
        "completeness_assessment": "comprehensive|partial|limited"
    }},
    "key_insights": [
        {{
            "insight": "Major insight or finding",
            "supporting_evidence": ["Evidence 1", "Evidence 2"],
            "sources": ["Source references"],
            "confidence": "high|medium|low",
            "importance": "critical|important|moderate",
            "sub_questions_addressed": ["q1", "q2"]
        }}
    ],
    "thematic_analysis": {{
        "major_themes": [
            {{
                "theme": "Theme name",
                "description": "Theme description",
                "evidence_count": 0,
                "consistency": "consistent|mixed|conflicting",
                "implications": "What this theme means"
            }}
        ],
        "cross_cutting_patterns": [
            {{
                "pattern": "Pattern description", 
                "frequency": "common|occasional|rare",
                "significance": "high|medium|low",
                "examples": ["Example 1", "Example 2"]
            }}
        ]
    }},
    "conflict_resolution": [
        {{
            "conflicting_topic": "Topic where sources disagree",
            "positions": [
                {{
                    "position": "One viewpoint",
                    "sources": ["Source references"],
                    "evidence_quality": "strong|moderate|weak"
                }}
            ],
            "resolution": "How the conflict was resolved",
            "final_conclusion": "Conclusion after resolving conflict"
        }}
    ],
    "evidence_assessment": {{
        "total_sources_analyzed": 0,
        "source_quality_distribution": {{
            "high_quality": 0,
            "medium_quality": 0,
            "low_quality": 0
        }},
        "source_type_coverage": {{
            "academic": 0,
            "industry": 0,
            "news": 0,
            "official": 0,
            "other": 0
        }},
        "temporal_coverage": {{
            "recent": 0,
            "medium_term": 0,
            "historical": 0
        }},
        "geographic_coverage": "Description of geographic scope",
        "bias_assessment": "Assessment of potential biases in sources"
    }},
    "research_gaps": [
        {{
            "gap_description": "Description of knowledge gap",
            "importance": "critical|important|moderate",
            "impact_on_conclusions": "How this gap affects findings",
            "suggested_follow_up": "Recommended additional research"
        }}
    ],
    "conclusions": {{
        "primary_conclusions": [
            {{
                "conclusion": "Main conclusion",
                "evidence_basis": "Evidence supporting this conclusion",
                "confidence_level": "high|medium|low",
                "limitations": "Limitations or caveats"
            }}
        ],
        "implications": [
            {{
                "implication": "What this research implies",
                "domain": "Area where this applies",
                "significance": "high|medium|low",
                "time_horizon": "short-term|medium-term|long-term"
            }}
        ],
        "recommendations": [
            {{
                "recommendation": "Actionable recommendation",
                "rationale": "Why this is recommended",
                "target_audience": "Who should act on this",
                "implementation_difficulty": "easy|moderate|difficult"
            }}
        ]
    }},
    "synthesis_metadata": {{
        "total_sub_questions_analyzed": 0,
        "synthesis_date": "{datetime.now().isoformat()}",
        "synthesis_method": "LLM-based comprehensive analysis",
        "quality_score": 0.0-1.0,
        "reliability_assessment": "high|medium|low"
    }}
}}
```

Focus on providing evidence-based insights with clear attribution to sources and honest assessment of limitations.
"""
        
        try:
            logger.info("🤖 InformationSynthesizerNode: Calling LLM for synthesis")
            response = call_llm(prompt)
            
            # Extract JSON from response
            json_str = response.split("```json")[1].split("```")[0].strip()
            synthesis = json.loads(json_str)
            
            logger.info("✅ InformationSynthesizerNode: Successfully parsed synthesis")
            
            # Validate and enhance the synthesis
            synthesis = self._validate_synthesis(synthesis, main_question, research_findings)
            
            return synthesis
            
        except (IndexError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ InformationSynthesizerNode: Error parsing LLM response: {e}")
            logger.error(f"📄 InformationSynthesizerNode: Raw response: {response}")
            
            # Return fallback synthesis
            return self._get_fallback_synthesis(main_question, research_findings)
        
        except Exception as e:
            logger.error(f"❌ InformationSynthesizerNode: Unexpected error: {e}")
            raise
    
    def _structure_research_findings(self, research_findings: Dict[str, Any]) -> str:
        """Structure research findings for LLM analysis"""
        if not research_findings:
            return "No research findings available"
        
        structured_text = []
        
        for sub_question_id, findings in research_findings.items():
            sub_question = findings.get("sub_question", "Unknown question")
            info_gathered = findings.get("information_gathered", {})
            research_status = findings.get("research_status", {})
            
            structured_text.append(f"""
Sub-Question {sub_question_id}: {sub_question}
Quality: {research_status.get('information_quality', 'unknown')}
Confidence: {research_status.get('confidence_level', 'unknown')}

Key Findings ({len(info_gathered.get('key_findings', []))} total):
""")
            
            # Add key findings
            for i, finding in enumerate(info_gathered.get("key_findings", [])[:3], 1):  # Limit to top 3
                structured_text.append(f"  {i}. {finding.get('finding', 'No finding')} (Source: {finding.get('source', 'Unknown')}, Credibility: {finding.get('credibility_score', 'Unknown')})")
            
            # Add data points if available
            data_points = info_gathered.get("data_points", [])
            if data_points:
                structured_text.append(f"\nData Points ({len(data_points)} total):")
                for dp in data_points[:2]:  # Limit to top 2
                    structured_text.append(f"  - {dp.get('metric', 'Unknown')}: {dp.get('value', 'Unknown')} {dp.get('unit', '')}")
            
            # Add expert opinions if available
            expert_opinions = info_gathered.get("expert_opinions", [])
            if expert_opinions:
                structured_text.append(f"\nExpert Opinions ({len(expert_opinions)} total):")
                for opinion in expert_opinions[:2]:  # Limit to top 2
                    structured_text.append(f"  - {opinion.get('expert', 'Unknown')}: {opinion.get('opinion', 'No opinion')}")
            
            structured_text.append("\n" + "="*80 + "\n")
        
        return "\n".join(structured_text)
    
    def _get_empty_synthesis(self, main_question: str) -> Dict[str, Any]:
        """Return empty synthesis structure"""
        return {
            "main_question": main_question,
            "synthesis_overview": {
                "primary_answer": "Insufficient data to answer the research question",
                "confidence_level": "low",
                "evidence_strength": "weak",
                "completeness_assessment": "limited"
            },
            "key_insights": [],
            "thematic_analysis": {
                "major_themes": [],
                "cross_cutting_patterns": []
            },
            "conflict_resolution": [],
            "evidence_assessment": {
                "total_sources_analyzed": 0,
                "source_quality_distribution": {"high_quality": 0, "medium_quality": 0, "low_quality": 0},
                "source_type_coverage": {"academic": 0, "industry": 0, "news": 0, "official": 0, "other": 0},
                "temporal_coverage": {"recent": 0, "medium_term": 0, "historical": 0},
                "geographic_coverage": "Unknown",
                "bias_assessment": "Cannot assess - no data"
            },
            "research_gaps": [
                {
                    "gap_description": "No research findings available",
                    "importance": "critical",
                    "impact_on_conclusions": "Cannot draw any conclusions",
                    "suggested_follow_up": "Conduct initial research"
                }
            ],
            "conclusions": {
                "primary_conclusions": [],
                "implications": [],
                "recommendations": []
            },
            "synthesis_metadata": {
                "total_sub_questions_analyzed": 0,
                "synthesis_date": datetime.now().isoformat(),
                "synthesis_method": "No data available",
                "quality_score": 0.0,
                "reliability_assessment": "low"
            },
            "status": "empty_findings"
        }
    
    def _get_fallback_synthesis(self, main_question: str, research_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Return fallback synthesis when LLM parsing fails"""
        logger.info("🔄 InformationSynthesizerNode: Creating fallback synthesis")
        
        # Extract basic information from research findings
        total_findings = 0
        total_sources = 0
        quality_levels = {"good": 0, "fair": 0, "poor": 0}
        
        for findings in research_findings.values():
            info = findings.get("information_gathered", {})
            total_findings += len(info.get("key_findings", []))
            
            source_analysis = findings.get("source_analysis", {})
            total_sources += source_analysis.get("total_sources_analyzed", 0)
            
            quality = findings.get("research_status", {}).get("information_quality", "fair")
            if quality in quality_levels:
                quality_levels[quality] += 1
        
        return {
            "main_question": main_question,
            "synthesis_overview": {
                "primary_answer": "Research findings are available but could not be automatically synthesized",
                "confidence_level": "medium",
                "evidence_strength": "moderate",
                "completeness_assessment": "partial"
            },
            "key_insights": [
                {
                    "insight": f"Research collected {total_findings} findings from {total_sources} sources",
                    "supporting_evidence": ["Multiple research sub-questions completed"],
                    "sources": ["Research findings data"],
                    "confidence": "medium",
                    "importance": "moderate",
                    "sub_questions_addressed": list(research_findings.keys())
                }
            ],
            "thematic_analysis": {
                "major_themes": [
                    {
                        "theme": "Data collection completed",
                        "description": "Research sub-questions have been completed",
                        "evidence_count": len(research_findings),
                        "consistency": "consistent",
                        "implications": "Data is available for manual analysis"
                    }
                ],
                "cross_cutting_patterns": []
            },
            "conflict_resolution": [],
            "evidence_assessment": {
                "total_sources_analyzed": total_sources,
                "source_quality_distribution": {"high_quality": quality_levels.get("good", 0), "medium_quality": quality_levels.get("fair", 0), "low_quality": quality_levels.get("poor", 0)},
                "source_type_coverage": {"academic": 0, "industry": 0, "news": 0, "official": 0, "other": total_sources},
                "temporal_coverage": {"recent": total_sources, "medium_term": 0, "historical": 0},
                "geographic_coverage": "Unknown",
                "bias_assessment": "Cannot assess automatically"
            },
            "research_gaps": [
                {
                    "gap_description": "Automatic synthesis failed",
                    "importance": "important",
                    "impact_on_conclusions": "Manual review required",
                    "suggested_follow_up": "Manual analysis of research findings"
                }
            ],
            "conclusions": {
                "primary_conclusions": [
                    {
                        "conclusion": "Research data collection completed successfully",
                        "evidence_basis": f"{len(research_findings)} sub-questions researched",
                        "confidence_level": "high",
                        "limitations": "Automatic synthesis failed"
                    }
                ],
                "implications": [],
                "recommendations": [
                    {
                        "recommendation": "Review research findings manually",
                        "rationale": "Automatic synthesis was not possible",
                        "target_audience": "Research team",
                        "implementation_difficulty": "moderate"
                    }
                ]
            },
            "synthesis_metadata": {
                "total_sub_questions_analyzed": len(research_findings),
                "synthesis_date": datetime.now().isoformat(),
                "synthesis_method": "Fallback analysis",
                "quality_score": 0.3,
                "reliability_assessment": "medium"
            },
            "status": "fallback_synthesis"
        }
    
    def _validate_synthesis(self, synthesis: Dict[str, Any], main_question: str, research_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the synthesis structure"""
        # Ensure main question is preserved
        synthesis["main_question"] = main_question
        
        # Validate required sections exist
        required_sections = ["synthesis_overview", "key_insights", "thematic_analysis", "evidence_assessment", "conclusions", "synthesis_metadata"]
        for section in required_sections:
            if section not in synthesis:
                synthesis[section] = {}
        
        # Validate arrays exist
        array_sections = ["key_insights", "conflict_resolution", "research_gaps"]
        for section in array_sections:
            if section not in synthesis:
                synthesis[section] = []
            elif not isinstance(synthesis[section], list):
                synthesis[section] = []
        
        # Add validation metadata
        synthesis["validation_status"] = "validated"
        synthesis["synthesis_date"] = datetime.now().isoformat()
        synthesis["total_research_findings"] = len(research_findings)
        
        # Calculate quality metrics
        if "synthesis_metadata" not in synthesis:
            synthesis["synthesis_metadata"] = {}
        
        synthesis["synthesis_metadata"]["total_sub_questions_analyzed"] = len(research_findings)
        synthesis["synthesis_metadata"]["total_insights"] = len(synthesis.get("key_insights", []))
        
        return synthesis
    
    def post(self, shared: Dict[str, Any], prep_res: tuple, exec_res: Dict[str, Any]) -> str:
        """Store synthesis results in shared store"""
        logger.info(f"💾 InformationSynthesizerNode: post - Storing synthesis for '{exec_res.get('main_question', 'Unknown')[:50]}...'")
        
        shared["research_synthesis"] = exec_res
        
        # Extract key synthesis information for easy access
        shared["synthesis_overview"] = exec_res.get("synthesis_overview", {})
        shared["key_insights"] = exec_res.get("key_insights", [])
        shared["research_conclusions"] = exec_res.get("conclusions", {})
        shared["research_gaps"] = exec_res.get("research_gaps", [])
        
        # Update research metadata with synthesis info
        if "research_metadata" not in shared:
            shared["research_metadata"] = {}
        
        shared["research_metadata"]["synthesis_complete"] = True
        shared["research_metadata"]["synthesis_quality"] = exec_res.get("synthesis_metadata", {}).get("quality_score", 0.0)
        shared["research_metadata"]["total_insights"] = len(exec_res.get("key_insights", []))
        shared["research_metadata"]["confidence_level"] = exec_res.get("synthesis_overview", {}).get("confidence_level", "unknown")
        
        # Create summary for easy access
        synthesis_summary = {
            "primary_answer": exec_res.get("synthesis_overview", {}).get("primary_answer", "No answer available"),
            "confidence_level": exec_res.get("synthesis_overview", {}).get("confidence_level", "unknown"),
            "total_insights": len(exec_res.get("key_insights", [])),
            "research_quality": exec_res.get("synthesis_metadata", {}).get("quality_score", 0.0),
            "synthesis_status": exec_res.get("status", "success")
        }
        
        shared["synthesis_summary"] = synthesis_summary
        
        logger.info(f"✅ InformationSynthesizerNode: Stored synthesis with {len(exec_res.get('key_insights', []))} insights")
        
        return "default"