# Personal Deep Researcher

This is a personal Deep Research tool built using Langgraph. It automates the process of researching and compiling information on various topics by leveraging multiple search tools and language models.

## Features

- Generates a detailed report on a topic following the outline with sources.
- Integrates three graphs, Orchestrator graphs uses Researcher graph which uses Searcher graphs.
- Uses Interrupt API from langgraph to take human input for planning.
- Integrates GPT-4o, 4o-mini, Gemini-flash-1.5 and deepseek-r1-distill-qwen-32b effectively to reduce the cost per million tokens.
- Uses Send and Command API from Langgraph to simultaneously execute Research graph and Searcher graphs for each section.
- Searcher graph decides between Tavily, Wikipedia and Arxiv search engines to get the most relevant information.
- Keeps track of the search queries to avoid querying the same term multiple times.
- Research graph decides whether more web search is needed or not.

## Project Structure

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables by creating a [.env](http://_vscodecontentref_/3) file in the root directory with the following content:
    ```env
    OPENAI_API_KEY = "your_openai_api_key"
    ANTHROPIC_API_KEY = "your_anthropic_api_key"
    GEMINI_API_KEY = "your_gemini_api_key"
    HF_TOKEN = "your_hf_token"
    TAVILY_API_KEY = "your_tavily_api_key"
    GOOGLE_API_KEY = "your_google_api_key"
    GOOGLE_CSE_ID = "your_google_cse_id"
    NEWSAPI_API_KEY = "your_newsapi_api_key"
    GROQ_API_KEY = "your_groq_api_key"
    GEMINI_API_KEY = "your_gemini_api_key"
    ```

## Usage

1. To run the deep research agent, execute:
    ```sh
    python deep_researcher/deep_research_agent.py
    ```

2. To run the search graph, execute:
    ```sh
    python deep_researcher/search_graph.py
    ```

3. To run the researcher graph, execute:
    ```sh
    python deep_researcher/researcher_graph.py
    ```

## Project Components

- **deep_research_agent.py**: Main script to run the deep research agent.
- **researcher_graph.py**: Script to build and run the researcher graph.
- **search_graph.py**: Script to build and run the search graph.
- **utils/nodes.py**: Contains the nodes (functions) used in the graphs.
- **utils/state.py**: Defines the state models used in the graphs.
- **utils/tools.py**: Contains the tools used for searching information.

## License

This project is licensed under the MIT License.
