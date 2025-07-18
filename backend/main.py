# Backend main application
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import asyncio
from typing import Dict, Any, Optional
import time
from pathlib import Path
import tempfile
import os

# Import our modules
from pdf_processor import PDFProcessor
from research_service import ResearchService

app = FastAPI(title="Data Engineer API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
pdf_processor = PDFProcessor()
research_service = ResearchService()

# Job storage (in production, use Redis or database)
jobs: Dict[str, Dict[str, Any]] = {}

class ResearchRequest(BaseModel):
    topic: str
    max_pdfs: int = 5

@app.get("/")
async def root():
    return {"message": "Data Engineer API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/research/start")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start automated PDF research for a topic"""
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "status": "starting",
        "progress": 0,
        "message": "Initializing research...",
        "topic": request.topic,
        "max_pdfs": request.max_pdfs,
        "found_pdfs": [],
        "results": None,
        "error": None,
        "created_at": time.time()
    }
    
    # Start background research
    background_tasks.add_task(run_automated_research, job_id, request.topic, request.max_pdfs)
    
    return {"job_id": job_id, "status": "started"}

@app.get("/research/status/{job_id}")
async def get_research_status(job_id: str):
    """Get the status of a research job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.post("/pdf/upload")
async def upload_pdf(background_tasks: BackgroundTasks, pdf_file: UploadFile = File(...)):
    """Upload and process a single PDF file"""
    if not pdf_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    temp_dir = Path(tempfile.gettempdir())
    pdf_path = temp_dir / f"upload_{job_id}.pdf"
    
    try:
        with open(pdf_path, "wb") as buffer:
            content = await pdf_file.read()
            buffer.write(content)
        
        # Initialize job
        jobs[job_id] = {
            "status": "processing",
            "progress": 20,
            "message": "Processing uploaded PDF...",
            "pdf_path": str(pdf_path),
            "results": None,
            "error": None,
            "created_at": time.time()
        }
        
        # Start background processing
        background_tasks.add_task(process_single_pdf, job_id, str(pdf_path))
        
        return {"job_id": job_id, "status": "processing"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/pdf/status/{job_id}")
async def get_pdf_status(job_id: str):
    """Get the status of a PDF processing job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

async def run_automated_research(job_id: str, topic: str, max_pdfs: int):
    """Background task for automated research"""
    try:
        jobs[job_id]["status"] = "searching"
        jobs[job_id]["progress"] = 10
        jobs[job_id]["message"] = "Searching for relevant PDFs..."
        
        # Search for PDFs
        found_pdfs = await research_service.find_pdfs(topic, max_pdfs)
        
        if not found_pdfs:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "No relevant PDFs found"
            return
        
        jobs[job_id]["found_pdfs"] = found_pdfs
        jobs[job_id]["progress"] = 30
        jobs[job_id]["message"] = f"Found {len(found_pdfs)} PDFs, downloading and processing..."
        
        # Download and process PDFs
        all_tables = []
        total_pdfs = len(found_pdfs)
        
        for i, pdf_info in enumerate(found_pdfs):
            try:
                progress = 30 + (i / total_pdfs) * 60
                jobs[job_id]["progress"] = progress
                jobs[job_id]["message"] = f"Processing PDF {i+1}/{total_pdfs}: {pdf_info.get('title', 'Unknown')}"
                
                # Download PDF
                pdf_path = await research_service.download_pdf(pdf_info["url"], job_id, i)
                
                if pdf_path:
                    # Process PDF
                    async def progress_callback(pct):
                        final_progress = progress + (pct / 100) * (60 / total_pdfs)
                        jobs[job_id]["progress"] = final_progress
                    
                    result = await pdf_processor.process_pdf(pdf_path, f"{job_id}_{i}", progress_callback)
                    
                    if result["success"]:
                        # Add source info to tables
                        for table in result["tables"]:
                            table["source_pdf"] = pdf_info.get("title", "Unknown")
                            table["source_url"] = pdf_info["url"]
                        
                        all_tables.extend(result["tables"])
                
            except Exception as e:
                print(f"Error processing PDF {i}: {e}")
                continue
        
        # Complete research
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Research completed successfully!"
        jobs[job_id]["results"] = {
            "tables": all_tables,
            "table_count": len(all_tables),
            "processed_pdfs": len(found_pdfs),
            "topic": topic
        }
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["progress"] = 0
        jobs[job_id]["message"] = f"Research failed: {str(e)}"

async def process_single_pdf(job_id: str, pdf_path: str):
    """Background task for single PDF processing"""
    try:
        async def progress_callback(pct):
            jobs[job_id]["progress"] = 20 + (pct * 0.8)  # Scale to 20-100%
            if pct < 100:
                jobs[job_id]["message"] = f"Processing PDF... {int(pct)}%"
        
        result = await pdf_processor.process_pdf(pdf_path, job_id, progress_callback)
        
        if result["success"]:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["message"] = "PDF processing completed!"
            jobs[job_id]["tables"] = result["tables"]
            jobs[job_id]["table_count"] = result["table_count"]
            jobs[job_id]["processing_time"] = result["processing_time"]
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = result["error"]
            jobs[job_id]["progress"] = 0
            jobs[job_id]["message"] = f"Processing failed: {result['error']}"
            
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["progress"] = 0
        jobs[job_id]["message"] = f"Processing failed: {str(e)}"
    finally:
        # Cleanup uploaded file
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 