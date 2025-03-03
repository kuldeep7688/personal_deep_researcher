from langgraph.graph import StateGraph, START, END
from deep_researcher.utils.nodes import (
    create_search_query, call_search_tools,
    get_important_topics, assign_search_workers, section_writer,
)
from deep_researcher.utils.state import (
    SearchGraphState, SearchGraphOutputState,
    ResearcherState, ResearcherOutputState,
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


# create researcher_graph
researcher_graph_builder = StateGraph(
    ResearcherState, output=ResearcherOutputState
)
researcher_graph_builder.add_node("get_important_topics", get_important_topics)
researcher_graph_builder.add_node(
    "execute_search_graph", search_graph_builder.compile()
)
researcher_graph_builder.add_node(
    "assign_search_workers", assign_search_workers
)
researcher_graph_builder.add_node("section_writer", section_writer)

researcher_graph_builder.add_edge(START, "get_important_topics")
researcher_graph_builder.add_edge(
    "get_important_topics", "assign_search_workers"
)
researcher_graph_builder.add_edge("execute_search_graph", "section_writer")
researcher_graph_builder.add_edge("section_writer", END)
researcher_graph = researcher_graph_builder.compile()
