from langgraph.graph import StateGraph,START,END
from state import State
from pathlib import Path
import sys

import sys
from pathlib import Path
 
ROOT = Path(__file__).resolve().parents[1]  # points to src/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

print(f"ROOT : {ROOT}")
def get_router(state):
    router_output= state['router']
    print(state)
    return router_output

agent_path = Path.cwd().parent / "src"
print('mmmmmmmmmmmmmmmm',agent_path)
if str(agent_path) not in sys.path:
    sys.path.insert(0, str(agent_path))

# sys.path.append(r"C:\Users\anshul.jain\Desktop\capstone\official\project\Deep_Research\src\agents\collector_agent\get_relevent_query.py")

# sys.path.append (path)

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


graph = StateGraph(State)
graph.add_node("router",router)
graph.add_node("llm_chat_bot",llm_chat_bot)
graph.add_node("get_relevent_query",get_relevent_query)
graph.add_node("search_summarize_data",data_over_web)
# graph.add_node("content_verifier_data",content_verifier)
graph.add_node('analyze_generated_data',analyze_generated_output)
graph.add_node("summarize_report",generate_summarize_report)
graph.add_node("web_data_scrap",web_data_fetch)
graph.add_node("similar_db_data",db_data_fetch)


graph.add_edge(START,'router')
graph.add_conditional_edges('router',get_router,{"llm_chat_bot":"llm_chat_bot","get_relevent_query":"get_relevent_query"})
graph.add_edge("llm_chat_bot",END)
graph.add_edge("get_relevent_query","search_summarize_data")
graph.add_edge("search_summarize_data","web_data_scrap")
graph.add_edge("web_data_scrap","similar_db_data")
graph.add_edge("similar_db_data","analyze_generated_data")
graph.add_edge("analyze_generated_data","summarize_report")
graph.add_edge("summarize_report",END)
compiled= graph.compile()



