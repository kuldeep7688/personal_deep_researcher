# general imports
from langgraph.graph import StateGraph, START, END
from deep_researcher.utils.nodes import (
    create_search_query, call_search_tools,
    get_important_topics, assign_search_workers, section_writer,
    generate_plan, generate_plan_schema,
    web_search_required_routing,
    assign_no_web_search_writing_workers, assign_web_search_writing_workers,
    combine_written_sections, write_final_report, write_sections_without_search
)
from deep_researcher.utils.state import (
    SearchGraphState, SearchGraphOutputState,
    ResearcherState, ResearcherOutputState,
    OrchestratorState
)

# create search graph
search_graph_builder = StateGraph(
    SearchGraphState, output=SearchGraphOutputState
)
search_graph_builder.add_node("create_search_query", create_search_query)
search_graph_builder.add_node("call_search_tools", call_search_tools)

search_graph_builder.add_edge(START, "create_search_query")
search_graph_builder.add_edge("create_search_query", "call_search_tools")


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


# create the main graph
graph_builder = StateGraph(OrchestratorState)
graph_builder.add_node("generate_plan", generate_plan)
graph_builder.add_node("generate_plan_schema", generate_plan_schema)
graph_builder.add_node(
    "write_sections_with_search", researcher_graph_builder.compile()
)
graph_builder.add_node(
    "assign_web_search_writing_workers", assign_web_search_writing_workers
)
# graph_builder.add_node(
#     "assign_no_web_search_writing_workers",
#     assign_no_web_search_writing_workers
# )
graph_builder.add_node("combine_written_sections", combine_written_sections)
graph_builder.add_node(
    "write_sections_without_search", write_sections_without_search
)
graph_builder.add_node("write_final_report", write_final_report)

graph_builder.add_edge(START, "generate_plan")
graph_builder.add_edge("generate_plan", "generate_plan_schema")
# graph_builder.add_conditional_edges(
#     "generate_plan_schema", assign_web_search_writing_workers,
#     ["write_sections_with_search"]
# )
# graph_builder.add_edge(
#     "generate_plan_schema", "assign_web_search_writing_workers"
# )
graph_builder.add_conditional_edges(
    "generate_plan_schema", web_search_required_routing, {
        "web_search_required": "assign_web_search_writing_workers",
        "no_web_search_required": "combine_written_sections"
    }
)
graph_builder.add_edge(
    "write_sections_with_search", "combine_written_sections",
)
graph_builder.add_conditional_edges(
    "combine_written_sections", assign_no_web_search_writing_workers,
    ["write_sections_without_search"]
)
graph_builder.add_edge(
    "write_sections_without_search", "write_final_report"
)
graph_builder.add_edge(
    "write_final_report", END
)
graph = graph_builder.compile()
