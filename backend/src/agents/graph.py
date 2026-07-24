from langgraph.graph import END, StateGraph
from src.agents.edges import decide_next_step
from src.agents.nodes import agent_node, tools_node
from src.agents.state import GraphState
from src.services.memory import get_checkpointer

# Initialize state graph builder
builder = StateGraph(GraphState)

# Register nodes
builder.add_node("agent_node", agent_node)
builder.add_node("tools_node", tools_node)

# Configure Entry Point
builder.set_entry_point("agent_node")

# Configure Conditional Edges from agent_node
builder.add_conditional_edges(
    "agent_node",
    decide_next_step,
    {
        "tools_node": "tools_node",
        "end": END,
    },
)

# After tool execution, loop back to agent to generate final response
builder.add_edge("tools_node", "agent_node")

# Set persistent memory checkpointer
memory_checkpointer = get_checkpointer()

# Compile the execution graph
graph = builder.compile(checkpointer=memory_checkpointer)
