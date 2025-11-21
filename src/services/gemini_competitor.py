
from pydantic import BaseModel

from graph.workflow import AgentGraph

agent_graph = AgentGraph()
compiled = agent_graph.compile()

class SearchRequest(BaseModel):
    query: str

async def perform_agent_graph_search(query: str):
    try:
        output = compiled.invoke({'query': query})
        return output
    except Exception as e:
        raise RuntimeError(f"Agent graph invocation failed: {e}")
