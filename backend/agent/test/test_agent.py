import pytest
import asyncio
from unittest.mock import patch
from agent.nodes import WorkflowDesignerNode, RethinkingWorkflowNode, WorkflowExecutorNode
from pocketflow import AsyncFlow

@pytest.mark.asyncio
async def test_rethinking_design_loop_max_attempts_flow():
    # 构造初始 shared
    shared = {
        "user_message": "Book a flight from LA to Shanghai",
        "available_nodes": {"nodes": {}},
        "similar_workflows": [],
    }
    designer = WorkflowDesignerNode()
    rethinking = RethinkingWorkflowNode()
    executor = WorkflowExecutorNode()
    # 只测设计-评审-设计-评审-...-执行
    designer - "designed" >> rethinking
    rethinking - "needs_revision" >> designer
    rethinking - "ready_to_execute" >> executor
    flow = AsyncFlow(start=designer)

    # mock call_llm: designer返回固定yaml，review返回需要revision直到第6次
    def fake_call_llm_designer(prompt):
        return """
```yaml
thinking: |
    Designed workflow.
workflow:
  name: TestFlow
  description: Test
  nodes: []
  connections: []
  shared_store_schema: {}
estimated_steps: 1
requires_user_input: false
requires_permission: false
```
"""
    def fake_call_llm_review(prompt):
        if fake_call_llm_review.attempt < 5:
            fake_call_llm_review.attempt += 1
            return """
```yaml
thinking: |
    Needs revision.
needs_revision: true
revision_suggestions:
  - Fix step order
ready_to_execute: false
```
"""
        else:
            return """
```yaml
thinking: |
    Looks good.
needs_revision: false
revision_suggestions:
  - None
ready_to_execute: true
```
"""
    fake_call_llm_review.attempt = 0

    with patch("agent.nodes.call_llm", side_effect=lambda prompt: fake_call_llm_designer(prompt) if "redesign" in prompt or "analyze the user's question" in prompt else fake_call_llm_review(prompt)):
        await flow.run_async(shared)
        # 最多5次循环，最后一次 ready_to_execute
        assert shared["design_review_attempts"] == 6
        assert shared["rethinking_result"]["ready_to_execute"] is True
        assert shared["rethinking_result"]["needs_revision"] is False

@pytest.mark.asyncio
async def test_rethinking_design_loop_early_success_flow():
    shared = {
        "user_message": "Book a hotel in Paris",
        "available_nodes": {"nodes": {}},
        "similar_workflows": [],
    }
    designer = WorkflowDesignerNode()
    rethinking = RethinkingWorkflowNode()
    executor = WorkflowExecutorNode()
    designer - "designed" >> rethinking
    rethinking - "needs_revision" >> designer
    rethinking - "ready_to_execute" >> executor
    flow = AsyncFlow(start=designer)

    def fake_call_llm_designer(prompt):
        return """
```yaml
thinking: |
    Designed workflow.
workflow:
  name: TestFlow
  description: Test
  nodes: []
  connections: []
  shared_store_schema: {}
estimated_steps: 1
requires_user_input: false
requires_permission: false
```
"""
    def fake_call_llm_review(prompt):
        if fake_call_llm_review.attempt < 2:
            fake_call_llm_review.attempt += 1
            return """
```yaml
thinking: |
    Needs revision.
needs_revision: true
revision_suggestions:
  - Add hotel star rating
ready_to_execute: false
```
"""
        else:
            return """
```yaml
thinking: |
    Looks good.
needs_revision: false
revision_suggestions:
  - None
ready_to_execute: true
```
"""
    fake_call_llm_review.attempt = 0

    with patch("agent.nodes.call_llm", side_effect=lambda prompt: fake_call_llm_designer(prompt) if "redesign" in prompt or "analyze the user's question" in prompt else fake_call_llm_review(prompt)):
        await flow.run_async(shared)
        assert shared["design_review_attempts"] == 3
        assert shared["rethinking_result"]["ready_to_execute"] is True
        assert shared["rethinking_result"]["needs_revision"] is False 