from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import uvicorn
import logging
from code_reviewer import CodeReviewer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Code Review Agent", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class LocalReviewRequest(BaseModel):
    base_branch: str = "develop"
    config_path: Optional[str] = "config/review_standards.yaml"

class BitbucketReviewRequest(BaseModel):
    workspace: Optional[str] = None
    repo: Optional[str] = None
    pr_id: str
    config_path: Optional[str] = "config/review_standards.yaml"

class ReviewResponse(BaseModel):
    status: str
    message: str
    reviews: Optional[List[Dict]] = None

# Global reviewer instance
reviewer = None

@app.on_event("startup")
async def startup_event():
    global reviewer
    try:
        reviewer = CodeReviewer()
        logger.info("Code reviewer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize code reviewer: {e}")

@app.get("/")
async def root():
    return FileResponse('static/index.html')

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Code Review Agent"}

@app.post("/review/local", response_model=ReviewResponse)
async def review_local(request: LocalReviewRequest, background_tasks: BackgroundTasks):
    """Review local code changes without posting to Bitbucket."""
    try:
        if not reviewer:
            raise HTTPException(status_code=500, detail="Code reviewer not initialized")
        
        reviews = reviewer.review_local_changes(request.base_branch)
        
        return ReviewResponse(
            status="success",
            message=f"Reviewed {len(reviews)} files",
            reviews=reviews
        )
    except Exception as e:
        logger.error(f"Local review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/review/bitbucket", response_model=ReviewResponse)
async def review_bitbucket(request: BitbucketReviewRequest):
    """Review Bitbucket pull request and add comments."""
    try:
        if not reviewer:
            raise HTTPException(status_code=500, detail="Code reviewer not initialized")
        
        # Use environment variables as defaults, request params as overrides
        workspace = request.workspace or os.getenv('BITBUCKET_WORKSPACE')
        repo = request.repo or os.getenv('BITBUCKET_REPO')
        
        if not workspace:
            raise HTTPException(status_code=400, detail="workspace required (provide in request or set BITBUCKET_WORKSPACE env var)")
        if not repo:
            raise HTTPException(status_code=400, detail="repo required (provide in request or set BITBUCKET_REPO env var)")
        
        reviews = reviewer.review_pull_request(
            workspace, 
            repo, 
            request.pr_id
        )
        
        critical_major_count = len([r for r in reviews if r.get('severity') in ['critical', 'major']])
        
        return ReviewResponse(
            status="success",
            message=f"Reviewed {len(reviews)} files, added {critical_major_count} comments to PR",
            reviews=reviews
        )
    except Exception as e:
        logger.error(f"Bitbucket review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/standards")
async def get_review_standards():
    """Get current review standards configuration."""
    try:
        if not reviewer:
            raise HTTPException(status_code=500, detail="Code reviewer not initialized")
        
        return reviewer.standards
    except Exception as e:
        logger.error(f"Failed to get standards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api")
async def api_info():
    return {
        "message": "AI Code Review Agent API",
        "endpoints": {
            "health": "/health",
            "local_review": "/review/local",
            "bitbucket_review": "/review/bitbucket",
            "standards": "/config/standards",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
