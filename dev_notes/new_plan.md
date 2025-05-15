# new plan

what is the purpose?
    - to help devs transform the way they view and analyze code

how to achieve it ?
    - through AI agents

what design and tools should the agent/s have?
    - copilot (cot model),visualizer
    - every agent should be able to communicate with each other
    - the final result should be the precise and concise summary of the project

what makes us different?
    - explaining the interdependencies
    - visualizing the code structure
    - possible errors and recommendations
    - how you can build your solution on this existing solution

possible future additions
    - instead of you searching for existing solution , we do it for you.

defining the agent
    - The AI agents' definition: Each agent could be a microservice. For example, a Code Parser Agent that processes code into ASTs and stores them. A Dependency Analyzer Agent that builds the graph. An Explanation Agent that uses LLMs to generate docs. A Recommendation Agent that suggests where to add new code. These agents can subscribe to events, like a file upload, and process accordingly

Core System Components
tech_stack = {
    "processing": {
        "language": "Python 3.11+",
        "async_framework": "AnyIO or asyncio",
        "distributed_tasks": "Celery + Redis",
        "code_parsing": "Tree-sitter with Python bindings",
        "ai_integration": "LangChain + LlamaIndex"
    },
    "orchestration": {
        "workflow_engine": "n8n","gumloop"
        "message_broker": "RabbitMQ",
        "distributed_coordination": "Apache ZooKeeper"
    },
    "storage": {
        "code_storage": "MinIO (S3-compatible)",
        "vector_database": "ChromaDB",
        "graph_database": "Neo4j",
        "metadata": "PostgreSQL with TimescaleDB"
    },
    "visualization": {
        "web_framework": "FastAPI + React",
        "graph_rendering": "Cytoscape.js + WebGL",
        "diagram_generation": "Diagram as Code (D2 lang)"
    }
}