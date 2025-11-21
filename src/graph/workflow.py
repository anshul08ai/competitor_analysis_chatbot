from langgraph.graph import StateGraph,START,END
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[0] 
print(ROOT,'llllllllllllllllllll') # points to src/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def get_router(state):
    router_output= state['router']
    print(state)
    return router_output

agent_path = Path(__file__).resolve().parents[1] 
if str(agent_path) not in sys.path:
    sys.path.insert(0, str(agent_path))

class AgentGraph:
    def __init__(self):
        from state import State
        self.graph = StateGraph(State)
        self._setup_nodes()
        self._setup_edges()

    def _setup_nodes(self):
        from agents.router_agent.router_selection import router
        from agents.general_chat_response_agent.llm_chat_bot_agent import llm_chat_bot
        from agents.collector_agent.search_summarize_url_data import search_over_intenet_with_ddg as data_over_web
        from agents.collector_agent.get_relevent_query import get_relevent_query
        from agents.verifier_agent.verifier import content_verifier
        from agents.analyzer_agent.analyzer import analyze_generated_output
        from agents.report_generator_agent.report_generate import generate_summarize_report
        from agents.need_refinement import needs_refinement_status
        from agents.refine_search_summarize_data import web_data_fetch
        from agents.vector_database_agent.data_fetch_via_db import db_data_fetch

        self.graph.add_node("router", router)
        self.graph.add_node("llm_chat_bot", llm_chat_bot)
        self.graph.add_node("get_relevent_query", get_relevent_query)
        self.graph.add_node("search_summarize_data", data_over_web)
        self.graph.add_node("content_verifier_data", content_verifier)
        self.graph.add_node("analyze_generated_data", analyze_generated_output)
        self.graph.add_node("summarize_report", generate_summarize_report)
        self.graph.add_node("web_data_scrap", web_data_fetch)
        self.graph.add_node("similar_db_data", db_data_fetch)

    def _setup_edges(self):
        self.graph.add_edge(START, 'router')
        self.graph.add_conditional_edges('router', self.get_router, {
            "llm_chat_bot": "llm_chat_bot",
            "get_relevent_query": "get_relevent_query"
        })
        self.graph.add_edge("llm_chat_bot", END)
        self.graph.add_edge("get_relevent_query", "search_summarize_data")
        self.graph.add_edge("search_summarize_data", "web_data_scrap")
        self.graph.add_edge("web_data_scrap", "similar_db_data")
        self.graph.add_edge("similar_db_data", "analyze_generated_data")
        self.graph.add_edge("analyze_generated_data", "summarize_report")
        self.graph.add_edge("summarize_report", END)

    @staticmethod
    def get_router(state):
        router_output = state['router']
        print(state)
        return router_output

    def compile(self):
        return self.graph.compile()

print('compiled')

