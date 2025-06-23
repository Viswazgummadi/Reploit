# File: main.py
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import asyncio
import json
from fastapi.middleware.cors import CORSMiddleware

import config
from rate_limiter import check_and_increment_usage
from indexer import process_and_index_repo
from agent import AgenticAssistant
from langchain_google_genai import GoogleGenerativeAI

app = FastAPI(title="AI Code Assistant API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- UPDATED API MODELS ---
class IndexRequest(BaseModel):
    repo_url: str

class QueryRequest(BaseModel):
    question: str
    history: List[Dict] # Expects a list of {'role': '...', 'content': '...'}

# ... (get_llm_for_request and get_agent_for_request are the same) ...
def get_llm_for_request(request: Request) -> GoogleGenerativeAI:
    user_api_key = request.headers.get("X-User-API-Key")
    if user_api_key:
        return GoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=user_api_key)
    if check_and_increment_usage():
        return GoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=config.GOOGLE_API_KEY)
    raise HTTPException(status_code=429, detail="Daily free tier quota exceeded.")

def get_agent_for_request(request: Request) -> AgenticAssistant:
    user_api_key = request.headers.get("X-User-API-Key")
    if user_api_key:
        return AgenticAssistant(google_api_key=user_api_key)
    if check_and_increment_usage():
        return AgenticAssistant(google_api_key=config.GOOGLE_API_KEY)
    raise HTTPException(status_code=429, detail="Daily free tier quota exceeded.")

# ... (/ and /index endpoints are the same) ...
@app.get("/", summary="API Status")
def root():
    return {"status": "AI Code Assistant API is running."}

@app.post("/index", summary="Index a GitHub Repository")
def index_repo(request: IndexRequest, background_tasks: BackgroundTasks, llm: GoogleGenerativeAI = Depends(get_llm_for_request)):
    background_tasks.add_task(process_and_index_repo, request.repo_url, llm)
    return {"message": "Repository indexing started in the background."}

# --- UPDATED STREAMING QUERY ENDPOINT ---
# It is now a POST request to handle the chat history
@app.post("/query", summary="Query the indexed codebase with conversation history")
async def query_codebase(request: QueryRequest, assistant: AgenticAssistant = Depends(get_agent_for_request)):
    
    async def event_generator():
        async for event in assistant.query_stream(request.question, request.history):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")