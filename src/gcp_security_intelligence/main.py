#!/usr/bin/env python
import sys
import warnings
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from gcp_security_intelligence.crew import GcpSecurityIntelligence

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


class ScanRequest(BaseModel):
    """Incoming request body for a scheduled or manual crew run."""
    project_id: str


class ScanResponse(BaseModel):
    """Response returned after a crew run completes."""
    status: str
    project_id: str
    report_file: str
    completed_at: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Configure logging on startup."""
    logging.basicConfig(level=logging.INFO)
    yield


app = FastAPI(title="GCP Security Intelligence", lifespan=lifespan)


@app.get("/healthz")
async def healthz():
    """Health check endpoint for Cloud Run."""
    return {"status": "ok"}


@app.post("/run", response_model=ScanResponse)
async def run_scan(request: ScanRequest):
    """Trigger a full security intelligence crew run for the given project."""
    try:
        GcpSecurityIntelligence().crew().kickoff(
            inputs={"project_id": request.project_id}
        )
        return ScanResponse(
            status="completed",
            project_id=request.project_id,
            report_file="report.md",
            completed_at=datetime.utcnow().isoformat() + "Z",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler so unhandled errors return JSON instead of a 500 HTML page."""
    return JSONResponse(status_code=500, content={"detail": str(exc)})


def run():
    """CLI entrypoint used by crewai run."""
    inputs = {"project_id": "scc-security-intelligence"}
    try:
        GcpSecurityIntelligence().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """Train the crew for a given number of iterations."""
    inputs = {"project_id": "scc-security-intelligence"}
    try:
        GcpSecurityIntelligence().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """Replay the crew execution from a specific task."""
    try:
        GcpSecurityIntelligence().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """Test the crew execution and return results."""
    inputs = {"project_id": "scc-security-intelligence"}
    try:
        GcpSecurityIntelligence().crew().test(
            n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
