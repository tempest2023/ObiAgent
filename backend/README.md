# PocketFlow General Agent System

A sophisticated agent system built on PocketFlow that can dynamically design and execute workflows to solve complex user problems. The system learns from successful workflows and can handle user interactions and permissions for sensitive operations.

## 🎯 Overview

The General Agent System is designed to solve complex, vague questions by:

1. **Analyzing** user questions and designing appropriate workflows
2. **Executing** workflows dynamically using available nodes
3. **Learning** from successful workflows and reusing patterns
4. **Handling** user interactions and permissions for sensitive operations
5. **Optimizing** workflows based on results and user feedback

## 🏗️ System Architecture

### Core Components

#### 1. **Node Registry** (`utils/node_registry.py`)
- **Purpose**: Catalogs all available nodes that the agent can use
- **Features**:
  - Node metadata (description, inputs, outputs, permission levels)
  - Categorization (search, analysis, booking, payment, etc.)
  - Permission levels (none, basic, sensitive, critical)
  - Example usage patterns

#### 2. **Workflow Store** (`utils/workflow_store.py`)
- **Purpose**: Stores and retrieves successful workflows for reuse
- **Features**:
  - Persistent storage of workflow patterns
  - Similarity-based workflow retrieval
  - Success rate tracking and learning
  - Workflow optimization suggestions

#### 3. **Permission Manager** (`utils/permission_manager.py`)
- **Purpose**: Handles user permissions for sensitive operations
- **Features**:
  - Permission request creation and tracking
  - Timeout management for permission requests
  - Support for different permission types (payment, booking, etc.)
  - User response handling

#### 4. **Agent Nodes** (`nodes.py`)

##### WorkflowDesignerNode
- Analyzes user questions using LLM
- Designs workflows based on available nodes
- Considers similar past workflows
- Generates structured workflow definitions

##### WorkflowExecutorNode
- Executes designed workflows dynamically
- Maps node names to actual implementations
- Handles progress reporting and error handling
- Saves successful workflows to store

##### UserInteractionNode
- Manages user questions and responses
- Handles permission requests
- Coordinates user input collection

##### WorkflowOptimizerNode
- Analyzes workflow results for issues
- Suggests workflow improvements
- Handles user feedback integration

### Flow Design

The system uses a sophisticated flow that can handle complex scenarios:

```mermaid
graph TD
    A[User Question] --> B[WorkflowDesignerNode]
    B --> C[WorkflowExecutorNode]
    C --> D{Needs User Input?}
    D -->|Yes| E[UserInteractionNode]
    D -->|No| F[WorkflowOptimizerNode]
    E --> G{Response Received?}
    G -->|No| E
    G -->|Yes| C
    F --> H{Optimization Needed?}
    H -->|Yes| B
    H -->|No| I[Success]
```

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+**
2. **OpenAI API Key** (for LLM calls)
3. **Google Generative AI Key** (optional, for alternative LLM)

### Installation

1. **Clone and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export GEMINI_API_KEY="your-gemini-api-key"  # optional
   ```

4. **Run the server:**
   ```bash
   python server.py
   ```

The server will start on `http://localhost:8000`

### API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## 📡 API Endpoints

### WebSocket Endpoints

#### `/api/v1/ws` - General Agent WebSocket
Handles real-time agent interactions:

**Message Types:**
- `chat`: Standard user question
- `user_response`: Response to agent questions
- `permission_response`: Response to permission requests
- `feedback`: User feedback for optimization

**Example Usage:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws');

// Send a question
ws.send(JSON.stringify({
    type: 'chat',
    content: 'Help book a flight ticket from Los Angeles to Shanghai with high cost performance, preferably departing in the afternoon.'
}));

// Handle responses
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.type, data.content);
};
```

### REST API Endpoints

#### Node Registry
- `GET /api/v1/nodes` - Get all available nodes
- `GET /api/v1/nodes/{node_name}` - Get specific node
- `GET /api/v1/nodes/category/{category}` - Get nodes by category

#### Workflow Store
- `GET /api/v1/workflows` - Get all stored workflows
- `GET /api/v1/workflows/{workflow_id}` - Get specific workflow
- `GET /api/v1/workflows/similar?question={question}` - Find similar workflows
- `DELETE /api/v1/workflows/{workflow_id}` - Delete workflow
- `GET /api/v1/workflows/stats` - Get workflow statistics

#### Permission Management
- `GET /api/v1/permissions` - Get pending permissions
- `GET /api/v1/permissions/{request_id}` - Get specific permission
- `POST /api/v1/permissions/{request_id}/respond` - Respond to permission
- `GET /api/v1/permissions/stats` - Get permission statistics

## 🔧 Example Usage

### Flight Booking Example

The system can handle complex requests like:

> "Help book a flight ticket from Los Angeles to Shanghai with high cost performance, preferably departing in the afternoon."

**What happens:**

1. **WorkflowDesignerNode** analyzes the question and designs a workflow:
   ```yaml
   workflow:
     name: Flight Booking Workflow
     nodes:
       - name: flight_search
         description: Search for flight options
       - name: cost_analysis
         description: Analyze costs and find best value
       - name: result_summarizer
         description: Present recommendations
   ```

2. **WorkflowExecutorNode** executes the workflow:
   - Searches for flights (mock implementation)
   - Analyzes costs and preferences
   - Generates recommendations

3. **UserInteractionNode** handles any user questions or permissions

4. **WorkflowOptimizerNode** evaluates success and suggests improvements

5. **Workflow Store** saves the successful workflow for future reuse

### Adding New Nodes

To add new functionality, register nodes in `utils/node_registry.py`:

```python
node_registry.register_node(NodeMetadata(
    name="custom_node",
    description="Description of what this node does",
    category=NodeCategory.ANALYSIS,
    permission_level=PermissionLevel.NONE,
    inputs=["input1", "input2"],
    outputs=["output1"],
    examples=[{"input1": "example", "output1": "result"}]
))
```

Then implement the node logic in `WorkflowExecutorNode._execute_node()`.

## 🧠 Learning and Optimization

### Workflow Learning
- Successful workflows are automatically saved
- Similar questions can reuse past workflow patterns
- Success rates are tracked and used for ranking

### Optimization
- Failed workflows trigger optimization analysis
- User feedback is incorporated into workflow improvements
- The system can redesign workflows based on issues

### Permission Handling
- Sensitive operations require explicit user permission
- Permission requests have timeouts
- Different permission levels for different operations

## 🔒 Security and Permissions

### Permission Levels
- **NONE**: No permission required
- **BASIC**: Simple confirmation
- **SENSITIVE**: Detailed review required
- **CRITICAL**: Explicit approval with details

### Sensitive Operations
- Payment processing
- Booking confirmations
- Data access
- System actions

## 📊 Monitoring and Statistics

The system provides comprehensive statistics:

- **Workflow Store**: Success rates, usage counts, node categories
- **Permission Manager**: Grant/deny rates, response times
- **Node Registry**: Available nodes by category

## 🛠️ Development

### Project Structure
```
backend/
├── agent/
│   ├── nodes.py              # Agent node implementations
│   ├── flow.py               # Flow definitions
│   ├── utils/
│   │   ├── node_registry.py  # Node catalog
│   │   ├── workflow_store.py # Workflow persistence
│   │   ├── permission_manager.py # Permission handling
│   │   └── stream_llm.py     # LLM utilities
│   └── README.md
├── server.py                 # FastAPI server
├── requirements.txt          # Dependencies
└── README.md                # This file
```

### Extending the System

1. **Add New Nodes**: Register in node registry and implement in executor
2. **Add New Flows**: Create new flow functions in `flow.py`
3. **Add New Utilities**: Extend the utils package
4. **Add New Endpoints**: Extend the FastAPI server

### Testing

```bash
# Test the server
curl http://localhost:8000/health

# Test node registry
curl http://localhost:8000/api/v1/nodes

# Test workflow store
curl http://localhost:8000/api/v1/workflows
```

## 🤝 Contributing

1. Follow the PocketFlow design patterns
2. Add comprehensive documentation
3. Include error handling and logging
4. Test with various user scenarios
5. Update the node registry for new functionality

## 📝 License

This project follows the same license as PocketFlow.

---

**Note**: This is a demonstration system with mock implementations for external services. In production, you would integrate with real APIs for flight search, payment processing, etc.
