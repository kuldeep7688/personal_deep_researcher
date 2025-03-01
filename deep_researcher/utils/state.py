from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from typing_extensions import Annotated, Literal, TypedDict


class SearchGraphState(TypedDict):
    """State for the Research Worker agent."""
    topic: str
    of_section: str
    search_tools_to_call: list
    search_queries_already_used: Annotated[list, operator.add]
    search_results: Annotated[list, operator.add]


class ResearcherState(TypedDict):
    """State for the Researcher agent."""
    section: str
    section_overview: str
    topics_of_section: list
    search_queries_already_used: Annotated[list, operator.add]
    compiled_sections: Annotated[list, operator.add]
    search_results: Annotated[list, operator.add]


class OrchestratorState(TypedDict):
    main_topic: str
    outline: str
    plan_in_text: str
    structured_plan: List[Section]
    compiled_sections: Annotated[list, operator.add]
    combined_written_sections: str
    search_results: Annotated[list, operator.add]
    search_queries_already_used: Annotated[list, operator.add]
    final_report: str
