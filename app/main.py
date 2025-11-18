from fastapi import FastAPI
from fastapi import Depends

from fastapi import FastAPI, Depends
from redis_client import redis_client
from auth.auth_routes import router as auth_router
from auth.session.session_manager import SessionManager
from auth.session.session_api import router as session_router
from auth.auth_routes import get_current_user
from auth.database import Base, engine

from api import relevant_queries
from api import search_duckduckgo
from api import web_data_fetcher
from api import summarize_news_data
from api import store_data_in_vector_db
from api import search_data_in_vector_db
from api import analysis_search_result
from api import verifier_search_result


# from fastapi import FastAPI, Depends
# from redis_client import redis_client

# from fastapi import FastAPI, Depends
# from redis_client import redis_client
# from auth.auth_routes import router as auth_router
# from auth.session.session_manager import SessionManager
# from auth.session.session_api import router as session_router
# from auth.auth_routes import get_current_user
# from auth.database import Base, engine

# from api import relevant_queries
# from api import search_duckduckgo
# from api import web_data_fetcher
# from api import summarize_news_data
# from api import store_data_in_vector_db
# from api import search_data_in_vector_db
# from api import analysis_search_result


# app = FastAPI()

app = FastAPI(
    title="Deep Research API",
    description="Competitor Analysis Project",
    version="1.0.0"
)
Base.metadata.create_all(bind=engine)
# # Apply authentication globally
# app_dependency = Depends(get_current_user)
 
# EXCEPTIONS: Remove protection for these
unprotected_routes = [
    "/auth/login",
    "/auth/register"
]


@app.get("/redis-test")
def redis_test():
    redis_client.set("framework", "fastapi")
    value = redis_client.get("framework")
    return {"redis_value": value}

app.include_router(session_router,prefix="/session",tags=['Session'])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(relevant_queries.router, prefix="/api", tags=["Relevant Queries"])
app.include_router(search_duckduckgo.router, prefix="/api", tags=["Search News"])
app.include_router(web_data_fetcher.router, prefix="/api", tags=["Fetch data from web"])
app.include_router(store_data_in_vector_db.router, prefix="/api", tags=["Store data In DB "])
app.include_router(search_data_in_vector_db.router, prefix="/api", tags=["search data In DB "])
app.include_router(summarize_news_data.router, prefix="/api", tags=["Summarize News Data "])
app.include_router(analysis_search_result.router, prefix="/api", tags=["Analysis content "])
app.include_router(verifier_search_result.router, prefix="/api", tags=["Verifier content "])


