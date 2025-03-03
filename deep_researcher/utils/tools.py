import os
import re
import requests
from bs4 import BeautifulSoup
from typing import List
from langchain_core.tools import Tool
from langchain_community.retrievers import WikipediaRetriever
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_community.retrievers import ArxivRetriever


class GoogleSearchExtractor:
    def __init__(self, api_key, cse_id, num_results=3, max_char_length=1000):
        self.google_search = GoogleSearchAPIWrapper(
            google_api_key=api_key,
            google_cse_id=cse_id,
            k=num_results
        )
        self.k = num_results
        self.max_char_length = max_char_length

    def clean_text(self, text):
        """Clean the text by removing newlines and tabs."""
        text = re.sub(r'[\n\t]+', ' ', text)
        return text

    def extract_html(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return self.clean_text(soup.get_text())[:self.max_char_length]
        return ""

    def search(self, query):
        search_results = self.google_search.results(query, self.k)
        print(len(search_results))
        extracted_results = []
        for result in search_results:
            print(result["title"])
            extracted_results.append({
                "title": result["title"],
                "content": self.extract_html(result["link"]),
                "url": result["link"]
            })
        return extracted_results

# google_search_extractor = GoogleSearchExtractor(
#     api_key=os.getenv("GOOGLE_API_KEY"),
#     cse_id=os.getenv("GOOGLE_CSE_ID"))

# results = google_search_extractor.search("Samsung company valuation")
# print(results)


# google search tool
# google_retriever = GoogleSearchAPIWrapper(
#     google_api_key=os.environ["GOOGLE_API_KEY"],
#     google_cse_id=os.environ["GOOGLE_CSE_ID"],
#     k=5
# )


# def call_google_search(query: str, num_results: int = 5) -> List[dict]:
#     search_results = google_retriever.results(query, num_results=num_results)
#     formatted_results = []
#     for result in search_results:
#         formatted_results.append(
#             {   "search_query": query,
#                 "title": result["title"],
#                 "source": result["link"],
#                 "content": preprocess_long_text(result["snippet"]),
#                 "search_engine": "Google"
#             }
#         )
#     return formatted_results


# search_google = Tool(
#     name="search_google",
#     description="Search Google for the given query. Best for broad, diverse queries, including news, commercial, and up-to-date web content.",
#     func=call_google_search
# )


def preprocess_long_text(text):
    """Preprocess long text by removing newlines and tabs."""
    # Remove newlines and tabs
    text = re.sub(r'[\n\t]+', ' ', text)
    # Truncate to 1000 characters
    if len(text) > 1000:
        text = text  # [:1000]
    return text


# Convert TavilySearchResults into a tool
tavily_retriever = TavilySearchResults(
    api_key=os.environ["TAVILY_API_KEY"],
    max_results=2
)


def call_tavily_search(query: str) -> List[dict]:
    search_results = tavily_retriever.invoke(query)
    formatted_results = []
    for result in search_results:
        formatted_results.append(
            {
                "search_query": query,
                "title": "",
                "source": result["url"],
                "content": preprocess_long_text(result["content"]),
                "search_engine": "Tavily"
            }
        )
    return formatted_results


search_tavily = Tool(
    name="search_tavily",
    description="Search Tavily for the given query. Best for real-time web search and retrieving structured, domain-specific information efficiently.",
    func=call_tavily_search
)


# Convert ArxivRetriever into a tool
arxiv_retriever = ArxivRetriever(
    load_max_docs=3
)


def call_arxiv_search(query: str) -> List[dict]:
    search_results = arxiv_retriever.invoke(query)
    formatted_results = []
    for result in search_results:
        formatted_results.append(
            {
                "search_query": query,
                "title": result.metadata["Title"],
                "source": result.metadata["Entry ID"],
                "content": preprocess_long_text(result.page_content),
                "search_engine": "arXiv"
            }
        )
    return formatted_results


search_arxiv = Tool(
    name="search_arxiv",
    description="Search Arxiv for the given query. arXiv → Best for academic research, technical papers, and cutting-edge scientific studies in fields like ML, physics, and mathematics.",
    func=call_arxiv_search
)


# wikipedia tool
wikipedia_retriever = WikipediaRetriever(
    top_k_results=3
)


def call_wikipedia_search(query: str) -> List[dict]:
    search_results = wikipedia_retriever.invoke(query)
    formatted_results = []
    for result in search_results:
        formatted_results.append(
            {
                "search_query": query,
                "title": result.metadata["title"],
                "source": result.metadata["source"],
                "content": preprocess_long_text(result.metadata["summary"]),
                "search_engine": "Wikipedia"
            }
        )
    return formatted_results


search_wikipedia = Tool(
    name="search_wikipedia",
    description="Search Wikipedia for the given query. Best for general knowledge and historical summaries with human-curated content.",
    func=call_wikipedia_search
)
