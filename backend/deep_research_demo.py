#!/usr/bin/env python3
"""Demo script for Deep Research Workflow using PocketFlow function nodes (with real web search, using only existing nodes)"""

from pocketflow import Flow
from agent.function_nodes.research_query_decomposer import ResearchQueryDecomposerNode
from agent.function_nodes.web_search import WebSearchNode
from agent.function_nodes.multi_source_information_gatherer import MultiSourceInformationGathererNode
from agent.function_nodes.information_synthesizer import InformationSynthesizerNode
from agent.function_nodes.result_summarizer import ResultSummarizerNode
from agent.function_nodes.research_report_generator import ResearchReportGeneratorNode
from agent.function_nodes.end_node import EndNode

# 1. Instantiate nodes
query_decomposer = ResearchQueryDecomposerNode()
web_search = WebSearchNode()
info_gatherer = MultiSourceInformationGathererNode()
info_synthesizer = InformationSynthesizerNode()
result_summarizer = ResultSummarizerNode()
report_generator = ResearchReportGeneratorNode()
end_node = EndNode()

# 2. Create the main flow (excluding web search and gather, which are handled per sub-question)
query_decomposer >> info_synthesizer >> result_summarizer >> report_generator >> end_node
research_flow = Flow(start=query_decomposer)

# 3. Prepare shared store with a sample research question
shared = {
    "research_question": "How is AI transforming healthcare in 2024?",
    "research_depth": "comprehensive",  # can be 'standard', 'focused', or 'comprehensive'
    "num_results": 5,  # Number of web search results per sub-question
}

print("\n🚀 Starting Deep Research Workflow (with real web search, using only existing nodes)...\n")

# 4. Step 1: Decompose the research question
query_decomposer.run(shared)
sub_questions = shared.get("sub_questions", [])

# 5. Step 2: For each sub-question, perform web search and gather information
shared["research_findings"] = {}  # Ensure findings dict exists
for subq in sub_questions:
    subq_id = subq.get("id", "unknown")
    subq_text = subq.get("question", "")
    print(f"\n🔎 Researching sub-question [{subq_id}]: {subq_text}")
    shared["query"] = subq_text
    shared["current_sub_question"] = subq
    # Run web search with error handling
    try:
        web_search.run(shared)
    except Exception as e:
        print(f"⚠️  Web search failed for sub-question [{subq_id}]: {e}")
        shared["search_results"] = []  # Set empty results to allow gatherer to proceed
    # Run information gatherer
    info_gatherer.run(shared)

# 6. Step 3: Synthesize, summarize, and generate report using the flow
research_flow.run(shared)

# 7. Print outputs
print("\n==== SUMMARY ====")
print(shared.get("result_summary", "No summary generated."))

print("\n==== FORMATTED REPORT ====")
print(shared.get("formatted_report", "No report generated.")) 