#!/usr/bin/env python3
"""
Content Research Workflow Demo (Function Nodes Only)

This demo showcases content research和 gathering using真实 function_nodes:
1. Web search for industry insights
2. Summarize results

Usage:
    python content_research_demo.py
"""
import sys
import os
from pocketflow import Flow
from agent.function_nodes.web_search import WebSearchNode
from agent.function_nodes.result_summarizer import ResultSummarizerNode

def check_api_key():
    if not os.environ.get("ARCADE_API_KEY"):
        print("[ERROR] ARCADE_API_KEY is not set. Please export your Arcade API key.")
        exit(1)

def create_content_research_workflow():
    # 只用 function_nodes 真实节点
    search = WebSearchNode()
    summarize = ResultSummarizerNode()
    search >> summarize
    return Flow(start=search)

def main():
    check_api_key()
    shared = {
        "query": "AI and Machine Learning industry trends 2024",
        "num_results": 5,
        "user_message": "Summarize the latest industry trends in AI and Machine Learning."
    }
    try:
        workflow = create_content_research_workflow()
        result = workflow.run(shared)
        print("\n[RESULT] Research Summary:")
        print(shared.get("result_summary", "No summary generated."))
    except ImportError as e:
        print("Lack web_search or result_summarizer nodes to run")
        exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        exit(1)

if __name__ == "__main__":
    main()