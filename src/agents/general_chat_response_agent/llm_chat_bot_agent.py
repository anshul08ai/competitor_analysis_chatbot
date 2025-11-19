from langgraph.graph import StateGraph,START,END
from langgraph.graph import StateGraph,START,END
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Literal,Annotated,List
from langchain_core.messages import HumanMessage,SystemMessage
from pathlib import Path
import sys,requests, yaml
from typing import Set, List, Dict, Any

src_path = Path.cwd().parent 
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

prompt_path = Path.cwd().parent
if str(prompt_path) not in sys.path:
    sys.path.insert(0, str(prompt_path))

from prompt_engineering.prompt_template import general_purpose_system_prompt, general_purpose_human_prompt
from llm.lite_llm_client import create_chat_model
from utils.tools import chat_store_api_call,collect_format_chat_history


def llm_chat_bot(state):
    try:
        # TODO : (API) IF new chat create session
        # TODO : (API) Collect chat history and pass to llm   ||| formatised
        # TODO : (API) Collect relevant document with vector db  ||| summarize
        # TODO : (UPDATE_PROMPT---athena) For this response will not be more that 400 words
        
        # format_chat_history = collect_format_chat_history(session_id)
        # print(f" FORMAT_CHAT_HISTORY : {format_chat_history}")
        user_query= state['query']
        system_msg = SystemMessage(content=general_purpose_system_prompt)
        human_msg = HumanMessage(content=general_purpose_human_prompt.format(user_query=user_query))
        connection_status = create_chat_model()

        if not connection_status.get('status'):
            state['output'] = "Unable to perfrom operation" +  + str(connection_status.text)
        llm =connection_status['model']
        response = llm.invoke([system_msg, human_msg]).content
        state['output']= response

        # TODO : (API) Save Response in Cache for particular session
        # messages = [
        #     {
        #         'role':'User',
        #         'message':user_query
        #     },
        #     {
        #         'role':'Assistant',
        #         'message':response
        #     }
        # ]
        # chat_save = chat_store_api_call(messages,session_id)
        # print(f"NORMAL_CHAT_SAVE_STATUS : {chat_save}")
        return state
    except Exception as e:
        state['output'] = "Unable to perfrom operation" + str(e)
        return state
    
