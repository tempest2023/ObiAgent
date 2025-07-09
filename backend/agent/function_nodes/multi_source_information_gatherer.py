from pocketflow import Node
from typing import Dict, List, Any, Optional
from agent.utils.stream_llm import call_llm
import logging
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class MultiSourceInformationGathererNode(Node):
    """
    Node to gather information from multiple sources based on research sub-questions.
    Can handle web searches, academic searches, news searches, and other source types.
    
    Example:
        >>> node = MultiSourceInformationGathererNode()
        >>> shared = {"current_sub_question": {"id": "q1", "question": "What is machine learning?"}}
        >>> node.prep(shared)
        # Returns (sub_question, search_sources, search_results)
        >>> node.exec((...))
        # Returns structured information gathered from multiple sources
    """
    
    def prep(self, shared: Dict[str, Any]) -> tuple:
        """Prepare sub-question and available search sources for information gathering"""
        current_sub_question = shared.get("current_sub_question", {})
        available_search_sources = shared.get("available_search_sources", ["web"])  
        existing_search_results = shared.get("search_results", [])
        research_context = shared.get("research_context", {})
        
        logger.info(f"🔄 MultiSourceInformationGathererNode: prep - question='{current_sub_question.get('question', 'Unknown')[:50]}...'")
        
        if not current_sub_question:
            logger.warning("⚠️ MultiSourceInformationGathererNode: No current sub-question provided")
            
        return current_sub_question, available_search_sources, existing_search_results, research_context
    
    def exec(self, inputs: tuple) -> Dict[str, Any]:
        """Gather information from multiple sources for the current sub-question"""
        sub_question, search_sources, existing_search_results, research_context = inputs
        
        question_text = sub_question.get("question", "")
        question_id = sub_question.get("id", "unknown")
        
        logger.info(f"🔄 MultiSourceInformationGathererNode: exec - gathering info for '{question_text[:50]}...'")
        
        if not question_text.strip():
            logger.warning("⚠️ MultiSourceInformationGathererNode: Empty question text")
            return self._get_empty_information(sub_question)
        
        # Extract relevant search results from existing data
        relevant_results = self._extract_relevant_search_results(question_text, existing_search_results)
        
        if not relevant_results:
            logger.warning("⚠️ MultiSourceInformationGathererNode: No relevant search results found")
            return self._get_no_results_information(sub_question)
        
        # Determine search strategy based on sub-question requirements
        expected_sources = sub_question.get("expected_sources", ["general"])
        search_strategy = sub_question.get("search_strategy", "General search")
        
        prompt = f"""
You are a research information analyst. Your task is to analyze search results and extract relevant, high-quality information for a specific research question.

Research Sub-Question: "{question_text}"
Question ID: {question_id}
Search Strategy: {search_strategy}
Expected Source Types: {expected_sources}

Search Results to Analyze:
{self._format_search_results_for_analysis(relevant_results)}

Please extract and organize the most relevant information:

1. Identify key facts, findings, and insights directly relevant to the sub-question
2. Note the source quality and credibility for each piece of information
3. Extract specific data points, statistics, quotes, and examples
4. Identify any conflicting information or different perspectives
5. Assess the completeness and reliability of the information

Output your analysis in JSON format:
```json
{{
    "sub_question_id": "{question_id}",
    "sub_question": "{question_text}",
    "information_gathered": {{
        "key_findings": [
            {{
                "finding": "Specific finding or fact",
                "source": "Source URL or reference",
                "source_type": "web|academic|news|official",
                "credibility_score": 0.0-1.0,
                "relevance_score": 0.0-1.0,
                "supporting_evidence": "Evidence or context",
                "extracted_date": "{datetime.now().isoformat()}"
            }}
        ],
        "data_points": [
            {{
                "metric": "Name of metric/statistic",
                "value": "Actual value",
                "unit": "Unit of measurement",
                "source": "Source reference",
                "context": "Context for the data point",
                "date": "Date of data if available"
            }}
        ],
        "expert_opinions": [
            {{
                "expert": "Expert name or organization",
                "opinion": "Expert's opinion or quote",
                "source": "Source reference",
                "expertise_area": "Area of expertise",
                "credibility": "high|medium|low"
            }}
        ],
        "conflicting_information": [
            {{
                "topic": "Topic where conflict exists",
                "perspectives": [
                    {{
                        "perspective": "One viewpoint",
                        "source": "Source reference",
                        "evidence": "Supporting evidence"
                    }}
                ],
                "resolution_needed": true|false
            }}
        ]
    }},
    "source_analysis": {{
        "total_sources_analyzed": 0,
        "source_breakdown": {{
            "web": 0,
            "academic": 0, 
            "news": 0,
            "official": 0,
            "other": 0
        }},
        "quality_assessment": {{
            "high_quality": 0,
            "medium_quality": 0,
            "low_quality": 0,
            "average_credibility": 0.0-1.0
        }},
        "coverage_assessment": {{
            "comprehensive": true|false,
            "gaps_identified": ["Gap 1", "Gap 2"],
            "additional_research_needed": true|false
        }}
    }},
    "research_status": {{
        "completeness_score": 0.0-1.0,
        "confidence_level": "high|medium|low",
        "information_quality": "excellent|good|fair|poor",
        "ready_for_synthesis": true|false,
        "next_steps": ["Step 1", "Step 2"]
    }}
}}
```

Focus on extracting factual, verifiable information that directly addresses the research sub-question.
"""
        
        try:
            logger.info("🤖 MultiSourceInformationGathererNode: Calling LLM for information analysis")
            response = call_llm(prompt)
            
            # Extract JSON from response
            json_str = response.split("```json")[1].split("```")[0].strip()
            information = json.loads(json_str)
            
            logger.info("✅ MultiSourceInformationGathererNode: Successfully parsed information")
            
            # Validate and enhance the information
            information = self._validate_information(information, sub_question)
            
            return information
            
        except (IndexError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ MultiSourceInformationGathererNode: Error parsing LLM response: {e}")
            logger.error(f"📄 MultiSourceInformationGathererNode: Raw response: {response}")
            
            # Return fallback information
            return self._get_fallback_information(sub_question, relevant_results)
        
        except Exception as e:
            logger.error(f"❌ MultiSourceInformationGathererNode: Unexpected error: {e}")
            raise
    
    def _extract_relevant_search_results(self, question_text: str, search_results: List[Dict]) -> List[Dict]:
        """Extract search results most relevant to the current question"""
        if not search_results:
            return []
        
        # Simple relevance filtering based on keyword matching
        question_keywords = set(re.findall(r'\b\w+\b', question_text.lower()))
        relevant_results = []
        
        for result in search_results:
            # Check title and snippet for keyword matches
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            content = f"{title} {snippet}"
            
            # Count keyword matches
            content_words = set(re.findall(r'\b\w+\b', content))
            matches = len(question_keywords.intersection(content_words))
            
            if matches > 0:
                result["relevance_score"] = matches / len(question_keywords)
                relevant_results.append(result)
        
        # Sort by relevance and take top results
        relevant_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return relevant_results[:10]  # Limit to top 10 relevant results
    
    def _format_search_results_for_analysis(self, search_results: List[Dict]) -> str:
        """Format search results for LLM analysis"""
        if not search_results:
            return "No search results available"
        
        formatted_results = []
        for i, result in enumerate(search_results[:5], 1):  # Limit to top 5 for prompt
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No snippet")
            url = result.get("url", "No URL")
            source_type = result.get("source_type", "web")
            
            formatted_results.append(f"""
Result {i}:
Title: {title}
Source: {url}
Type: {source_type}
Content: {snippet}
""")
        
        return "\n".join(formatted_results)
    
    def _get_empty_information(self, sub_question: Dict[str, Any]) -> Dict[str, Any]:
        """Return empty information structure"""
        return {
            "sub_question_id": sub_question.get("id", "unknown"),
            "sub_question": sub_question.get("question", ""),
            "information_gathered": {
                "key_findings": [],
                "data_points": [],
                "expert_opinions": [],
                "conflicting_information": []
            },
            "source_analysis": {
                "total_sources_analyzed": 0,
                "source_breakdown": {"web": 0, "academic": 0, "news": 0, "official": 0, "other": 0},
                "quality_assessment": {"high_quality": 0, "medium_quality": 0, "low_quality": 0, "average_credibility": 0.0},
                "coverage_assessment": {"comprehensive": False, "gaps_identified": ["No search results"], "additional_research_needed": True}
            },
            "research_status": {
                "completeness_score": 0.0,
                "confidence_level": "low",
                "information_quality": "poor",
                "ready_for_synthesis": False,
                "next_steps": ["Obtain search results"]
            },
            "status": "empty_question"
        }
    
    def _get_no_results_information(self, sub_question: Dict[str, Any]) -> Dict[str, Any]:
        """Return information structure when no relevant results found"""
        return {
            "sub_question_id": sub_question.get("id", "unknown"),
            "sub_question": sub_question.get("question", ""),
            "information_gathered": {
                "key_findings": [],
                "data_points": [],
                "expert_opinions": [],
                "conflicting_information": []
            },
            "source_analysis": {
                "total_sources_analyzed": 0,
                "source_breakdown": {"web": 0, "academic": 0, "news": 0, "official": 0, "other": 0},
                "quality_assessment": {"high_quality": 0, "medium_quality": 0, "low_quality": 0, "average_credibility": 0.0},
                "coverage_assessment": {"comprehensive": False, "gaps_identified": ["No relevant search results"], "additional_research_needed": True}
            },
            "research_status": {
                "completeness_score": 0.0,
                "confidence_level": "low",
                "information_quality": "poor",
                "ready_for_synthesis": False,
                "next_steps": ["Perform targeted search", "Revise search strategy"]
            },
            "status": "no_relevant_results"
        }
    
    def _get_fallback_information(self, sub_question: Dict[str, Any], search_results: List[Dict]) -> Dict[str, Any]:
        """Return fallback information when LLM parsing fails"""
        logger.info("🔄 MultiSourceInformationGathererNode: Creating fallback information")
        
        # Extract basic information from search results
        key_findings = []
        for result in search_results[:3]:
            key_findings.append({
                "finding": result.get("snippet", "Information available from search results"),
                "source": result.get("url", "Unknown source"),
                "source_type": result.get("source_type", "web"),
                "credibility_score": 0.5,
                "relevance_score": result.get("relevance_score", 0.5),
                "supporting_evidence": result.get("title", ""),
                "extracted_date": datetime.now().isoformat()
            })
        
        return {
            "sub_question_id": sub_question.get("id", "unknown"),
            "sub_question": sub_question.get("question", ""),
            "information_gathered": {
                "key_findings": key_findings,
                "data_points": [],
                "expert_opinions": [],
                "conflicting_information": []
            },
            "source_analysis": {
                "total_sources_analyzed": len(search_results),
                "source_breakdown": {"web": len(search_results), "academic": 0, "news": 0, "official": 0, "other": 0},
                "quality_assessment": {"high_quality": 0, "medium_quality": len(search_results), "low_quality": 0, "average_credibility": 0.5},
                "coverage_assessment": {"comprehensive": False, "gaps_identified": ["LLM analysis failed"], "additional_research_needed": True}
            },
            "research_status": {
                "completeness_score": 0.3,
                "confidence_level": "low",
                "information_quality": "fair",
                "ready_for_synthesis": True,
                "next_steps": ["Manual review recommended"]
            },
            "status": "fallback_extraction"
        }
    
    def _validate_information(self, information: Dict[str, Any], sub_question: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the information structure"""
        # Ensure required sections exist
        required_sections = ["information_gathered", "source_analysis", "research_status"]
        for section in required_sections:
            if section not in information:
                information[section] = {}
        
        # Validate information_gathered structure
        info_gathered = information["information_gathered"]
        required_info_sections = ["key_findings", "data_points", "expert_opinions", "conflicting_information"]
        for section in required_info_sections:
            if section not in info_gathered:
                info_gathered[section] = []
        
        # Ensure sub-question information is preserved
        information["sub_question_id"] = sub_question.get("id", "unknown")
        information["sub_question"] = sub_question.get("question", "")
        
        # Add validation metadata
        information["validation_status"] = "validated"
        information["extracted_date"] = datetime.now().isoformat()
        information["total_findings"] = len(info_gathered.get("key_findings", []))
        
        return information
    
    def post(self, shared: Dict[str, Any], prep_res: tuple, exec_res: Dict[str, Any]) -> str:
        """Store gathered information in shared store"""
        sub_question_id = exec_res.get("sub_question_id", "unknown")
        logger.info(f"💾 MultiSourceInformationGathererNode: post - Storing information for question '{sub_question_id}'")
        
        # Initialize research findings storage if not exists
        if "research_findings" not in shared:
            shared["research_findings"] = {}
        
        # Store information for this sub-question
        shared["research_findings"][sub_question_id] = exec_res
        
        # Update research queue status
        if "research_queue" in shared:
            pending = shared["research_queue"].get("pending", [])
            in_progress = shared["research_queue"].get("in_progress", [])
            completed = shared["research_queue"].get("completed", [])
            
            # Move current question from in_progress to completed
            if sub_question_id in in_progress:
                in_progress.remove(sub_question_id)
            if sub_question_id not in completed:
                completed.append(sub_question_id)
            
            shared["research_queue"]["in_progress"] = in_progress
            shared["research_queue"]["completed"] = completed
        
        # Update research metadata
        if "research_metadata" not in shared:
            shared["research_metadata"] = {}
        
        shared["research_metadata"]["completed_sub_questions"] = len(shared["research_findings"])
        shared["research_metadata"]["last_completed"] = sub_question_id
        shared["research_metadata"]["information_quality"] = exec_res.get("research_status", {}).get("information_quality", "unknown")
        
        # Check if all research is complete
        total_questions = shared["research_metadata"].get("total_sub_questions", 0)
        completed_questions = len(shared["research_findings"])
        
        if completed_questions >= total_questions and total_questions > 0:
            shared["research_metadata"]["all_research_complete"] = True
            logger.info("🎉 MultiSourceInformationGathererNode: All research sub-questions completed!")
        
        logger.info(f"✅ MultiSourceInformationGathererNode: Stored information with {exec_res.get('total_findings', 0)} findings")
        
        return "default"