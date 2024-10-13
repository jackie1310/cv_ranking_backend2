from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from src.candidate.routers import router as candidate_router
from src.job.routers import router as job_router
from src.matching.routers import router as matching_router

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Message": "Welcome to Cybersoft"}

@app.get("/healthz")
async def healthcheck() -> bool:
    return True

app.include_router(candidate_router, prefix="/candidate", tags=["Candidate"])
app.include_router(job_router, prefix="/job", tags=["Job"])
app.include_router(matching_router, prefix="/matching", tags=["Matching"])