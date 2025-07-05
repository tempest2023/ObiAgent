import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

# Import the nodes to test
from agent.function_nodes.research_query_decomposer import ResearchQueryDecomposerNode
from agent.function_nodes.multi_source_information_gatherer import MultiSourceInformationGathererNode
from agent.function_nodes.information_synthesizer import InformationSynthesizerNode
from agent.function_nodes.citation_manager import CitationManagerNode
from agent.function_nodes.research_report_generator import ResearchReportGeneratorNode


class TestResearchQueryDecomposerNode(unittest.TestCase):
    """Test cases for ResearchQueryDecomposerNode"""
    
    def setUp(self):
        self.node = ResearchQueryDecomposerNode()
        self.mock_llm_response = """
```json
{
    "main_question": "How is AI transforming healthcare?",
    "research_scope": {
        "primary_focus": "Healthcare AI applications",
        "secondary_aspects": ["Medical diagnosis", "Treatment planning", "Drug discovery"],
        "research_boundaries": "Focus on current and near-term applications"
    },
    "sub_questions": [
        {
            "id": "q1",
            "question": "What are the current applications of AI in medical diagnosis?",
            "rationale": "Understanding current state of AI in diagnosis",
            "search_strategy": "Search for recent medical AI applications",
            "priority": "high",
            "depends_on": [],
            "expected_sources": ["academic", "medical"]
        },
        {
            "id": "q2", 
            "question": "How is AI being used in drug discovery and development?",
            "rationale": "Understanding AI impact on pharmaceutical research",
            "search_strategy": "Search for pharmaceutical AI research",
            "priority": "medium",
            "depends_on": ["q1"],
            "expected_sources": ["academic", "industry"]
        }
    ],
    "research_strategy": {
        "recommended_order": ["q1", "q2"],
        "parallel_tracks": [["q1"], ["q2"]],
        "estimated_time": "4-6 hours",
        "key_challenges": ["Technical complexity", "Rapid evolution"]
    },
    "quality_criteria": {
        "source_requirements": "Peer-reviewed sources preferred",
        "recency_requirements": "Within last 3 years",
        "geographic_coverage": "Global perspective",
        "completeness_threshold": "Comprehensive coverage"
    }
}
```
"""
    
    def test_prep_method(self):
        """Test the prep method extracts correct data from shared store"""
        shared = {
            "research_question": "How is AI transforming healthcare?",
            "research_depth": "comprehensive",
            "research_context": {"domain": "healthcare"}
        }
        
        result = self.node.prep(shared)
        
        self.assertEqual(result[0], "How is AI transforming healthcare?")
        self.assertEqual(result[1], "comprehensive")
        self.assertEqual(result[2], {"domain": "healthcare"})
    
    def test_prep_with_defaults(self):
        """Test prep method with missing optional parameters"""
        shared = {"research_question": "Test question"}
        
        result = self.node.prep(shared)
        
        self.assertEqual(result[0], "Test question")
        self.assertEqual(result[1], "standard")  # default depth
        self.assertEqual(result[2], {})  # default context
    
    @patch('agent.function_nodes.research_query_decomposer.call_llm')
    def test_exec_method_success(self, mock_llm):
        """Test successful execution of query decomposition"""
        mock_llm.return_value = self.mock_llm_response
        
        inputs = ("How is AI transforming healthcare?", "comprehensive", {})
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["main_question"], "How is AI transforming healthcare?")
        self.assertIn("sub_questions", result)
        self.assertIn("research_strategy", result)
        self.assertEqual(len(result["sub_questions"]), 2)
    
    @patch('agent.function_nodes.research_query_decomposer.call_llm')
    def test_exec_with_empty_question(self, mock_llm):
        """Test execution with empty research question"""
        inputs = ("", "standard", {})
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "empty_question")
        self.assertEqual(len(result["sub_questions"]), 0)
        mock_llm.assert_not_called()
    
    @patch('agent.function_nodes.research_query_decomposer.call_llm')
    def test_exec_llm_failure(self, mock_llm):
        """Test fallback behavior when LLM parsing fails"""
        mock_llm.return_value = "Invalid JSON response"
        
        inputs = ("Test question", "standard", {})
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "fallback_decomposition")
        self.assertEqual(len(result["sub_questions"]), 3)  # fallback creates 3 questions
    
    def test_post_method(self):
        """Test post method stores data correctly in shared store"""
        shared = {}
        prep_res = ("Test question", "standard", {})
        exec_res = {
            "main_question": "Test question",
            "sub_questions": [{"id": "q1", "question": "Test sub-question"}],
            "research_strategy": {"recommended_order": ["q1"]},
            "research_scope": {"primary_focus": "Test"}
        }
        
        action = self.node.post(shared, prep_res, exec_res)
        
        self.assertEqual(action, "default")
        self.assertIn("research_decomposition", shared)
        self.assertIn("sub_questions", shared)
        self.assertIn("research_queue", shared)
        self.assertIn("research_metadata", shared)


class TestMultiSourceInformationGathererNode(unittest.TestCase):
    """Test cases for MultiSourceInformationGathererNode"""
    
    def setUp(self):
        self.node = MultiSourceInformationGathererNode()
        self.mock_llm_response = """
```json
{
    "sub_question_id": "q1",
    "sub_question": "What are current AI applications in medical diagnosis?",
    "information_gathered": {
        "key_findings": [
            {
                "finding": "AI is widely used in radiology for image analysis",
                "source": "https://example.com/ai-radiology",
                "source_type": "academic",
                "credibility_score": 0.9,
                "relevance_score": 0.95,
                "supporting_evidence": "Multiple studies show 95% accuracy",
                "extracted_date": "2024-01-15T10:00:00"
            }
        ],
        "data_points": [
            {
                "metric": "Diagnostic accuracy",
                "value": "95%",
                "unit": "percentage",
                "source": "Medical journal study",
                "context": "AI vs human radiologists",
                "date": "2024"
            }
        ],
        "expert_opinions": [
            {
                "expert": "Dr. Sarah Johnson",
                "opinion": "AI significantly improves diagnostic speed",
                "source": "Medical AI Conference 2024",
                "expertise_area": "Medical AI",
                "credibility": "high"
            }
        ],
        "conflicting_information": []
    },
    "source_analysis": {
        "total_sources_analyzed": 5,
        "source_breakdown": {"academic": 3, "news": 1, "web": 1, "official": 0, "other": 0},
        "quality_assessment": {"high_quality": 3, "medium_quality": 2, "low_quality": 0, "average_credibility": 0.85},
        "coverage_assessment": {"comprehensive": true, "gaps_identified": [], "additional_research_needed": false}
    },
    "research_status": {
        "completeness_score": 0.9,
        "confidence_level": "high",
        "information_quality": "excellent",
        "ready_for_synthesis": true,
        "next_steps": ["Proceed to synthesis"]
    }
}
```
"""
    
    def test_prep_method(self):
        """Test the prep method extracts correct data"""
        shared = {
            "current_sub_question": {"id": "q1", "question": "Test question"},
            "search_results": [{"title": "Test", "url": "test.com"}],
            "research_context": {"domain": "test"}
        }
        
        result = self.node.prep(shared)
        
        self.assertEqual(result[0]["id"], "q1")
        self.assertEqual(len(result[2]), 1)  # search_results
        self.assertEqual(result[3]["domain"], "test")
    
    @patch('agent.function_nodes.multi_source_information_gatherer.call_llm')
    def test_exec_method_success(self, mock_llm):
        """Test successful information gathering"""
        mock_llm.return_value = self.mock_llm_response
        
        sub_question = {"id": "q1", "question": "Test question"}
        search_results = [{"title": "Test", "url": "test.com", "snippet": "AI medical diagnosis"}]
        inputs = (sub_question, ["web"], search_results, {})
        
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["sub_question_id"], "q1")
        self.assertIn("information_gathered", result)
        self.assertIn("source_analysis", result)
        self.assertGreater(len(result["information_gathered"]["key_findings"]), 0)
    
    def test_exec_no_relevant_results(self):
        """Test execution when no relevant search results found"""
        sub_question = {"id": "q1", "question": "Test question"}
        search_results = []
        inputs = (sub_question, ["web"], search_results, {})
        
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "no_relevant_results")
        self.assertEqual(len(result["information_gathered"]["key_findings"]), 0)
    
    def test_extract_relevant_search_results(self):
        """Test relevance filtering of search results"""
        question_text = "artificial intelligence medical diagnosis"
        search_results = [
            {"title": "AI in Medical Diagnosis", "snippet": "Artificial intelligence revolutionizes medical diagnosis", "url": "test1.com"},
            {"title": "Cooking Recipes", "snippet": "Best pasta recipes", "url": "test2.com"},
            {"title": "Medical AI Applications", "snippet": "AI applications in healthcare diagnosis", "url": "test3.com"}
        ]
        
        relevant = self.node._extract_relevant_search_results(question_text, search_results)
        
        self.assertEqual(len(relevant), 2)  # Should filter out cooking recipes
        self.assertTrue(all(result.get("relevance_score", 0) > 0 for result in relevant))
    
    def test_post_method(self):
        """Test post method updates research queue correctly"""
        shared = {"research_queue": {"pending": ["q1"], "in_progress": ["q1"], "completed": []}}
        prep_res = ({}, [], [], {})
        exec_res = {"sub_question_id": "q1", "total_findings": 3}
        
        action = self.node.post(shared, prep_res, exec_res)
        
        self.assertEqual(action, "default")
        self.assertIn("research_findings", shared)
        self.assertNotIn("q1", shared["research_queue"]["in_progress"])
        self.assertIn("q1", shared["research_queue"]["completed"])


class TestInformationSynthesizerNode(unittest.TestCase):
    """Test cases for InformationSynthesizerNode"""
    
    def setUp(self):
        self.node = InformationSynthesizerNode()
        self.mock_llm_response = """
```json
{
    "main_question": "How is AI transforming healthcare?",
    "synthesis_overview": {
        "primary_answer": "AI is transforming healthcare through improved diagnosis, personalized treatment, and drug discovery",
        "confidence_level": "high",
        "evidence_strength": "strong",
        "completeness_assessment": "comprehensive"
    },
    "key_insights": [
        {
            "insight": "AI diagnostic tools achieve 95% accuracy in medical imaging",
            "supporting_evidence": ["Multiple clinical trials", "Peer-reviewed studies"],
            "sources": ["Journal of Medical AI", "Nature Medicine"],
            "confidence": "high",
            "importance": "critical",
            "sub_questions_addressed": ["q1", "q2"]
        }
    ],
    "thematic_analysis": {
        "major_themes": [
            {
                "theme": "Diagnostic Enhancement",
                "description": "AI significantly improves diagnostic accuracy and speed",
                "evidence_count": 15,
                "consistency": "consistent",
                "implications": "Reduced diagnostic errors and faster treatment"
            }
        ],
        "cross_cutting_patterns": [
            {
                "pattern": "Gradual adoption across medical specialties",
                "frequency": "common",
                "significance": "high",
                "examples": ["Radiology", "Pathology", "Cardiology"]
            }
        ]
    },
    "conflict_resolution": [],
    "evidence_assessment": {
        "total_sources_analyzed": 25,
        "source_quality_distribution": {"high_quality": 15, "medium_quality": 8, "low_quality": 2},
        "source_type_coverage": {"academic": 12, "industry": 8, "news": 3, "official": 2, "other": 0},
        "temporal_coverage": {"recent": 20, "medium_term": 4, "historical": 1},
        "geographic_coverage": "Global perspective with US and EU focus",
        "bias_assessment": "Minimal bias detected, sources are diverse"
    },
    "research_gaps": [
        {
            "gap_description": "Limited long-term outcome studies",
            "importance": "important",
            "impact_on_conclusions": "Moderate - affects long-term impact assessment",
            "suggested_follow_up": "Longitudinal studies needed"
        }
    ],
    "conclusions": {
        "primary_conclusions": [
            {
                "conclusion": "AI is significantly improving healthcare outcomes",
                "evidence_basis": "25 high-quality sources across multiple domains",
                "confidence_level": "high",
                "limitations": "Limited long-term data available"
            }
        ],
        "implications": [
            {
                "implication": "Healthcare delivery will become more personalized",
                "domain": "Clinical practice",
                "significance": "high",
                "time_horizon": "medium-term"
            }
        ],
        "recommendations": [
            {
                "recommendation": "Invest in AI training for healthcare professionals",
                "rationale": "Ensure successful AI adoption",
                "target_audience": "Healthcare institutions",
                "implementation_difficulty": "moderate"
            }
        ]
    },
    "synthesis_metadata": {
        "total_sub_questions_analyzed": 6,
        "synthesis_date": "2024-01-15T15:30:00",
        "synthesis_method": "LLM-based comprehensive analysis",
        "quality_score": 0.9,
        "reliability_assessment": "high"
    }
}
```
"""
    
    def test_prep_method(self):
        """Test prep method extracts synthesis data correctly"""
        shared = {
            "research_findings": {"q1": {"sub_question": "Test"}},
            "research_scope": {"primary_focus": "Healthcare"},
            "research_question": "Test question?",
            "research_metadata": {"total_questions": 3}
        }
        
        result = self.node.prep(shared)
        
        self.assertEqual(len(result[0]), 1)  # research_findings
        self.assertEqual(result[1]["primary_focus"], "Healthcare")
        self.assertEqual(result[2], "Test question?")
        self.assertEqual(result[3]["total_questions"], 3)
    
    @patch('agent.function_nodes.information_synthesizer.call_llm')
    def test_exec_method_success(self, mock_llm):
        """Test successful synthesis execution"""
        mock_llm.return_value = self.mock_llm_response
        
        research_findings = {
            "q1": {
                "sub_question": "Test question",
                "information_gathered": {"key_findings": [{"finding": "Test finding"}]},
                "research_status": {"information_quality": "good"}
            }
        }
        inputs = (research_findings, {"primary_focus": "Healthcare"}, "Test question?", {})
        
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["main_question"], "Test question?")
        self.assertIn("synthesis_overview", result)
        self.assertIn("key_insights", result)
        self.assertGreater(len(result["key_insights"]), 0)
    
    def test_exec_empty_findings(self):
        """Test execution with no research findings"""
        inputs = ({}, {}, "Test question?", {})
        
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "empty_findings")
        self.assertEqual(len(result["key_insights"]), 0)
    
    def test_structure_research_findings(self):
        """Test research findings structuring for LLM"""
        research_findings = {
            "q1": {
                "sub_question": "Test question",
                "information_gathered": {
                    "key_findings": [{"finding": "Important finding", "credibility_score": 0.9}],
                    "data_points": [{"metric": "Accuracy", "value": "95%"}]
                },
                "research_status": {"information_quality": "excellent", "confidence_level": "high"}
            }
        }
        
        structured = self.node._structure_research_findings(research_findings)
        
        self.assertIn("Test question", structured)
        self.assertIn("Important finding", structured)
        self.assertIn("95%", structured)
    
    def test_post_method(self):
        """Test post method stores synthesis correctly"""
        shared = {}
        prep_res = ({}, {}, "Test question", {})
        exec_res = {
            "main_question": "Test question",
            "synthesis_overview": {"confidence_level": "high"},
            "key_insights": [{"insight": "Test insight"}],
            "conclusions": {"primary_conclusions": []},
            "research_gaps": [],
            "synthesis_metadata": {"quality_score": 0.9, "total_insights": 1}
        }
        
        action = self.node.post(shared, prep_res, exec_res)
        
        self.assertEqual(action, "default")
        self.assertIn("research_synthesis", shared)
        self.assertIn("synthesis_overview", shared)
        self.assertIn("key_insights", shared)
        self.assertIn("research_metadata", shared)
        self.assertTrue(shared["research_metadata"]["synthesis_complete"])


class TestCitationManagerNode(unittest.TestCase):
    """Test cases for CitationManagerNode"""
    
    def setUp(self):
        self.node = CitationManagerNode()
        self.mock_llm_response = """
```json
{
    "citation_style": "apa",
    "citation_database": [
        {
            "citation_id": "source_1",
            "formatted_citation": "Johnson, S. (2024). AI in Medical Diagnosis. Journal of Medical AI, 15(3), 123-145.",
            "in_text_citation": "(Johnson, 2024)",
            "source_type": "academic",
            "url": "https://example.com/ai-diagnosis",
            "title": "AI in Medical Diagnosis",
            "author": "Dr. Sarah Johnson",
            "publication_date": "2024",
            "publisher": "Journal of Medical AI",
            "access_date": "2024-01-15",
            "credibility_assessment": {
                "credibility_score": 0.95,
                "credibility_level": "high",
                "credibility_factors": ["Peer-reviewed", "Established journal"],
                "potential_biases": [],
                "reliability_notes": "High-quality academic source"
            },
            "usage_tracking": {
                "times_cited": 1,
                "sub_questions_referenced": ["q1"],
                "key_findings_supported": ["finding_1"],
                "importance_weight": 0.9
            }
        }
    ],
    "citation_summary": {
        "total_sources": 1,
        "source_type_breakdown": {"academic": 1, "news": 0, "web": 0, "official": 0, "other": 0},
        "credibility_distribution": {"high_credibility": 1, "medium_credibility": 0, "low_credibility": 0},
        "temporal_distribution": {"very_recent": 1, "recent": 0, "older": 0, "undated": 0}
    },
    "citation_quality_assessment": {
        "overall_quality": "excellent",
        "source_diversity": "medium",
        "academic_rigor": "high",
        "potential_issues": [],
        "missing_information": []
    },
    "bibliography": {
        "formatted_bibliography": "Johnson, S. (2024). AI in Medical Diagnosis. Journal of Medical AI, 15(3), 123-145.",
        "grouped_by_type": {
            "academic_sources": ["Johnson, S. (2024). AI in Medical Diagnosis. Journal of Medical AI, 15(3), 123-145."],
            "news_sources": [],
            "web_sources": [],
            "other_sources": []
        }
    },
    "citation_guidelines": {
        "in_text_usage": "Use (Author, Year) format for APA style",
        "common_patterns": ["(Johnson, 2024)", "(Smith et al., 2023)"],
        "style_notes": "Follow APA 7th edition guidelines",
        "example_usage": "According to Johnson (2024), AI improves diagnostic accuracy."
    },
    "metadata": {
        "generated_date": "2024-01-15T16:00:00",
        "citation_count": 1,
        "style_version": "APA 7th edition",
        "last_updated": "2024-01-15T16:00:00"
    }
}
```
"""
    
    def test_prep_method(self):
        """Test prep method extracts citation data correctly"""
        shared = {
            "research_findings": {"q1": {"information_gathered": {"key_findings": []}}},
            "search_results": [{"url": "test.com", "title": "Test"}],
            "citations": {},
            "citation_style": "mla"
        }
        
        result = self.node.prep(shared)
        
        self.assertEqual(len(result[0]), 1)  # research_findings
        self.assertEqual(len(result[1]), 1)  # search_results
        self.assertEqual(result[3], "mla")  # citation_style
    
    @patch('agent.function_nodes.citation_manager.call_llm')
    def test_exec_method_success(self, mock_llm):
        """Test successful citation generation"""
        mock_llm.return_value = self.mock_llm_response
        
        research_findings = {
            "q1": {
                "information_gathered": {
                    "key_findings": [{"source": "https://example.com", "finding": "Test"}]
                }
            }
        }
        search_results = [{"url": "https://example.com", "title": "Test Article"}]
        inputs = (research_findings, search_results, {}, "apa", {})
        
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["citation_style"], "apa")
        self.assertIn("citation_database", result)
        self.assertGreater(len(result["citation_database"]), 0)
    
    def test_exec_no_sources(self):
        """Test execution when no sources are available"""
        inputs = ({}, [], {}, "apa", {})
        
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "no_sources")
        self.assertEqual(len(result["citation_database"]), 0)
    
    def test_extract_all_sources(self):
        """Test source extraction from research findings and search results"""
        research_findings = {
            "q1": {
                "information_gathered": {
                    "key_findings": [{"source": "https://academic.com", "finding": "Research finding"}],
                    "expert_opinions": [{"source": "https://expert.com", "expert": "Dr. Smith"}]
                }
            }
        }
        search_results = [{"url": "https://news.com", "title": "News Article"}]
        
        sources = self.node._extract_all_sources(research_findings, search_results)
        
        self.assertEqual(len(sources), 3)  # 2 from research + 1 from search
        urls = [source["url"] for source in sources]
        self.assertIn("https://academic.com", urls)
        self.assertIn("https://expert.com", urls)
        self.assertIn("https://news.com", urls)
    
    def test_post_method(self):
        """Test post method stores citations correctly"""
        shared = {}
        prep_res = ({}, [], {}, "apa", {})
        exec_res = {
            "citation_database": [{"citation_id": "test_1", "formatted_citation": "Test citation"}],
            "bibliography": {"formatted_bibliography": "Test bibliography"},
            "citation_style": "apa",
            "citation_summary": {"total_sources": 1},
            "citation_quality_assessment": {"overall_quality": "good"}
        }
        
        action = self.node.post(shared, prep_res, exec_res)
        
        self.assertEqual(action, "default")
        self.assertIn("citations", shared)
        self.assertIn("citation_database", shared)
        self.assertIn("citation_lookup", shared)
        self.assertIn("research_metadata", shared)
        self.assertTrue(shared["research_metadata"]["citations_generated"])


class TestResearchReportGeneratorNode(unittest.TestCase):
    """Test cases for ResearchReportGeneratorNode"""
    
    def setUp(self):
        self.node = ResearchReportGeneratorNode()
        self.mock_llm_response = """
```json
{
    "report_metadata": {
        "title": "AI in Healthcare: A Comprehensive Research Report",
        "research_question": "How is AI transforming healthcare?",
        "report_type": "comprehensive",
        "target_audience": "general",
        "generation_date": "2024-01-15T17:00:00",
        "word_count_estimate": 2500,
        "section_count": 7,
        "citation_count": 15
    },
    "executive_summary": {
        "key_question": "How is AI transforming healthcare?",
        "primary_findings": "AI is significantly transforming healthcare through improved diagnostics, personalized treatment, and accelerated drug discovery",
        "key_insights": [
            "AI diagnostic tools achieve 95% accuracy",
            "Personalized medicine is becoming more accessible",
            "Drug discovery timelines are being reduced by 30%"
        ],
        "main_conclusions": "AI adoption in healthcare is accelerating with measurable improvements in patient outcomes",
        "recommendations_summary": "Healthcare institutions should invest in AI training and infrastructure",
        "confidence_assessment": "high"
    },
    "report_sections": [
        {
            "section_id": "introduction",
            "section_title": "Introduction",
            "section_number": 1,
            "content": "Artificial Intelligence (AI) is revolutionizing healthcare across multiple domains. This report examines the current state and future prospects of AI in healthcare.",
            "subsections": [
                {
                    "subsection_title": "Background",
                    "content": "Healthcare AI has evolved rapidly over the past decade, with significant advances in machine learning and data processing capabilities."
                }
            ],
            "citations_used": ["source_1", "source_2"],
            "word_count": 250
        },
        {
            "section_id": "findings",
            "section_title": "Research Findings",
            "section_number": 2,
            "content": "Our research reveals three major areas where AI is making significant impact: diagnostic imaging, treatment planning, and drug discovery.",
            "subsections": [],
            "citations_used": ["source_3", "source_4"],
            "word_count": 800
        },
        {
            "section_id": "conclusions",
            "section_title": "Conclusions",
            "section_number": 3,
            "content": "AI is demonstrably improving healthcare outcomes with strong evidence for continued growth and adoption.",
            "subsections": [],
            "citations_used": ["source_5"],
            "word_count": 300
        }
    ],
    "appendices": [
        {
            "appendix_id": "bibliography",
            "title": "References",
            "content": "Complete bibliography of all sources cited",
            "type": "bibliography"
        }
    ],
    "quality_assessment": {
        "content_quality": "excellent",
        "citation_quality": "good",
        "structure_quality": "excellent",
        "audience_appropriateness": "high",
        "completeness": "comprehensive",
        "areas_for_improvement": []
    },
    "report_statistics": {
        "total_word_count": 2500,
        "total_sections": 3,
        "total_citations": 15,
        "unique_sources": 12,
        "research_depth_score": 0.9,
        "evidence_strength": "strong"
    }
}
```
"""
    
    def test_prep_method(self):
        """Test prep method sets up report configuration correctly"""
        shared = {
            "research_synthesis": {"main_question": "Test"},
            "citations": {"citation_database": []},
            "research_question": "Test question?",
            "report_config": {"report_type": "brief"}
        }
        
        result = self.node.prep(shared)
        
        self.assertEqual(result[0]["main_question"], "Test")
        self.assertEqual(result[3]["report_type"], "brief")
        self.assertEqual(result[4], "Test question?")
    
    def test_prep_with_defaults(self):
        """Test prep method applies default configuration"""
        shared = {"research_synthesis": {}, "citations": {}}
        
        result = self.node.prep(shared)
        
        report_config = result[3]
        self.assertEqual(report_config["report_type"], "comprehensive")
        self.assertEqual(report_config["target_audience"], "general")
        self.assertTrue(report_config["include_methodology"])
    
    @patch('agent.function_nodes.research_report_generator.call_llm')
    def test_exec_method_success(self, mock_llm):
        """Test successful report generation"""
        mock_llm.return_value = self.mock_llm_response
        
        research_synthesis = {
            "synthesis_overview": {"primary_answer": "AI is transforming healthcare"},
            "key_insights": [{"insight": "Test insight"}],
            "conclusions": {"primary_conclusions": []}
        }
        citations = {"citation_database": [{"citation_id": "test_1"}]}
        report_config = {"report_type": "comprehensive", "target_audience": "general"}
        
        inputs = (research_synthesis, citations, {}, report_config, "Test question?")
        
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertIn("report_metadata", result)
        self.assertIn("executive_summary", result)
        self.assertIn("report_sections", result)
        self.assertGreater(len(result["report_sections"]), 0)
    
    def test_exec_no_synthesis(self):
        """Test execution when no synthesis data is available"""
        inputs = ({}, {}, {}, {"report_type": "brief"}, "Test question?")
        
        result = self.node.exec(inputs)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "insufficient_data")
        self.assertEqual(len(result["report_sections"]), 1)  # Only notice section
    
    def test_prepare_citation_lookup(self):
        """Test citation lookup preparation"""
        citations = {
            "citation_database": [
                {"citation_id": "test_1", "in_text_citation": "(Test, 2024)"},
                {"citation_id": "test_2", "in_text_citation": "(Example, 2023)"}
            ]
        }
        
        lookup = self.node._prepare_citation_lookup(citations)
        
        self.assertEqual(len(lookup), 2)
        self.assertEqual(lookup["test_1"], "(Test, 2024)")
        self.assertEqual(lookup["test_2"], "(Example, 2023)")
    
    def test_prepare_structured_content(self):
        """Test structured content preparation for LLM"""
        research_synthesis = {
            "synthesis_overview": {"primary_answer": "Test answer", "confidence_level": "high"},
            "key_insights": [{"insight": "Important insight", "confidence": "high"}],
            "conclusions": {"primary_conclusions": [{"conclusion": "Test conclusion"}]}
        }
        citations = {"citation_summary": {"total_sources": 10}}
        
        content = self.node._prepare_structured_content(research_synthesis, citations, {})
        
        self.assertIn("Test answer", content)
        self.assertIn("Important insight", content)
        self.assertIn("Test conclusion", content)
        self.assertIn("10", content)  # citation count
    
    def test_post_method(self):
        """Test post method stores report correctly"""
        shared = {}
        prep_res = ({}, {}, {}, {}, "Test question")
        exec_res = {
            "report_metadata": {"title": "Test Report", "word_count_estimate": 1000},
            "executive_summary": {"primary_findings": "Test findings"},
            "report_sections": [{"section_title": "Test Section"}],
            "report_statistics": {"total_word_count": 1000, "total_sections": 1},
            "quality_assessment": {"content_quality": "good"},
            "key_insights": [],
            "research_gaps": [],
            "conclusions": {"primary_conclusions": []}
        }
        
        action = self.node.post(shared, prep_res, exec_res)
        
        self.assertEqual(action, "default")
        self.assertIn("research_report", shared)
        self.assertIn("formatted_report", shared)
        self.assertIn("report_summary", shared)
        self.assertIn("research_metadata", shared)
        self.assertTrue(shared["research_metadata"]["report_generated"])
    
    def test_create_formatted_report_text(self):
        """Test formatted text report creation"""
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
                    "subsections": [{"subsection_title": "Background", "content": "Test background"}]
                }
            ],
            "report_statistics": {"total_word_count": 100, "total_sections": 1, "total_citations": 0}
        }
        
        formatted = self.node._create_formatted_report_text(report)
        
        self.assertIn("# Test Report", formatted)
        self.assertIn("Test question?", formatted)
        self.assertIn("## Executive Summary", formatted)
        self.assertIn("## 1. Introduction", formatted)
        self.assertIn("### Background", formatted)


class TestDeepResearchWorkflowIntegration(unittest.TestCase):
    """Integration tests for the complete deep research workflow"""
    
    def setUp(self):
        self.decomposer = ResearchQueryDecomposerNode()
        self.gatherer = MultiSourceInformationGathererNode()
        self.synthesizer = InformationSynthesizerNode()
        self.citation_manager = CitationManagerNode()
        self.report_generator = ResearchReportGeneratorNode()
    
    @patch('agent.function_nodes.research_query_decomposer.call_llm')
    def test_decomposer_to_gatherer_workflow(self, mock_llm):
        """Test workflow from decomposer to gatherer"""
        # Mock decomposer response with exactly 1 sub-question
        mock_llm.return_value = """
```json
{
    "main_question": "Test question",
    "research_scope": {"primary_focus": "Test"},
    "sub_questions": [{"id": "q1", "question": "Sub-question 1"}],
    "research_strategy": {"recommended_order": ["q1"]},
    "quality_criteria": {}
}
```
"""
        
        # Simulate shared store
        shared = {"research_question": "Test question", "research_depth": "standard"}
        
        # Run decomposer
        decomposer_prep = self.decomposer.prep(shared)
        decomposer_result = self.decomposer.exec(decomposer_prep)
        self.decomposer.post(shared, decomposer_prep, decomposer_result)
        
        # Verify decomposer output structure
        self.assertIn("research_decomposition", shared)
        self.assertIn("sub_questions", shared)
        self.assertEqual(len(shared["sub_questions"]), 1)
        
        # Setup for gatherer
        shared["current_sub_question"] = shared["sub_questions"][0]
        shared["search_results"] = [{"url": "test.com", "title": "Test", "snippet": "Sub-question content"}]
        
        # Test gatherer can process decomposer output
        gatherer_prep = self.gatherer.prep(shared)
        self.assertEqual(gatherer_prep[0]["id"], "q1")
    
    def test_complete_workflow_structure(self):
        """Test that all nodes have compatible input/output structures"""
        # Simulate a complete workflow data structure
        shared = {
            "research_question": "How is AI transforming healthcare?",
            "research_depth": "comprehensive",
            "search_results": [
                {"url": "https://example.com", "title": "AI in Healthcare", "snippet": "AI is transforming healthcare through..."}
            ],
            "citation_style": "apa"
        }
        
        # Test that each node can prep without errors
        try:
            # Decomposer prep
            decomposer_prep = self.decomposer.prep(shared)
            self.assertIsInstance(decomposer_prep, tuple)
            
            # Add mock decomposition for downstream nodes
            shared["research_decomposition"] = {"sub_questions": [{"id": "q1", "question": "Test"}]}
            shared["current_sub_question"] = {"id": "q1", "question": "Test"}
            
            # Gatherer prep
            gatherer_prep = self.gatherer.prep(shared)
            self.assertIsInstance(gatherer_prep, tuple)
            
            # Add mock research findings for downstream nodes
            shared["research_findings"] = {"q1": {"information_gathered": {"key_findings": []}}}
            
            # Synthesizer prep
            synthesizer_prep = self.synthesizer.prep(shared)
            self.assertIsInstance(synthesizer_prep, tuple)
            
            # Citation manager prep
            citation_prep = self.citation_manager.prep(shared)
            self.assertIsInstance(citation_prep, tuple)
            
            # Add mock synthesis and citations for report generator
            shared["research_synthesis"] = {"synthesis_overview": {}, "key_insights": []}
            shared["citations"] = {"citation_database": []}
            
            # Report generator prep
            report_prep = self.report_generator.prep(shared)
            self.assertIsInstance(report_prep, tuple)
            
        except Exception as e:
            self.fail(f"Workflow structure compatibility test failed: {e}")
    
    def test_data_flow_consistency(self):
        """Test that data flows correctly between nodes"""
        # Test that decomposer output matches gatherer input expectations
        decomposer_output = {
            "sub_questions": [{"id": "q1", "question": "Test question", "expected_sources": ["academic"]}]
        }
        
        # This should work for gatherer
        current_sub_question = decomposer_output["sub_questions"][0]
        self.assertIn("id", current_sub_question)
        self.assertIn("question", current_sub_question)
        
        # Test gatherer output matches synthesizer input
        gatherer_output = {
            "q1": {
                "sub_question": "Test question",
                "information_gathered": {
                    "key_findings": [{"finding": "Test", "source": "test.com"}]
                }
            }
        }
        
        # This should work for synthesizer
        self.assertIn("q1", gatherer_output)
        self.assertIn("information_gathered", gatherer_output["q1"])
        
        # Test synthesizer output matches report generator input
        synthesizer_output = {
            "synthesis_overview": {"primary_answer": "Test answer"},
            "key_insights": [{"insight": "Test insight"}],
            "conclusions": {"primary_conclusions": []}
        }
        
        # This should work for report generator
        self.assertIn("synthesis_overview", synthesizer_output)
        self.assertIn("key_insights", synthesizer_output)


if __name__ == "__main__":
    # Run individual test classes
    unittest.main(verbosity=2)