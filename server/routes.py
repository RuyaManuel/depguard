import os
import tempfile
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from agents.agent import Agent
router = APIRouter()


@router.post("/scan")
async def scan(requirements: UploadFile = File(...)):
    # Validate the uploaded file
    if requirements.filename != "requirements.txt":
        raise HTTPException(
            status_code=400,
            detail="Only requirements.txt files are accepted."
        )

    # Save uploaded requirements.txt to a temp directory
    # so check_vulnerability() has a real project_path to work with
    temp_dir = tempfile.mkdtemp()

    try:
        req_path = os.path.join(temp_dir, "requirements.txt")
        with open(req_path, "wb") as f:
            content = await requirements.read()
            f.write(content)

        # Boot the agent — it returns the full log list
        agent = Agent(project_path=temp_dir)
        logs = agent.run_agent()

        return JSONResponse(content={
            "status": "complete",
            "logs": logs
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Always clean up temp directory when done
        shutil.rmtree(temp_dir, ignore_errors=True)