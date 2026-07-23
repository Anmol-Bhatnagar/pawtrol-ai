from langgraph.graph import END, StateGraph
from src.agents.edges import decide_next_step
from src.agents.nodes import generator_node, router_node, search_node
from src.agents.state import GraphState
from src.services.memory import get_checkpointer

# Initialize state graph builder
builder = StateGraph(GraphState)

# Register nodes
builder.add_node("router_node", router_node)
builder.add_node("search_node", search_node)
builder.add_node("generator_node", generator_node)

# Configure Entry Point
builder.set_entry_point("router_node")

# Configure Conditional Edges
builder.add_conditional_edges(
    "router_node",
    decide_next_step,
    {
        "search_node": "search_node",
        "generator_node": "generator_node",
    },
)

# Standard Edges
builder.add_edge("search_node", "generator_node")
builder.add_edge("generator_node", END)

# Set persistent memory checkpointer
memory_checkpointer = get_checkpointer()

# Compile the execution graph
graph = builder.compile(checkpointer=memory_checkpointer)
