import os
import json
import tempfile
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from agents.agent import Agent

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/scan")
async def scan(requirements: UploadFile = File(...)):
    if requirements.filename != "requirements.txt":
        raise HTTPException(
            status_code=400,
            detail="Only requirements.txt files are accepted."
        )

    temp_dir = tempfile.mkdtemp()

    try:
        req_path = os.path.join(temp_dir, "requirements.txt")
        with open(req_path, "wb") as f:
            content = await requirements.read()
            f.write(content)

        # Run the agent
        agent = Agent(project_path=temp_dir)
        logs = agent.run_agent()

        # Read the updated requirements.txt if the agent modified it
        updated_requirements = None
        if os.path.exists(req_path):
            with open(req_path, "r") as f:
                updated_requirements = f.read()

        # Read the audit report if the agent generated it
        report_path = os.path.join(temp_dir, "audit_report.json")
        audit_report = None
        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                audit_report = json.load(f)

        return JSONResponse(content={
            "status": "complete",
            "logs": logs,
            "updated_requirements": updated_requirements,
            "audit_report": audit_report,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)