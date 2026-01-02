from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import databases, jobs, tools
import os

app = FastAPI(
    title="Sequence Alignment Service",
    description="A web service for BLAST and Minimap2 alignments",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data directories exist
DATA_DIR = "/data"
for d in ["references", "results", "uploads"]:
    os.makedirs(os.path.join(DATA_DIR, d), exist_ok=True)

# Include routers
app.include_router(databases.router)
app.include_router(jobs.router)
app.include_router(tools.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Sequence Alignment Service API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
