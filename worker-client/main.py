# worker-client/main.py
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from registrar import register, unregister
from executor import execute_embedding
from shared.schemas import ChunkPayload, ChunkResult
import httpx, config

@asynccontextmanager
async def lifespan(app: FastAPI):
    await register()   # POST to orchestrator on startup
    yield
    await unregister() # cleanup on shutdown

app = FastAPI(lifespan=lifespan)

@app.post("/jobs/incoming")
async def receive_job(job: ChunkPayload, bg: BackgroundTasks):
    bg.add_task(process_job, job)
    return {"status": "accepted"}  # 200 immediately

async def process_job(job: ChunkPayload):
    embeddings, cpu_seconds = execute_embedding(job.texts)
    result = ChunkResult(
        chunk_id=job.chunk_id,
        worker_id=config.WORKER_ID,
        embeddings=embeddings,
        cpu_seconds=cpu_seconds,
        status="success"
    )
    async with httpx.AsyncClient() as client:
        await client.post(job.callback_url, json=result.dict())
    await re_register_available()