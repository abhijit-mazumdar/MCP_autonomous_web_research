from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time
from sqlalchemy.orm import Session
from app.db.models import ResearchTaskORM, SessionLocal, init_db
from app.llm.ollama_client import OllamaClient

app = FastAPI()

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database on startup
@app.on_event("startup")
def on_startup():
    init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ResearchTask(BaseModel):
    id: int
    query: str
    status: str
    result: Optional[str] = None
    timestamp: datetime

@app.get("/")
def read_root():
    return {"message": "Welcome to the MCP Autonomous Web Research Agent Server!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/research", response_model=List[ResearchTask])
def get_research_tasks(db: Session = Depends(get_db)):
    tasks = db.query(ResearchTaskORM).all()
    return [ResearchTask(
        id=t.id,
        query=t.query,
        status=t.status,
        result=t.result,
        timestamp=t.timestamp
    ) for t in tasks]

class ResearchTaskRequest(BaseModel):
    query: str

def simulate_scraping(task: ResearchTask):
    # Simulate a delay for scraping
    time.sleep(2)
    task.status = "completed"
    task.result = f"Simulated research result for query: '{task.query}'"

ollama_client = OllamaClient()

def llm_generate_scraping_strategy(task_id: int, query: str):
    db = SessionLocal()
    try:
        task = db.query(ResearchTaskORM).filter(ResearchTaskORM.id == task_id).first()
        if not task:
            return
        prompt = f"Generate a robust web scraping strategy for the following research query: '{query}'. Include anti-detection techniques."
        result = ollama_client.generate(prompt, model="codellama")
        task.result = result or "LLM did not return a result."
        task.status = "completed"
        db.commit()
    finally:
        db.close()

@app.post("/research", response_model=ResearchTask)
def create_research_task(task_req: ResearchTaskRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task = ResearchTaskORM(
        query=task_req.query,
        status="pending",
        result=None
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    background_tasks.add_task(llm_generate_scraping_strategy, task.id, task.query)
    return ResearchTask(
        id=task.id,
        query=task.query,
        status=task.status,
        result=task.result,
        timestamp=task.timestamp
    )

class ResearchTaskUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[str] = None

@app.patch("/research/{task_id}", response_model=ResearchTask)
def update_research_task(
    update: ResearchTaskUpdate,
    task_id: int = Path(..., description="The ID of the research task to update."),
    db: Session = Depends(get_db)
):
    task = db.query(ResearchTaskORM).filter(ResearchTaskORM.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if update.status is not None:
        task.status = update.status
    if update.result is not None:
        task.result = update.result
    db.commit()
    db.refresh(task)
    return ResearchTask(
        id=task.id,
        query=task.query,
        status=task.status,
        result=task.result,
        timestamp=task.timestamp
    )

class ContentAnalysisRequest(BaseModel):
    content: str

class ContentAnalysisResponse(BaseModel):
    analysis: str

@app.post("/analyze", response_model=ContentAnalysisResponse)
def analyze_content(request: ContentAnalysisRequest = Body(...)):
    prompt = f"Analyze and summarize the following content for accuracy, relevance, and key points.\n\nContent:\n{request.content}"
    analysis = ollama_client.generate(prompt, model="llama3.2")
    return ContentAnalysisResponse(analysis=analysis or "LLM did not return a result.") 