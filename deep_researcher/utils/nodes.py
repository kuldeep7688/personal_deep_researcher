# general imports
# import os

# langchain imports
from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)
from langgraph.constants import Send
# from langgraph.types import interrupt

# state imports
from deep_researcher.utils.state import (
    SearchGraphState,
    ResearcherState,
    OrchestratorState,
    TopicList, WrittenSection, PlannedSections
)

# tools imports
from deep_researcher.utils.tools import (
    search_arxiv, search_tavily,
    search_wikipedia
)


# Node for Search Graph
def create_search_query(state: SearchGraphState):
    """Create a search query for the topic."""
    llm_search_with_tools = init_chat_model(
        model="gpt-40-mini",
        temperature=0,
        max_tokens=500
    ).bind_tools(
        search_wikipedia, search_tavily, search_arxiv
    )
    out = llm_search_with_tools.invoke(
        [
            SystemMessage(content="You are a research assistant. You will be given a topic. Create a query that is helpful in searching the internet and will fetch meaningful information that helpful in writing. You can use the following tools to search the internet: Wikipedia, Tavily, Arxiv. Use the best tool to do search."),
            HumanMessage(content=f"{state['topic']} in {state['of_section']}"),
        ]
    )
    return {
        "search_tools_to_call": out.tool_calls
    }


def call_search_tools(state: SearchGraphState):
    tool_calls = state["search_tools_to_call"]
    print(
        f"\n\nFor Section : {state['of_section']} For topic : {state['topic']} the tool calls are :\n")
    for tool_call in tool_calls:
        print(
            f"Tool Name : {tool_call['name']} | Tool Args : {tool_call['args']['__arg1']}")
    print("\n\n")

    search_results = []
    new_search_queries = set()
    for tool_call in tool_calls:
        if tool_call["name"] == "search_wikipedia":
            if tool_call["args"] in state["search_queries_already_used"]:
                continue
            else:
                new_search_queries.add(tool_call["args"]["__arg1"])
                search_results_from_wikipedia = search_wikipedia.invoke(
                    tool_call["args"])
                if len(search_results_from_wikipedia) > 0:
                    search_results.extend(search_results_from_wikipedia)

        elif tool_call["name"] == "search_tavily":
            if tool_call["args"] in state["search_queries_already_used"]:
                continue
            else:
                new_search_queries.add(tool_call["args"]["__arg1"])
                search_results_from_tavily = search_tavily.invoke(
                    tool_call["args"])
                if len(search_results_from_tavily) > 0:
                    search_results.extend(search_results_from_tavily)
        elif tool_call["name"] == "search_arxiv":
            if tool_call["args"] in state["search_queries_already_used"]:
                continue
            else:
                new_search_queries.add(tool_call["args"]["__arg1"])
                search_results_from_arxiv = search_arxiv.invoke(
                    tool_call["args"])
                if len(search_results_from_arxiv) > 0:
                    search_results.extend(search_results_from_arxiv)
        # elif tool_call["name"] == "search_google":
        #     if tool_call["args"] in state["search_queries_already_used"]:
        #         continue
        #     else:
        #         new_search_queries.add(tool_call["args"]["__arg1"])
        #         search_results_from_google = search_google.invoke(
        #             tool_call["args"])
        #         if len(search_results_from_google) > 0:
        #             search_results.extend(search_results_from_google)

    print("tool calls done")
    return {
        "search_results": search_results,
        "search_queries_already_used": list(new_search_queries)
    }


# Nodes for Researcher Graph
def get_important_topics(state: ResearcherState):
    """Get important topics from the research worker."""
    topic_identifying_llm = init_chat_model(
        model="google_genai:gemini-1.5-flash",
        temperature=0,
        max_tokens=500
    ).with_structured_output(TopicList)
    out = topic_identifying_llm.invoke(
        [
            SystemMessage(content="Given a section title and overview. Identify the topics which will be helpful to search the internet to better understanf the section. The topics must be less than 3 and must be relevant to the section."),
            HumanMessage(
                content=f"Section: {state['section']}\nSection Overview: {state['section_overview']}"),
        ]
    )
    print(
        f"\n\nThe topics identified for the Section {state['section']} are :\n {out.topics}\n\n")
    return {
        "topics_of_section": out.topics
    }


def assign_search_workers(state: ResearcherState):
    """Assign search workers to the topics."""
    print("\n\nAssigning search workers to the topics.\n\n")
    return [
        Send("execute_search_graph", {"topic": topic, "of_section": state["section"]}) for topic in state["topics_of_section"]
    ]


def section_writer(state: ResearcherState):
    """Synthesize the section."""
    print(f"\n\nWriting the section : {state['section']}.\n\n")
    section_writer_llm = init_chat_model(
        model="google_genai:gemini-1.5-flash",
        temperature=0.2,
        max_tokens=2048,
    ).with_structured_output(WrittenSection)

    out = section_writer_llm.invoke(
        [
            SystemMessage(content="You are a research assistant. You will be given a section title and overview. You will be given search results, filter them and select the useful ones to write the content of the section."),
            HumanMessage(
                content=f"Section: {state['section']}\nSection Overview: {state['section_overview']}\n  Search Results: {state['search_results']}"),
        ]
    )
    print(f"\n\nThe section {state['section']} is written.\n\n")
    return {
        "compiled_sections": [out]
    }


# Nodes for Orchestrator Graph
def generate_plan(state: OrchestratorState):
    """Generate an outline for the report."""
    print("Generating plan using deepseek")
    planner_llm = init_chat_model(
        model="groq:deepseek-r1-distill-qwen-32b",
        temperature=0.2,
        max_tokens=2048,
        max_retries=3
    )
    out = planner_llm.invoke(
        [
            SystemMessage(content="You are a research assistant. You will be given a main topic and an outline. You will generate a plan for a report. The plan must have sections and an overview for every section. Overview should cover the main topics and points of the section."),
            HumanMessage(
                content=f"Main Topic: {state['main_topic']}\n Outline: {state['outline']}"),
        ]
    )
    return {
        "plan_in_text": out
    }


def generate_plan_schema(state: OrchestratorState):
    """Extract the schema out of a plan mentioned in text."""
    print("Fitting plan into a schema")
    structured_planner = init_chat_model(
        model="openai:gpt-4o",
        max_tokens=2048,
        temperature=0
    ).with_structured_output(PlannedSections)
    structured_plan = structured_planner.invoke(
        [
            SystemMessage(
                content="You are a research assistant. You will be given a plan for a report. You will extract the schema out of the plan."),
            HumanMessage(content=f"Plan: {state['plan_in_text']}"),
        ]
    )
    print("The structured plan is :\n:")
    for section in structured_plan.sections:
        print(
            f"Section: {section.title}\nOverview: {section.overview}\nWeb Search Required: {section.web_search_required}\n\n")
    return {
        "structured_plan": structured_plan.sections
    }


def web_search_required_routing(state: OrchestratorState):
    """Assign initial section writing to the research worker."""
    print("\n\n Assigning writing workers to the sections which require web search.\n\n")
    for section in state["structured_plan"]:
        if section.web_search_required is True:
            return "web_search_required"
    return "no_web_search_required"


def assign_web_search_writing_workers(state: OrchestratorState):
    """Assign search workers to the topics."""
    print("\n\n Assigning writing workers to the sections which require web search.\n\n")
    return [
        Send(
            "write_sections_with_search",
            {
                "section": section.title,
                "section_overview": section.overview,
                "search_results": state["search_results"]
            }
        )
        for section in state["structured_plan"]
        if section.web_search_required is True
    ]


def combine_written_sections(state: OrchestratorState):
    """Combine the written sections."""
    print("\n\n Combining the already written sections.\n\n")
    web_searched_written_section_info = ""
    for section in state["compiled_sections"]:
        web_searched_written_section_info += f"Section: {section.title}\nContent: {section.content}\nSources: {section.sources}\n\n"
    return {
        "combined_written_sections": web_searched_written_section_info
    }


def assign_no_web_search_writing_workers(state: OrchestratorState):
    """Assign search workers to the topics."""
    print("\n\n Assigning writing workers to the sections which do not require web search.\n\n")
    return [
        Send(
            "write_sections_without_search",
            {
                "section": section.title,
                "section_overview": section.overview,
                "combined_written_sections": state["combined_written_sections"],
                "search_results": state["search_results"]
            }
        )
        for section in state["structured_plan"]
        if section.web_search_required is False
    ]


def write_sections_without_search(state: ResearcherState):
    """Write the remaining sections which do not require web search."""
    print("\n\n Writing the sections which do not require web search.\n\n")
    web_searched_written_section_info = state["combined_written_sections"]
    section_writer_llm = init_chat_model(
        model="google_genai:gemini-1.5-flash",
        temperature=0.2,
        max_tokens=2048,
    ).with_structured_output(WrittenSection)
    out = section_writer_llm.invoke(
        [
            SystemMessage(
                content="You are a research assistant. You will be given a section title and overview and already written sections to write the content of this section."),
            HumanMessage(
                content=f"Section: {state['section']}\nSection Overview: {state['section_overview']}\n  Written Sections : {web_searched_written_section_info}"),
        ]
    )
    return {
        "compiled_sections": [out]
    }


def write_final_report(state: OrchestratorState):
    """Write the final report."""
    print("\n\n Writing the final report.\n\n")
    final_report = ""
    for section in state["compiled_sections"]:
        final_report += f"Section: {section.title}\nContent: {section.content}\nSources: {section.sources}\n\n"

    return {
        "final_report": final_report
    }
