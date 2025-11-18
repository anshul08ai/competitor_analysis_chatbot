from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.messages import SystemMessage, HumanMessage
from langdetect import detect
import re
from dateparser import parse
import requests
import bs4

from pathlib import Path
import sys
prompt_path = Path.cwd().parent / "src" / "prompt_engineering"
if str(prompt_path) not in sys.path:
    sys.path.insert(0, str(prompt_path))

llm_path = Path.cwd().parent / "src" / "llm"
if str(llm_path) not in sys.path:
    sys.path.insert(0, str(llm_path))

from prompt_template import summerize_data_for_query
from lite_llm_client import create_chat_model

import asyncio
from fastapi.concurrency import run_in_threadpool
 
 
class DuckDuckGo:
    def __init__(self, max_results=3):
        self.wrapper = DuckDuckGoSearchAPIWrapper(max_results=max_results)
 
    # --------------------------------------------------
    # 1. SEARCH NEWS
    # --------------------------------------------------
    async def search_duckduckgo(self, query: str):
        """async wrapper for duckduckgo search"""
        def _search():
            results = self.wrapper.results(
                query + " news published recently english only",
                max_results=self.wrapper.max_results,
            )
 
            english = []
            for r in results:
                try:
                    text = r.get("snippet") or r.get("body") or r.get("title", "")
                    if detect(text) == "en":
                        english.append(r)
                except:
                    continue
 
            return english[:3]
 
        return await run_in_threadpool(_search)
 
    # --------------------------------------------------
    # 2. FETCH WEB CONTENT & SUMMARIZE
    # --------------------------------------------------
    async def fetch_and_summarize(self, url: str, user_query: str):
        """fetch webpage & summarize using LLM async safe"""
 
        def _fetch():
            if not url.startswith("https"):
                return None
 
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = bs4.BeautifulSoup(res.text, "lxml")
            return soup.body.get_text(" ", strip=True) if soup.body else ""
 
        text = await run_in_threadpool(_fetch)
        if not text:
            return None
 
        # Summarization LLM
        def _summarize():
            conn = create_chat_model()
            if not conn.get("status"):
                return text[:2000]
 
            llm = conn["model"]
            system_msg = SystemMessage(content="Summarize news professionally.")
            human_msg = HumanMessage(
                content=summerize_data_for_query.format(
                    user_query=user_query,
                    data=text[:20000]
                )
            )
            return llm.invoke([system_msg, human_msg]).content
 
        return await run_in_threadpool(_summarize)
    
    def fetch_web_data(self, url,user_query):
        try:
            if str(url).startswith('https:'):
                res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = bs4.BeautifulSoup(res.text, "lxml")
                text_content = soup.body.get_text(" ", strip=True) if soup.body else ""
                connection_status = create_chat_model()

                if not connection_status.get('status'):
                    print('why here')
                    return text_content[:5000]
                system_msg = SystemMessage(content="You are a helpful assistant specializing in news summarization.")
                human_msg = HumanMessage(content=summerize_data_for_query.format(user_query=user_query,data=text_content[:20000]))
                llm =connection_status['model']
                output=llm.invoke([system_msg, human_msg])
                return output.content
            else:
                return  None
        except Exception as e:
            print('eeeeeeeeeeeeee',e)
            return None
 
    # --------------------------------------------------
    # 3. MAIN FUNCTION FOR A SINGLE QUERY
    # --------------------------------------------------
    async def get_all_data_about(self, query: str):
        """
        Fully async → search → fetch → summarize
        """
        # results = await self.search_duckduckgo(query)
        url_list = []
        for item in query:
            urls = self.search_duckduckgo(item)
            url_list.extend(urls)
        
        # url_list = await asyncio.gather(*tasks)
        
        output = url_list
 
        # tasks = []
        # for item in final_urls:
        #     url = item["link"]
        #     tasks.append(self.fetch_and_summarize(url, query))
 
        # summaries = await asyncio.gather(*tasks)
 
        # output = {}
        # for item, summary in zip(final_urls, summaries):
        #     url = item["link"]
        #     output['content'] = {
        #         'query': query,
        #         "url"  : url,
        #         "title": item.get("title"),
        #         "snippet": item.get("snippet"),
        #         "summary": summary
        #     }
 
        return output
 

# class DuckDuckGo:
#     def __init__(self, max_results=3):
#         self.wrapper = DuckDuckGoSearchAPIWrapper(max_results=max_results)

# class DuckDuckGo:
#     def __init__(self, max_results=3):
#         self.wrapper = DuckDuckGoSearchAPIWrapper(max_results=max_results)

#     def search_duckduckgo(self, query):
#         results = self.wrapper.results(
#             query + " in English only with publish date",
#             max_results=self.wrapper.max_results,  
#         )
#         english_only = []
#         for r in results:
#             try:
#                 text = r.get("snippet") or r.get("body") or r.get("title", "")
#                 if detect(text) == "en":
#                     english_only.append(r)
#             except:
#                 continue
#         return english_only[:3]
 

#     def fetch_web_data(self, url,user_query):
#         try:
#             if str(url).startswith('https:'):
#                 res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#                 soup = bs4.BeautifulSoup(res.text, "lxml")
#                 text_content = soup.body.get_text(" ", strip=True) if soup.body else ""
#                 connection_status = create_chat_model()

#                 if not connection_status.get('status'):
#                     print('why here')
#                     return text_content[:5000]
#                 system_msg = SystemMessage(content="You are a helpful assistant specializing in news summarization.")
#                 human_msg = HumanMessage(content=summerize_data_for_query.format(user_query=user_query,data=text_content[:20000]))
#                 llm =connection_status['model']
#                 output=llm.invoke([system_msg, human_msg])
#                 return output.content
#             else:
#                 return  None
#         except Exception as e:
#             print('eeeeeeeeeeeeee',e)
#             return None
        
#     def get_all_data_about(self,query,have_data):
#         try:
#             output={}
#             response=self.search_duckduckgo(query)
#             for content in response:
#                 print(content)
#                 url=content['link']
#                 if url not in have_data:
#                     output[url]=[{'summary':self.fetch_url_text(url,query),'published_date':None}]
#                 else:
#                     continue
#             return output
#         except Exception as e:
#             print('get all data error ',e)
#             return output