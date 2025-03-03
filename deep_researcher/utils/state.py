import operator
from pydantic import BaseModel, Field
from typing import List
from typing_extensions import Annotated, TypedDict


class TopicList(BaseModel):
    topics: List[str] = Field(
        description="List of topics which will be helpful in understanding. Must not be more than three topics.",
    )


class SectionPlan(BaseModel):
    title: str = Field(
        description="Title of the section",
    )
    overview: str = Field(
        description="Overview of the section",
    )
    web_search_required: bool = Field(
        description="Whether web search is required for this section.",
    )


class PlannedSections(BaseModel):
    sections: List[SectionPlan] = Field(
        description="Sections of the report.",
    )


class WrittenSection(BaseModel):
    title: str = Field(
        description="Title of the section",
    )
    content: str = Field(
        description="Content of the section",
    )
    sources: str = Field(
        description="Source urls of the section",
    )


class SearchGraphState(TypedDict):
    """State for the Research Worker agent."""
    topic: str
    of_section: str
    search_tools_to_call: list
    search_queries_already_used: Annotated[list, operator.add]
    search_results: Annotated[list, operator.add]


class SearchGraphOutputState(TypedDict):
    """State for the Research Worker agent."""
    search_queries_already_used: list[str]
    search_results: list[str]


class ResearcherState(TypedDict):
    """State for the Researcher agent."""
    section: str
    section_overview: str
    topics_of_section: list
    search_queries_already_used: Annotated[list, operator.add]
    compiled_sections: Annotated[list, operator.add]
    search_results: Annotated[list, operator.add]
    combined_written_sections = str


class ResearcherOutputState(TypedDict):
    """Output State for the Researcher agent."""
    search_queries_already_used: list[str]
    compiled_sections: list[WrittenSection]
    search_results: list[dict]


class OrchestratorState(TypedDict):
    main_topic: str
    outline: str
    plan_in_text: str
    structured_plan: List[SectionPlan]
    feedback_on_report_plan: str
    compiled_sections: Annotated[list, operator.add]
    combined_written_sections: str
    search_results: Annotated[list, operator.add]
    search_queries_already_used: Annotated[list, operator.add]
    final_report: str
