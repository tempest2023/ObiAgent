"""
Workflow Store System

This module provides a store for saving and retrieving workflows.
It allows the agent to reuse successful workflow patterns and learn from past solutions.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

@dataclass
class WorkflowMetadata:
    """Metadata for a stored workflow"""
    id: str
    name: str
    description: str
    question_pattern: str
    nodes_used: List[str]
    success_rate: float
    created_at: str
    last_used: str
    usage_count: int
    tags: List[str]

@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    metadata: WorkflowMetadata
    nodes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    shared_store_schema: Dict[str, Any]

class WorkflowStore:
    """Store for saving and retrieving workflows"""
    
    def __init__(self, storage_path: str = "workflows", basedir: str = "./"):
        if basedir is not None:
            self.storage_path = os.path.join(basedir, storage_path)
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self._ensure_storage_directory()
        self._load_existing_workflows()
    
    def _ensure_storage_directory(self):
        """Ensure the storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _load_existing_workflows(self):
        """Load existing workflows from storage"""
        if not os.path.exists(self.storage_path):
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_path, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        workflow = self._deserialize_workflow(data)
                        self.workflows[workflow.metadata.id] = workflow
                except Exception as e:
                    print(f"Error loading workflow {filename}: {e}")
    
    def _deserialize_workflow(self, data: Dict[str, Any]) -> WorkflowDefinition:
        """Deserialize workflow from JSON data"""
        metadata = WorkflowMetadata(**data['metadata'])
        return WorkflowDefinition(
            metadata=metadata,
            nodes=data['nodes'],
            connections=data['connections'],
            shared_store_schema=data['shared_store_schema']
        )
    
    def _serialize_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Serialize workflow to JSON data"""
        return {
            'metadata': asdict(workflow.metadata),
            'nodes': workflow.nodes,
            'connections': workflow.connections,
            'shared_store_schema': workflow.shared_store_schema
        }
    
    def _generate_workflow_id(self, question: str, nodes: List[str]) -> str:
        """Generate a unique ID for a workflow"""
        content = f"{question}:{':'.join(sorted(nodes))}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def save_workflow(self, 
                     question: str,
                     nodes: List[Dict[str, Any]],
                     connections: List[Dict[str, Any]],
                     shared_store_schema: Dict[str, Any],
                     success: bool = True,
                     tags: List[str] = None) -> str:
        """Save a workflow to the store"""
        
        node_names = [node.get('name', '') for node in nodes]
        workflow_id = self._generate_workflow_id(question, node_names)
        
        # Check if workflow already exists
        if workflow_id in self.workflows:
            # Update existing workflow
            existing = self.workflows[workflow_id]
            existing.metadata.usage_count += 1
            existing.metadata.last_used = datetime.now().isoformat()
            
            # Update success rate
            total_uses = existing.metadata.usage_count
            current_success_rate = existing.metadata.success_rate
            new_success_rate = ((current_success_rate * (total_uses - 1)) + (1 if success else 0)) / total_uses
            existing.metadata.success_rate = new_success_rate
            
            workflow = existing
        else:
            # Create new workflow
            metadata = WorkflowMetadata(
                id=workflow_id,
                name=f"Workflow for: {question[:50]}...",
                description=question,
                question_pattern=question,
                nodes_used=node_names,
                success_rate=1.0 if success else 0.0,
                created_at=datetime.now().isoformat(),
                last_used=datetime.now().isoformat(),
                usage_count=1,
                tags=tags or []
            )
            
            workflow = WorkflowDefinition(
                metadata=metadata,
                nodes=nodes,
                connections=connections,
                shared_store_schema=shared_store_schema
            )
        
        # Save to file
        filepath = os.path.join(self.storage_path, f"{workflow_id}.json")
        with open(filepath, 'w') as f:
            json.dump(self._serialize_workflow(workflow), f, indent=2)
        
        self.workflows[workflow_id] = workflow
        return workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get a workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def find_similar_workflows(self, question: str, limit: int = 5) -> List[WorkflowDefinition]:
        """Find workflows similar to the given question"""
        # Simple keyword matching - could be enhanced with embeddings
        question_lower = question.lower()
        scored_workflows = []
        
        for workflow in self.workflows.values():
            score = 0
            
            # Check question similarity
            workflow_question = workflow.metadata.question_pattern.lower()
            common_words = set(question_lower.split()) & set(workflow_question.split())
            score += len(common_words) * 2
            
            # Boost by success rate and usage count
            score += workflow.metadata.success_rate * 10
            score += min(workflow.metadata.usage_count, 10) * 0.5
            
            if score > 0:
                scored_workflows.append((score, workflow))
        
        # Sort by score and return top results
        scored_workflows.sort(key=lambda x: x[0], reverse=True)
        return [workflow for score, workflow in scored_workflows[:limit]]
    
    def get_workflows_by_tags(self, tags: List[str]) -> List[WorkflowDefinition]:
        """Get workflows that match any of the given tags"""
        matching_workflows = []
        for workflow in self.workflows.values():
            if any(tag in workflow.metadata.tags for tag in tags):
                matching_workflows.append(workflow)
        return matching_workflows
    
    def get_all_workflows(self) -> List[WorkflowDefinition]:
        """Get all stored workflows"""
        return list(self.workflows.values())
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow from the store"""
        if workflow_id not in self.workflows:
            return False
        
        # Remove from memory
        del self.workflows[workflow_id]
        
        # Remove from file system
        filepath = os.path.join(self.storage_path, f"{workflow_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored workflows"""
        total_workflows = len(self.workflows)
        total_usage = sum(w.metadata.usage_count for w in self.workflows.values())
        avg_success_rate = sum(w.metadata.success_rate for w in self.workflows.values()) / total_workflows if total_workflows > 0 else 0
        
        # Count by category
        node_categories = {}
        for workflow in self.workflows.values():
            for node_name in workflow.metadata.nodes_used:
                category = node_name.split('_')[0] if '_' in node_name else 'other'
                node_categories[category] = node_categories.get(category, 0) + 1
        
        return {
            'total_workflows': total_workflows,
            'total_usage': total_usage,
            'average_success_rate': avg_success_rate,
            'node_categories': node_categories
        }

# Global workflow store instance
workflow_store = WorkflowStore(storage_path = "workflows", basedir = "./")