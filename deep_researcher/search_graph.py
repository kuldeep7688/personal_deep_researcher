# general imports
from langgraph.graph import StateGraph, START, END
from deep_researcher.utils.nodes import (
    create_search_query, call_search_tools,
)
from deep_researcher.utils.state import (
    SearchGraphState, SearchGraphOutputState
)

# create search graph
search_graph_builder = StateGraph(
    SearchGraphState, output=SearchGraphOutputState
)
search_graph_builder.add_node("create_search_query", create_search_query)
search_graph_builder.add_node("call_search_tools", call_search_tools)

search_graph_builder.add_edge(START, "create_search_query")
search_graph_builder.add_edge("create_search_query", "call_search_tools")
search_graph_builder.add_edge("call_search_tools", END)
search_graph = search_graph_builder.compile()
