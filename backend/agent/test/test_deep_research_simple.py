#!/usr/bin/env python3
"""
Simplified test runner for deep research nodes.
Can be run directly without pytest or complex imports.
"""

import sys
import os
import json
from datetime import datetime
from unittest.mock import Mock, patch

# Add the workspace root directory to the path to find pocketflow
workspace_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, workspace_root)
# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import nodes directly
from agent.function_nodes.research_query_decomposer import ResearchQueryDecomposerNode
from agent.function_nodes.multi_source_information_gatherer import MultiSourceInformationGathererNode
from agent.function_nodes.information_synthesizer import InformationSynthesizerNode
from agent.function_nodes.citation_manager import CitationManagerNode
from agent.function_nodes.research_report_generator import ResearchReportGeneratorNode

@patch('agent.function_nodes.research_query_decomposer.call_llm')
def test_research_query_decomposer(mock_llm):
    """Test ResearchQueryDecomposerNode basic functionality"""
    print("🧪 Testing ResearchQueryDecomposerNode...")
    
    # Mock LLM response for successful decomposition
    mock_llm.return_value = """
```json
{
    "main_question": "Test question", 
    "research_scope": {"primary_focus": "Test"},
    "sub_questions": [{"id": "q1", "question": "Sub-question 1"}],
    "research_strategy": {"recommended_order": ["q1"]},
    "quality_criteria": {}
}
```"""
    
    node = ResearchQueryDecomposerNode()
    
    # Test prep method
    shared = {
        "research_question": "How is AI transforming healthcare?",
        "research_depth": "comprehensive"
    }
    
    prep_result = node.prep(shared)
    assert prep_result[0] == "How is AI transforming healthcare?"
    assert prep_result[1] == "comprehensive"
    print("✅ Prep method works correctly")
    
    # Test with empty question (should return empty structure)
    inputs = ("", "standard", {})
    result = node.exec(inputs)
    assert result["status"] == "empty_question"
    assert len(result["sub_questions"]) == 0
    print("✅ Empty question handling works")
    
    # Test successful decomposition (should call LLM)
    inputs = ("Test question", "standard", {})
    result = node.exec(inputs)
    assert result["main_question"] == "Test question"
    assert len(result["sub_questions"]) == 1
    print("✅ LLM decomposition works")
    
    # Test fallback decomposition (mock LLM to return invalid JSON)
    mock_llm.return_value = "Invalid JSON response"
    inputs = ("Test question", "standard", {})
    result = node.exec(inputs)
    assert result["status"] == "fallback_decomposition"
    assert len(result["sub_questions"]) == 3
    print("✅ Fallback decomposition works")
    
    # Test post method
    shared = {}
    exec_res = {
        "main_question": "Test question",
        "sub_questions": [{"id": "q1", "question": "Test"}],
        "research_strategy": {"recommended_order": ["q1"]},
        "research_scope": {"primary_focus": "Test"}
    }
    
    action = node.post(shared, prep_result, exec_res)
    assert action == "default"
    assert "research_decomposition" in shared
    assert "research_queue" in shared
    print("✅ Post method stores data correctly")
    
    print("🎉 ResearchQueryDecomposerNode: ALL TESTS PASSED\n")

@patch('agent.function_nodes.multi_source_information_gatherer.call_llm')
def test_multi_source_information_gatherer(mock_llm):
    """Test MultiSourceInformationGathererNode basic functionality"""
    print("🧪 Testing MultiSourceInformationGathererNode...")
    
    # Mock LLM response
    mock_llm.return_value = """
```json
{
    "sub_question_id": "q1",
    "sub_question": "Test question",
    "information_gathered": {
        "key_findings": [{"finding": "Test finding", "source": "test.com"}],
        "data_points": [],
        "expert_opinions": [],
        "conflicting_information": []
    },
    "source_analysis": {
        "total_sources_analyzed": 1,
        "source_breakdown": {"web": 1, "academic": 0, "news": 0, "official": 0, "other": 0},
        "quality_assessment": {"high_quality": 0, "medium_quality": 1, "low_quality": 0, "average_credibility": 0.5},
        "coverage_assessment": {"comprehensive": false, "gaps_identified": [], "additional_research_needed": false}
    },
    "research_status": {
        "completeness_score": 0.7,
        "confidence_level": "medium",
        "information_quality": "good",
        "ready_for_synthesis": true,
        "next_steps": []
    }
}
```"""
    
    node = MultiSourceInformationGathererNode()
    
    # Test prep method
    shared = {
        "current_sub_question": {"id": "q1", "question": "Test question"},
        "search_results": [{"title": "Test", "url": "test.com"}]
    }
    
    prep_result = node.prep(shared)
    assert prep_result[0]["id"] == "q1"
    print("✅ Prep method works correctly")
    
    # Test with no search results
    inputs = ({"id": "q1", "question": "Test"}, ["web"], [], {})
    result = node.exec(inputs)
    assert result["status"] == "no_relevant_results"
    print("✅ No results handling works")
    
    # Test with search results (should call LLM)
    search_results = [{"title": "Artificial Intelligence", "url": "test.com", "snippet": "Artificial intelligence is used in medical applications"}]
    # Patch the mock_llm to return a response with key findings for this input
    mock_llm.return_value = """
```json
{
    "sub_question_id": "q1",
    "sub_question": "artificial intelligence",
    "information_gathered": {
        "key_findings": [{"finding": "AI is used in medical applications", "source": "test.com"}],
        "data_points": [],
        "expert_opinions": [],
        "conflicting_information": []
    },
    "source_analysis": {
        "total_sources_analyzed": 1,
        "source_breakdown": {"web": 1, "academic": 0, "news": 0, "official": 0, "other": 0},
        "quality_assessment": {"high_quality": 0, "medium_quality": 1, "low_quality": 0, "average_credibility": 0.5},
        "coverage_assessment": {"comprehensive": false, "gaps_identified": [], "additional_research_needed": false}
    },
    "research_status": {
        "completeness_score": 0.7,
        "confidence_level": "medium",
        "information_quality": "good",
        "ready_for_synthesis": true,
        "next_steps": []
    }
}
```
"""
    inputs = ({"id": "q1", "question": "artificial intelligence"}, ["web"], search_results, {})
    result = node.exec(inputs)
    assert result["sub_question_id"] == "q1"
    assert len(result["information_gathered"]["key_findings"]) > 0
    print("✅ LLM information gathering works")
    
    # Test relevance filtering
    question_text = "artificial intelligence medical"
    search_results = [
        {"title": "AI in Medicine", "snippet": "AI medical applications", "url": "test1.com"},
        {"title": "Cooking", "snippet": "Best recipes", "url": "test2.com"}
    ]
    
    relevant = node._extract_relevant_search_results(question_text, search_results)
    assert len(relevant) == 1  # Should filter out cooking
    assert relevant[0]["url"] == "test1.com"
    print("✅ Search result filtering works")
    
    print("🎉 MultiSourceInformationGathererNode: ALL TESTS PASSED\n")

@patch('agent.function_nodes.information_synthesizer.call_llm')
def test_information_synthesizer(mock_llm):
    """Test InformationSynthesizerNode basic functionality"""
    print("🧪 Testing InformationSynthesizerNode...")
    
    # Mock LLM response
    mock_llm.return_value = """
```json
{
    "main_question": "Test question?",
    "synthesis_overview": {
        "primary_answer": "Test answer based on research",
        "confidence_level": "high",
        "evidence_strength": "strong",
        "completeness_assessment": "comprehensive"
    },
    "key_insights": [
        {
            "insight": "Key insight from research",
            "supporting_evidence": ["Evidence 1"],
            "sources": ["Source 1"],
            "confidence": "high",
            "importance": "critical",
            "sub_questions_addressed": ["q1"]
        }
    ],
    "thematic_analysis": {
        "major_themes": [{"theme": "Test Theme", "description": "Theme description"}],
        "cross_cutting_patterns": []
    },
    "conflict_resolution": [],
    "evidence_assessment": {
        "total_sources_analyzed": 1,
        "source_quality_distribution": {"high_quality": 1, "medium_quality": 0, "low_quality": 0}
    },
    "research_gaps": [],
    "conclusions": {
        "primary_conclusions": [{"conclusion": "Test conclusion"}],
        "implications": [],
        "recommendations": []
    },
    "synthesis_metadata": {
        "total_sub_questions_analyzed": 1,
        "quality_score": 0.9
    }
}
```"""
    
    node = InformationSynthesizerNode()
    
    # Test prep method
    shared = {
        "research_findings": {"q1": {"sub_question": "Test"}},
        "research_scope": {"primary_focus": "Healthcare"},
        "research_question": "Test question?"
    }
    
    prep_result = node.prep(shared)
    assert len(prep_result[0]) == 1  # research_findings
    assert prep_result[2] == "Test question?"
    print("✅ Prep method works correctly")
    
    # Test with empty findings
    inputs = ({}, {}, "Test question", {})
    result = node.exec(inputs)
    assert result["status"] == "empty_findings"
    print("✅ Empty findings handling works")
    
    # Test with research findings (should call LLM)
    research_findings = {
        "q1": {
            "sub_question": "Test question",
            "information_gathered": {"key_findings": [{"finding": "Important finding"}]},
            "research_status": {"information_quality": "good"}
        }
    }
    inputs = (research_findings, {"primary_focus": "Healthcare"}, "Test question?", {})
    result = node.exec(inputs)
    assert result["main_question"] == "Test question?"
    assert len(result["key_insights"]) > 0
    print("✅ LLM synthesis works")
    
    # Test research findings structuring
    structured = node._structure_research_findings(research_findings)
    assert "Test question" in structured
    assert "Important finding" in structured
    print("✅ Research findings structuring works")
    
    print("🎉 InformationSynthesizerNode: ALL TESTS PASSED\n")

@patch('agent.function_nodes.citation_manager.call_llm')
def test_citation_manager(mock_llm):
    """Test CitationManagerNode basic functionality"""
    print("🧪 Testing CitationManagerNode...")
    
    # Mock LLM response
    mock_llm.return_value = """
```json
{
    "citation_style": "apa",
    "citation_database": [
        {
            "citation_id": "source_1",
            "formatted_citation": "Test Citation (2024). Test Source.",
            "in_text_citation": "(Test, 2024)",
            "source_type": "web",
            "url": "https://test.com",
            "title": "Test Source",
            "author": "Test Author",
            "credibility_assessment": {
                "credibility_score": 0.8,
                "credibility_level": "high"
            }
        }
    ],
    "citation_summary": {
        "total_sources": 1,
        "source_type_breakdown": {"web": 1, "academic": 0, "news": 0, "official": 0, "other": 0}
    },
    "citation_quality_assessment": {
        "overall_quality": "good"
    },
    "bibliography": {
        "formatted_bibliography": "Test Citation (2024). Test Source."
    },
    "citation_guidelines": {
        "in_text_usage": "Use (Author, Year) format"
    },
    "metadata": {
        "citation_count": 1
    }
}
```"""
    
    node = CitationManagerNode()
    
    # Test prep method
    shared = {
        "research_findings": {"q1": {"information_gathered": {"key_findings": []}}},
        "search_results": [{"url": "test.com", "title": "Test"}],
        "citation_style": "apa"
    }
    
    prep_result = node.prep(shared)
    assert prep_result[3] == "apa"  # citation_style
    print("✅ Prep method works correctly")
    
    # Test with no sources
    inputs = ({}, [], {}, "apa", {})
    result = node.exec(inputs)
    assert result["status"] == "no_sources"
    assert len(result["citation_database"]) == 0
    print("✅ No sources handling works")
    
    # Test with sources (should call LLM)
    research_findings = {
        "q1": {
            "information_gathered": {
                "key_findings": [{"source": "https://academic.com", "finding": "Test"}]
            }
        }
    }
    search_results = [{"url": "https://news.com", "title": "News"}]
    inputs = (research_findings, search_results, {}, "apa", {})
    result = node.exec(inputs)
    assert result["citation_style"] == "apa"
    assert len(result["citation_database"]) > 0
    print("✅ LLM citation generation works")
    
    # Test source extraction
    sources = node._extract_all_sources(research_findings, search_results)
    assert len(sources) == 2  # 1 from research + 1 from search
    urls = [source["url"] for source in sources]
    assert "https://academic.com" in urls
    assert "https://news.com" in urls
    print("✅ Source extraction works")
    
    print("🎉 CitationManagerNode: ALL TESTS PASSED\n")

@patch('agent.function_nodes.research_report_generator.call_llm')
def test_research_report_generator(mock_llm):
    """Test ResearchReportGeneratorNode basic functionality"""
    print("🧪 Testing ResearchReportGeneratorNode...")
    
    # Mock LLM response
    mock_llm.return_value = """
```json
{
    "report_metadata": {
        "title": "Test Research Report",
        "research_question": "Test question?",
        "report_type": "comprehensive",
        "target_audience": "general",
        "word_count_estimate": 1000,
        "section_count": 3
    },
    "executive_summary": {
        "key_question": "Test question?",
        "primary_findings": "Test findings based on research",
        "key_insights": ["Insight 1", "Insight 2"],
        "main_conclusions": "Test conclusions",
        "confidence_assessment": "high"
    },
    "report_sections": [
        {
            "section_id": "introduction",
            "section_title": "Introduction",
            "section_number": 1,
            "content": "Test introduction content",
            "subsections": [],
            "citations_used": [],
            "word_count": 200
        },
        {
            "section_id": "findings",
            "section_title": "Research Findings",
            "section_number": 2,
            "content": "Test findings content",
            "subsections": [],
            "citations_used": [],
            "word_count": 400
        }
    ],
    "appendices": [],
    "quality_assessment": {
        "content_quality": "good",
        "citation_quality": "good",
        "structure_quality": "good"
    },
    "report_statistics": {
        "total_word_count": 1000,
        "total_sections": 2,
        "total_citations": 0
    }
}
```"""
    
    node = ResearchReportGeneratorNode()
    
    # Test prep method with defaults
    shared = {"research_synthesis": {}, "citations": {}}
    prep_result = node.prep(shared)
    
    report_config = prep_result[3]
    assert report_config["report_type"] == "comprehensive"
    assert report_config["target_audience"] == "general"
    assert report_config["include_methodology"] == True
    print("✅ Prep method applies defaults correctly")
    
    # Test with no synthesis data
    inputs = ({}, {}, {}, {"report_type": "brief"}, "Test question?")
    result = node.exec(inputs)
    assert result["status"] == "insufficient_data"
    assert len(result["report_sections"]) == 1  # Notice section only
    print("✅ No synthesis data handling works")
    
    # Test with synthesis data (should call LLM)
    research_synthesis = {
        "synthesis_overview": {"primary_answer": "Test answer"},
        "key_insights": [{"insight": "Test insight"}],
        "conclusions": {"primary_conclusions": []}
    }
    citations = {"citation_database": []}
    inputs = (research_synthesis, citations, {}, {"report_type": "comprehensive"}, "Test question?")
    result = node.exec(inputs)
    assert result["report_metadata"]["title"] == "Test Research Report"
    assert len(result["report_sections"]) > 0
    print("✅ LLM report generation works")
    
    # Test citation lookup preparation
    citations = {
        "citation_database": [
            {"citation_id": "test_1", "in_text_citation": "(Test, 2024)"},
            {"citation_id": "test_2", "in_text_citation": "(Example, 2023)"}
        ]
    }
    
    lookup = node._prepare_citation_lookup(citations)
    assert len(lookup) == 2
    assert lookup["test_1"] == "(Test, 2024)"
    assert lookup["test_2"] == "(Example, 2023)"
    print("✅ Citation lookup preparation works")
    
    # Test formatted report text creation
    report = {
        "report_metadata": {
            "title": "Test Report",
            "research_question": "Test question?",
            "generation_date": "2024-01-15"
        },
        "executive_summary": {"primary_findings": "Test findings"},
        "report_sections": [
            {
                "section_title": "Introduction",
                "section_number": 1,
                "content": "Test introduction",
                "subsections": []
            }
        ],
        "report_statistics": {"total_word_count": 100, "total_sections": 1}
    }
    
    formatted = node._create_formatted_report_text(report)
    assert "# Test Report" in formatted
    assert "Test question?" in formatted
    assert "## 1. Introduction" in formatted
    print("✅ Formatted report text creation works")
    
    print("🎉 ResearchReportGeneratorNode: ALL TESTS PASSED\n")

def test_workflow_integration():
    """Test basic workflow integration between nodes"""
    print("🧪 Testing Workflow Integration...")
    
    # Test that nodes have compatible data structures
    shared = {
        "research_question": "How is AI transforming healthcare?",
        "research_depth": "comprehensive",
        "search_results": [
            {"url": "https://example.com", "title": "AI Healthcare", "snippet": "AI transforms healthcare..."}
        ],
        "citation_style": "apa"
    }
    
    # Test all nodes can prep without errors
    decomposer = ResearchQueryDecomposerNode()
    gatherer = MultiSourceInformationGathererNode()
    synthesizer = InformationSynthesizerNode()
    citation_manager = CitationManagerNode()
    report_generator = ResearchReportGeneratorNode()
    
    # Test decomposer
    decomposer_prep = decomposer.prep(shared)
    assert isinstance(decomposer_prep, tuple)
    print("✅ Decomposer prep works")
    
    # Add mock data for downstream nodes
    shared["research_decomposition"] = {"sub_questions": [{"id": "q1", "question": "Test"}]}
    shared["current_sub_question"] = {"id": "q1", "question": "Test"}
    
    # Test gatherer
    gatherer_prep = gatherer.prep(shared)
    assert isinstance(gatherer_prep, tuple)
    print("✅ Gatherer prep works")
    
    # Add mock research findings
    shared["research_findings"] = {"q1": {"information_gathered": {"key_findings": []}}}
    
    # Test synthesizer
    synthesizer_prep = synthesizer.prep(shared)
    assert isinstance(synthesizer_prep, tuple)
    print("✅ Synthesizer prep works")
    
    # Test citation manager
    citation_prep = citation_manager.prep(shared)
    assert isinstance(citation_prep, tuple)
    print("✅ Citation manager prep works")
    
    # Add mock synthesis for report generator
    shared["research_synthesis"] = {"synthesis_overview": {}, "key_insights": []}
    shared["citations"] = {"citation_database": []}
    
    # Test report generator
    report_prep = report_generator.prep(shared)
    assert isinstance(report_prep, tuple)
    print("✅ Report generator prep works")
    
    print("🎉 Workflow Integration: ALL TESTS PASSED\n")

def main():
    """Run all tests"""
    print("🚀 Starting Deep Research Nodes Test Suite\n")
    print("=" * 60)
    
    try:
        test_research_query_decomposer()
        test_multi_source_information_gatherer()
        test_information_synthesizer()
        test_citation_manager()
        test_research_report_generator()
        test_workflow_integration()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED! Deep Research Nodes are working correctly.")
        print("✅ Ready for production use!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())