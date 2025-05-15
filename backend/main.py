# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import aioredis
# import os
import json
import shutil
import uuid
from config import settings
# from pack.project_analyzer import ProjectAnalyzer
# import logging

# from pack.zip_handler import ZipFileHandler
import os
import asyncio
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pack.project_analyzer import ProjectAnalyzer
from pack.zip_handler import ZipFileHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Project Analyzer",
    description="API for analyzing code projects with AI insights",
    version="1.0.0"
)

# CORS configuration 
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Range"] 
)


redis = None

@app.on_event("startup")
async def startup_event():
    global redis
    try:
        redis = await aioredis.from_url(
            settings.REDIS_URL, 
            encoding="utf-8", 
            decode_responses=True,
            socket_timeout=settings.REDIS_TIMEOUT
        )
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        
        redis = {}

@app.on_event("shutdown")
async def shutdown_event():
    if redis and hasattr(redis, 'close'):
        await redis.close()

# @app.post("/analyze")
# async def analyze_project(file: UploadFile = File(...), prompt: Optional[str] = None):
#     """
#     Handle project upload and analysis with Redis caching.
#     """
#     global redis
#     try:
#         # [Previous implementation remains the same]
#         project_id = str(uuid.uuid4()) 
#         project_path = f"./tmp/{project_id}"
#         os.makedirs(project_path, exist_ok=True)

#         # Save and process file...
#         analyzer = ProjectAnalyzer(project_path)
#         results = await analyzer.analyze_project() 

#         # Caching with fallback
#         try:
#             if isinstance(redis, dict):  # Fallback in-memory storage
#                 redis[f"project:{project_id}"] = json.dumps(results)
#             else:
#                 await redis.set(f"project:{project_id}", json.dumps(results)) 
#         except Exception as cache_error:
#             logger.warning(f"Caching failed: {cache_error}")

#         # Cleanup temporary files
#         shutil.rmtree(project_path)  

#         return {
#             "project_id": project_id,
#             "results": results
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e)) 


@app.post("/analyze") #response_model=AnalysisResponse)
async def analyze_code(file: UploadFile = File(...)):
    """
    Analyze a ZIP file containing code.
    """
    logger.info(f"Received file: {file.filename}")
    
    # Input validation
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")
    
    try:
        # Create a temporary file to store the uploaded ZIP
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            # Write the uploaded file to the temporary file
            contents = await file.read()
            temp_zip.write(contents)
            temp_zip_path = temp_zip.name
            
        logger.info(f"Saved ZIP file to temporary location: {temp_zip_path}")
        
        # Process the ZIP file
        zip_handler = ZipFileHandler()
        project_dir = zip_handler.extract_zip(temp_zip_path)
        
        if not project_dir:
            raise HTTPException(status_code=500, detail="Failed to extract ZIP file")
        
        # Get file count for logging
        file_list = zip_handler.get_file_list()
        logger.info(f"Extracted {len(file_list)} files from ZIP")
        
        # Initialize and run the project analyzer
        analyzer = ProjectAnalyzer(project_dir)
        result = await analyzer.analyze_project()
        
        # Cleanup temporary files
        os.unlink(temp_zip_path)
        zip_handler.cleanup()
        
        return {"project_analysis": result}
    
    except Exception as e:
        logger.error(f"Error analyzing project: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error analyzing project: {str(e)}")

@app.get("/results/{project_id}")
async def get_results(project_id: str):
    """
    Retrieve cached analysis results from Redis with fallback.
    """
    global redis
    try:
        # Check if using fallback in-memory storage
        if isinstance(redis, dict):
            results = redis.get(f"project:{project_id}")
        else:
            results = await redis.get(f"project:{project_id}")
        
        if not results:
            raise HTTPException(status_code=404, detail="Results not found")
        return json.loads(results) 
    except Exception as e:
        logger.error(f"Error retrieving results: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 