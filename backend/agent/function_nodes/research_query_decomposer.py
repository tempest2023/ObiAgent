from pocketflow import Node
from typing import Dict, List, Any, Optional
from agent.utils.stream_llm import call_llm
import logging
import json

logger = logging.getLogger(__name__)

class ResearchQueryDecomposerNode(Node):
    """
    Node to decompose complex research questions into manageable sub-questions
    that can be researched systematically. This is the first step in deep research.
    
    Example:
        >>> node = ResearchQueryDecomposerNode()
        >>> shared = {"research_question": "How is AI transforming healthcare?", "research_depth": "comprehensive"}
        >>> node.prep(shared)
        # Returns (research_question, research_depth, context)
        >>> node.exec(("How is AI transforming healthcare?", "comprehensive", {}))
        # Returns structured decomposition with sub-questions, search strategies, and priorities
    """
    
    def prep(self, shared: Dict[str, Any]) -> tuple:
        """Prepare research question and context for decomposition"""
        research_question = shared.get("research_question", "")
        research_depth = shared.get("research_depth", "standard")  # standard, comprehensive, focused
        research_context = shared.get("research_context", {})
        
        logger.info(f"🔄 ResearchQueryDecomposerNode: prep - question='{research_question[:100]}...', depth='{research_depth}'")
        
        if not research_question:
            logger.warning("⚠️ ResearchQueryDecomposerNode: No research question provided")
            
        return research_question, research_depth, research_context
    
    def exec(self, inputs: tuple) -> Dict[str, Any]:
        """Decompose research question into structured sub-questions and search strategy"""
        research_question, research_depth, research_context = inputs
        
        logger.info(f"🔄 ResearchQueryDecomposerNode: exec - decomposing '{research_question[:50]}...'")
        
        if not research_question.strip():
            logger.warning("⚠️ ResearchQueryDecomposerNode: Empty research question")
            return self._get_empty_decomposition(research_question)
        
        # Determine decomposition strategy based on depth
        depth_instructions = {
            "focused": "Create 3-5 focused sub-questions for targeted research",
            "standard": "Create 5-8 sub-questions covering main aspects of the topic", 
            "comprehensive": "Create 8-12 sub-questions for thorough, multi-faceted research"
        }
        
        instruction = depth_instructions.get(research_depth, depth_instructions["standard"])
        
        # Include context if available
        context_text = ""
        if research_context:
            context_text = f"""
Research Context:
- Domain: {research_context.get('domain', 'General')}
- Time Period: {research_context.get('time_period', 'Current')}
- Geographic Focus: {research_context.get('geographic_focus', 'Global')}
- Specific Requirements: {research_context.get('requirements', 'None specified')}
"""
        
        prompt = f"""
You are a research strategist helping to decompose a complex research question into manageable sub-questions.

Main Research Question: "{research_question}"
Research Depth: {research_depth}
Instruction: {instruction}

{context_text}

Please decompose this research question systematically:

1. Analyze the main question and identify key dimensions to explore
2. Create specific, searchable sub-questions that together comprehensively address the main question
3. Suggest appropriate search strategies for each sub-question
4. Prioritize the sub-questions by importance and dependency
5. Identify what types of sources would be most valuable

Output your response in JSON format:
```json
{{
    "main_question": "{research_question}",
    "research_scope": {{
        "primary_focus": "Main focus area",
        "secondary_aspects": ["Aspect 1", "Aspect 2"],
        "research_boundaries": "What this research will and won't cover"
    }},
    "sub_questions": [
        {{
            "id": "q1",
            "question": "Specific sub-question",
            "rationale": "Why this question is important",
            "search_strategy": "How to search for this information",
            "priority": "high|medium|low",
            "depends_on": ["q0"],
            "expected_sources": ["academic", "industry", "news", "official"]
        }}
    ],
    "research_strategy": {{
        "recommended_order": ["q1", "q2", "q3"],
        "parallel_tracks": [["q1", "q2"], ["q3", "q4"]],
        "estimated_time": "Expected research duration",
        "key_challenges": ["Challenge 1", "Challenge 2"]
    }},
    "quality_criteria": {{
        "source_requirements": "Minimum source quality standards",
        "recency_requirements": "How recent information needs to be",
        "geographic_coverage": "Geographic scope needed",
        "completeness_threshold": "What constitutes complete research"
    }}
}}
```

Ensure each sub-question is:
- Specific and searchable
- Contributes uniquely to answering the main question
- Can be researched independently
- Has clear success criteria
"""
        
        try:
            logger.info("🤖 ResearchQueryDecomposerNode: Calling LLM for query decomposition")
            response = call_llm(prompt)
            
            # Extract JSON from response
            json_str = response.split("```json")[1].split("```")[0].strip()
            decomposition = json.loads(json_str)
            
            logger.info("✅ ResearchQueryDecomposerNode: Successfully parsed decomposition")
            
            # Validate and enhance the decomposition
            decomposition = self._validate_decomposition(decomposition, research_question)
            
            return decomposition
            
        except (IndexError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ ResearchQueryDecomposerNode: Error parsing LLM response: {e}")
            logger.error(f"📄 ResearchQueryDecomposerNode: Raw response: {response}")
            
            # Return fallback decomposition
            return self._get_fallback_decomposition(research_question, research_depth)
        
        except Exception as e:
            logger.error(f"❌ ResearchQueryDecomposerNode: Unexpected error: {e}")
            raise
    
    def _get_empty_decomposition(self, research_question: str) -> Dict[str, Any]:
        """Return empty decomposition structure"""
        return {
            "main_question": research_question,
            "research_scope": {
                "primary_focus": "Unknown",
                "secondary_aspects": [],
                "research_boundaries": "No question provided"
            },
            "sub_questions": [],
            "research_strategy": {
                "recommended_order": [],
                "parallel_tracks": [],
                "estimated_time": "Unknown",
                "key_challenges": ["No research question provided"]
            },
            "quality_criteria": {
                "source_requirements": "Standard",
                "recency_requirements": "Recent",
                "geographic_coverage": "Global",
                "completeness_threshold": "Basic"
            },
            "status": "empty_question"
        }
    
    def _get_fallback_decomposition(self, research_question: str, research_depth: str) -> Dict[str, Any]:
        """Return fallback decomposition when LLM parsing fails"""
        logger.info("🔄 ResearchQueryDecomposerNode: Creating fallback decomposition")
        
        # Create simple decomposition based on common research patterns
        fallback_questions = [
            {
                "id": "q1",
                "question": f"What is {research_question.split('?')[0].lower()}?",
                "rationale": "Basic definition and overview",
                "search_strategy": "Search for definitions and overviews",
                "priority": "high",
                "depends_on": [],
                "expected_sources": ["academic", "official"]
            },
            {
                "id": "q2", 
                "question": f"What are the current trends related to {research_question.split('?')[0].lower()}?",
                "rationale": "Current state and developments",
                "search_strategy": "Search for recent news and reports",
                "priority": "medium",
                "depends_on": ["q1"],
                "expected_sources": ["news", "industry"]
            },
            {
                "id": "q3",
                "question": f"What are the implications and future outlook for {research_question.split('?')[0].lower()}?",
                "rationale": "Future considerations and impact",
                "search_strategy": "Search for analysis and predictions",
                "priority": "medium",
                "depends_on": ["q1", "q2"],
                "expected_sources": ["academic", "industry"]
            }
        ]
        
        return {
            "main_question": research_question,
            "research_scope": {
                "primary_focus": "General research topic",
                "secondary_aspects": ["Current state", "Trends", "Future outlook"],
                "research_boundaries": "Basic coverage of the topic"
            },
            "sub_questions": fallback_questions,
            "research_strategy": {
                "recommended_order": ["q1", "q2", "q3"],
                "parallel_tracks": [["q2", "q3"]],
                "estimated_time": "2-4 hours",
                "key_challenges": ["LLM decomposition failed, using fallback"]
            },
            "quality_criteria": {
                "source_requirements": "Reliable sources preferred",
                "recency_requirements": "Within last 2 years",
                "geographic_coverage": "Global perspective",
                "completeness_threshold": "Basic understanding"
            },
            "status": "fallback_decomposition"
        }
    
    def _validate_decomposition(self, decomposition: Dict[str, Any], research_question: str) -> Dict[str, Any]:
        """Validate and clean the decomposition structure"""
        # Ensure main question is preserved
        decomposition["main_question"] = research_question
        
        # Validate required sections exist
        required_sections = ["research_scope", "sub_questions", "research_strategy", "quality_criteria"]
        for section in required_sections:
            if section not in decomposition:
                decomposition[section] = {}
        
        # Validate sub_questions structure
        if not isinstance(decomposition["sub_questions"], list):
            decomposition["sub_questions"] = []
        
        # Ensure each sub-question has required fields
        for i, sq in enumerate(decomposition["sub_questions"]):
            if not isinstance(sq, dict):
                continue
            
            # Add missing fields with defaults
            sq.setdefault("id", f"q{i+1}")
            sq.setdefault("question", "Missing question")
            sq.setdefault("rationale", "No rationale provided")
            sq.setdefault("search_strategy", "General search")
            sq.setdefault("priority", "medium")
            sq.setdefault("depends_on", [])
            sq.setdefault("expected_sources", ["general"])
        
        # Add validation status
        decomposition["validation_status"] = "validated"
        decomposition["sub_question_count"] = len(decomposition["sub_questions"])
        return decomposition
    
    def post(self, shared: Dict[str, Any], prep_res: tuple, exec_res: Dict[str, Any]) -> str:
        """Store research decomposition in shared store"""
        logger.info(f"💾 ResearchQueryDecomposerNode: post - Storing decomposition for '{exec_res.get('main_question', 'Unknown')[:50]}...'")
        
        shared["research_decomposition"] = exec_res
        
        # Extract key information for easy access by downstream nodes
        shared["sub_questions"] = exec_res.get("sub_questions", [])
        shared["research_strategy"] = exec_res.get("research_strategy", {})
        shared["research_scope"] = exec_res.get("research_scope", {})
        
        # Create search queue for systematic research
        recommended_order = exec_res.get("research_strategy", {}).get("recommended_order", [])
        parallel_tracks = exec_res.get("research_strategy", {}).get("parallel_tracks", [])
        
        shared["research_queue"] = {
            "pending": recommended_order.copy(),
            "in_progress": [],
            "completed": [],
            "parallel_tracks": parallel_tracks
        }
        
        # Store research metadata
        shared["research_metadata"] = {
            "total_sub_questions": len(exec_res.get("sub_questions", [])),
            "research_depth": prep_res[1],  # from prep
            "estimated_time": exec_res.get("research_strategy", {}).get("estimated_time", "Unknown"),
            "decomposition_status": exec_res.get("status", "success")
        }
        
        logger.info(f"✅ ResearchQueryDecomposerNode: Stored decomposition with {len(exec_res.get('sub_questions', []))} sub-questions")
        
        return "default"