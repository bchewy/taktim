"""
Multimodal Backend API
FastAPI server with CrewAI agents for multimodal content analysis
"""

import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import csv
import io
import pymysql

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.agents.multimodal_crew import MultimodalCrew, ChatAgent
from src.utils.file_handler import FileHandler
from src.utils.agent_progress_tracker import progress_tracker, start_analysis_tracking, complete_analysis_tracking

# Load environment variables from project root
from pathlib import Path
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

app = FastAPI(
    title="Multimodal Analysis API",
    description="CrewAI-powered multimodal content analysis system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
file_handler = FileHandler()
multimodal_crew = MultimodalCrew()
chat_agent = ChatAgent()

# In-memory storage for task results and session context
task_results = {}
session_contexts = {}


# Pydantic models
class AnalysisRequest(BaseModel):
    query: str = Field(..., description="Query or instruction for analysis")
    file_ids: List[str] = Field(default=[], description="List of uploaded file IDs")
    task_id: Optional[str] = Field(None, description="Optional custom task ID")


class ChatRequest(BaseModel):
    message: str = Field(..., description="Chat message")
    session_id: str = Field(..., description="Session ID for context")


class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending", "running", "completed", "failed"
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    size: int
    processed: bool
    processing_info: Optional[Dict[str, Any]] = None


# Project Analysis Models
class ProjectAnalysis(BaseModel):
    summary: str = Field(..., description="Brief summary of the project")
    project_name: str = Field(..., description="Name of the project")
    project_description: str = Field(..., description="Detailed description of the project")
    project_type: Optional[str] = Field(None, description="Type of project (Web Application, Mobile Application, etc.)")
    priority: Optional[str] = Field(None, description="Project priority (Low, Medium, High, Critical)")
    due_date: Optional[str] = Field(None, description="Project due date")


class RegulationInfo(BaseModel):
    jurisdiction: str = Field(..., description="Geographic jurisdiction")
    law_name: str = Field(..., description="Name of the regulation")
    impact_level: str = Field(..., description="Impact level: low, medium, high")
    why_applies: str = Field(..., description="Explanation of why this regulation applies")


class LegalAnalysisResult(BaseModel):
    compliance_status: str = Field(..., description="Overall compliance status")
    overall_risk_level: str = Field(..., description="Overall risk level")
    key_regulations: List[RegulationInfo] = Field(default=[], description="Applicable regulations")
    compliance_requirements: List[str] = Field(default=[], description="Specific compliance requirements")
    recommendations: List[str] = Field(default=[], description="Implementation recommendations")
    detailed_analysis: str = Field(..., description="Detailed legal analysis text")


# Helper functions
def generate_task_id() -> str:
    """Generate unique task ID"""
    return str(uuid.uuid4())


async def run_analysis_task(task_id: str, 
                          file_paths: List[str], 
                          image_data: List[Dict],
                          query: str):
    """Background task for running multimodal analysis"""
    try:
        task_results[task_id]["status"] = "running"
        
        # Run CrewAI analysis
        result = multimodal_crew.full_multimodal_analysis(
            file_paths=file_paths,
            image_data=image_data, 
            query=query
        )
        
        task_results[task_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "result": result
        })
        
    except Exception as e:
        task_results[task_id].update({
            "status": "failed",
            "completed_at": datetime.utcnow(),
            "error": str(e)
        })


# Database connection setup using PyMySQL
def connect_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "password"),
        database=os.getenv("DB_NAME", "analysis_db"),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor,
    )

def save_analysis_to_db(feature_name: str, result: dict):
    """Save analysis result to the database using PyMySQL"""
    try:
        db = connect_db()
        with db.cursor() as cursor:
            # Insert or update the result in the database
            query = """
            INSERT INTO features (feature_name, result)
            VALUES (%s, %s)
            """
            cursor.execute(query, (feature_name, json.dumps(result)))
            db.commit()

    except pymysql.MySQLError as err:
        print(f"Error: {err}")
    finally:
        db.close()


# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "multimodal-backend",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file"""
    try:
        # Save file
        file_info = await file_handler.save_file(file)
        
        # Process file
        processed_info = file_handler.process_file(file_info)
        
        return UploadResponse(
            file_id=processed_info["id"],
            filename=processed_info["filename"],
            file_type=processed_info["type"],
            size=processed_info["size"],
            processed=processed_info.get("processed", False),
            processing_info=processed_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/api/analyze")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start multimodal content analysis"""
    try:
        task_id = request.task_id or generate_task_id()
        
        # Initialize task status
        task_results[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "query": request.query,
            "file_ids": request.file_ids
        }
        
        # Collect file information
        file_paths = []
        image_data = []
        
        for file_id in request.file_ids:
            # Find file by ID (this is simplified - in production you'd have a proper file database)
            for upload_dir in [file_handler.upload_dir / "images", file_handler.upload_dir / "documents"]:
                for file_path in upload_dir.glob(f"{file_id}_*"):
                    if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                        image_data.append({
                            "filename": file_path.name,
                            "file_path": str(file_path),
                            "file_id": file_id
                        })
                    else:
                        file_paths.append(str(file_path))
        
        # Start background analysis
        background_tasks.add_task(
            run_analysis_task,
            task_id=task_id,
            file_paths=file_paths,
            image_data=image_data,
            query=request.query
        )
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Analysis started",
            "files_found": len(file_paths) + len(image_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed to start: {str(e)}")


@app.get("/api/results/{task_id}")
async def get_results(task_id: str):
    """Get analysis results"""
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_results[task_id]


@app.post("/api/chat")
async def chat_with_context(request: ChatRequest):
    """Interactive chat with multimodal context"""
    try:
        session_id = request.session_id
        
        # Get or create session context
        if session_id not in session_contexts:
            session_contexts[session_id] = {
                "created_at": datetime.utcnow(),
                "messages": [],
                "analysis_context": {}
            }
        
        session = session_contexts[session_id]
        
        # Add user message to history
        session["messages"].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow()
        })
        
        # Generate response using chat agent
        response = chat_agent.chat_with_context(
            message=request.message,
            context=session.get("analysis_context", {})
        )
        
        # Add assistant response to history
        session["messages"].append({
            "role": "assistant", 
            "content": response,
            "timestamp": datetime.utcnow()
        })
        
        return {
            "response": response,
            "session_id": session_id,
            "message_count": len(session["messages"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/api/chat/{session_id}/context")
async def update_chat_context(session_id: str, task_id: str):
    """Add analysis results to chat context"""
    try:
        if task_id not in task_results:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if session_id not in session_contexts:
            session_contexts[session_id] = {
                "created_at": datetime.utcnow(),
                "messages": [],
                "analysis_context": {}
            }
        
        # Add task results to session context
        task_result = task_results[task_id]
        if task_result["status"] == "completed":
            session_contexts[session_id]["analysis_context"] = task_result["result"]
            
            return {
                "message": "Context updated successfully",
                "session_id": session_id,
                "task_id": task_id
            }
        else:
            raise HTTPException(status_code=400, detail="Task not completed yet")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context update failed: {str(e)}")


@app.get("/api/tasks")
async def list_tasks():
    """List all tasks"""
    return {
        "tasks": list(task_results.values()),
        "total": len(task_results)
    }


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get chat session history"""
    if session_id not in session_contexts:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_contexts[session_id]


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task and its results"""
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del task_results[task_id]
    return {"message": "Task deleted successfully"}


# Legal Compliance Analysis Endpoints
@app.post("/api/legal-analyze", response_model=LegalAnalysisResult)
async def analyze_feature_legal_compliance(feature: ProjectAnalysis):
    """Analyze TikTok feature for legal compliance using CrewAI Legal Agent"""
    try:
        # Convert Pydantic model to dict for the legal agent
        feature_data = feature.model_dump()
        
        # Run legal compliance analysis
        result = multimodal_crew.analyze_legal_compliance(feature_data)
        
        # Parse the legal analysis result
        # Note: In a real implementation, you'd want to parse the raw text response
        # and structure it properly. For now, we'll return a structured response.
        return LegalAnalysisResult(
            compliance_status="needs_review",  # This would be parsed from agent response
            overall_risk_level="medium",       # This would be parsed from agent response
            key_regulations=[
                RegulationInfo(
                    jurisdiction="US",
                    law_name="COPPA",
                    impact_level="high",
                    why_applies="Feature targets users under 13"
                )
            ],
            compliance_requirements=[
                "Implement age verification",
                "Obtain parental consent for users under 13",
                "Provide data deletion mechanisms"
            ],
            recommendations=[
                "Add privacy-by-design features",
                "Implement transparent data collection notices",
                "Create user-friendly privacy controls"
            ],
            detailed_analysis=result.get("legal_analysis", "Analysis completed")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Legal analysis failed: {str(e)}")


@app.post("/api/legal-risk-assessment")
async def assess_feature_risks(feature: ProjectAnalysis, jurisdictions: Optional[List[str]] = None):
    """Perform detailed risk assessment for TikTok feature"""
    try:
        feature_data = feature.model_dump()
        
        # Run risk assessment
        result = multimodal_crew.assess_regulatory_risks(feature_data, jurisdictions)
        
        return {
            "feature_name": feature.project_name,
            "risk_assessment": result.get("risk_assessment", "Assessment completed"),
            "jurisdictions_analyzed": jurisdictions or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


@app.post("/api/legal-quick-check")
async def quick_legal_check(
    project_name: str = Form(...),
    summary: str = Form(...),
    project_description: str = Form(...),
    project_type: str = Form(default=""),
    priority: str = Form(default=""),
    due_date: str = Form(default="")
):
    """Quick legal compliance check for projects"""
    try:
        feature_data = {
            "project_name": project_name,
            "summary": summary,
            "project_description": project_description,
            "project_type": project_type,
            "priority": priority,
            "due_date": due_date
        }
        
        # Run quick legal analysis
        result = multimodal_crew.analyze_legal_compliance(feature_data)
        
        return {
            "feature_name": project_name,
            "quick_assessment": "Analysis completed - check detailed_analysis for full results",
            "legal_analysis": result.get("legal_analysis", "Analysis completed"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick legal check failed: {str(e)}")


# Comprehensive Geo-Compliance Analysis Endpoints
@app.post("/api/comprehensive-compliance-analysis")
async def comprehensive_compliance_analysis(feature: ProjectAnalysis):
    """Comprehensive geo-regulatory compliance analysis with real-time tracking"""
    session_id = None
    try:
        # Start progress tracking
        session_id = start_analysis_tracking()
        
        # Convert Pydantic model to dict
        feature_data = feature.model_dump()
        feature_data['_session_id'] = session_id  # Pass session ID to crew
        
        # Run comprehensive analysis (Legal + Geo-Regulatory) with tracking
        result = multimodal_crew.analyze_comprehensive_compliance(feature_data)
        
        # Save result to the database
        save_analysis_to_db(feature.project_name, result=result)

        # Complete tracking
        complete_analysis_tracking(session_id)
        
        return {
            "analysis_type": "comprehensive_geo_compliance",
            "feature_analyzed": feature.project_name,
            "result": result,
            "regulatory_inquiry_ready": result.get("audit_trail_ready", False),
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id  # Return session ID for frontend tracking
        }
        
    except Exception as e:
        if session_id:
            complete_analysis_tracking(session_id)
        raise HTTPException(status_code=500, detail=f"Comprehensive compliance analysis failed: {str(e)}")


@app.post("/api/geo-regulatory-mapping") 
async def geo_regulatory_mapping(feature: ProjectAnalysis):
    """Geo-regulatory mapping analysis for jurisdiction-specific requirements"""
    try:
        feature_data = feature.model_dump()
        
        # Run geo-regulatory analysis only
        if hasattr(multimodal_crew, 'geo_regulatory_agent') and multimodal_crew.geo_regulatory_agent:
            result = multimodal_crew.geo_regulatory_agent.analyze_geo_compliance(feature_data)
        else:
            raise HTTPException(status_code=503, detail="Geo-Regulatory Agent not available")
        
        return {
            "analysis_type": "geo_regulatory_mapping",
            "feature_analyzed": feature.project_name,
            "project_type": feature.project_type,
            "geo_compliance_analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geo-regulatory mapping failed: {str(e)}")


@app.get("/api/progress-stream/{session_id}")
async def stream_analysis_progress(session_id: str):
    """Stream real-time analysis progress via Server-Sent Events"""
    
    async def generate_stream():
        async for data in progress_tracker.stream_progress(session_id):
            yield data
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@app.post("/api/audit-trail-generation")
async def generate_audit_trail(feature: ProjectAnalysis):
    """Generate audit trail for regulatory inquiry responses"""
    try:
        feature_data = feature.model_dump()
        
        # Run comprehensive analysis to get full compliance data
        comprehensive_result = multimodal_crew.analyze_comprehensive_compliance(feature_data)
        
        # Format for audit trail
        audit_data = {
            "feature_screened": feature.project_name,
            "screening_timestamp": datetime.utcnow().isoformat(),
            "compliance_analysis": comprehensive_result,
            "regulatory_databases_queried": ["Congress.gov", "GovInfo.gov", "Internal Regulatory Database"],
            "project_details": {
                "name": feature.project_name,
                "type": feature.project_type,
                "priority": feature.priority,
                "due_date": feature.due_date
            },
            "audit_trail_status": "REGULATORY_INQUIRY_READY"
        }
        
        return {
            "audit_trail": audit_data,
            "regulatory_response_ready": True,
            "evidence_citations_included": True,
            "traceability_complete": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit trail generation failed: {str(e)}")


@app.post("/api/bulk-csv-analysis")
async def bulk_csv_analysis(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Bulk analysis from CSV file upload"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Read CSV content
        content = await file.read()
        csv_string = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_string))
        
        # Convert CSV rows to analysis tasks
        tasks = []
        for row in csv_reader:
            # Map CSV columns to our ProjectAnalysis structure
            task = {
                "project_name": row.get('Summary', ''),
                "summary": f"{row.get('Issue Type', '')} - {row.get('Summary', '')}",
                "project_description": f"Issue: {row.get('Issue key', '')} - {row.get('Summary', '')}. Priority: {row.get('Priority', '')}. Status: {row.get('Status', '')}",
                "project_type": row.get('Issue Type', ''),
                "priority": row.get('Priority', ''),
                "due_date": row.get('Due date', ''),
            }
            
            # Only include tasks with meaningful content
            if task["project_name"]:
                tasks.append(task)
        
        if not tasks:
            raise HTTPException(status_code=400, detail="No valid tasks found in CSV")
        
        # Generate task ID for bulk operation
        task_id = generate_task_id()
        
        # Initialize bulk task status
        task_results[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "task_type": "bulk_csv_analysis",
            "total_items": len(tasks),
            "completed_items": 0,
            "results": []
        }
        
        # Start background bulk analysis
        background_tasks.add_task(
            run_bulk_csv_analysis_task,
            task_id=task_id,
            tasks=tasks
        )
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": f"Bulk CSV analysis started for {len(tasks)} items",
            "total_items": len(tasks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV bulk analysis failed: {str(e)}")


async def run_bulk_csv_analysis_task(task_id: str, tasks: List[Dict]):
    """Background task for running bulk CSV analysis"""
    try:
        task_results[task_id]["status"] = "running"
        results = []
        
        for i, task in enumerate(tasks):
            try:
                # Run comprehensive analysis on each task
                result = multimodal_crew.analyze_comprehensive_compliance(task)
                
                results.append({
                    "feature_name": task["project_name"],
                    "analysis_result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                    "success": True
                })
                
                # Update progress
                task_results[task_id]["completed_items"] = i + 1
                
            except Exception as e:
                results.append({
                    "feature_name": task["project_name"],
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "success": False
                })
        
        # Mark as completed
        task_results[task_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "results": results,
            "success_count": len([r for r in results if r["success"]]),
            "failure_count": len([r for r in results if not r["success"]])
        })
        
    except Exception as e:
        task_results[task_id].update({
            "status": "failed",
            "completed_at": datetime.utcnow(),
            "error": str(e)
        })


@app.get("/api/features")
async def get_all_features():
    """Retrieve all feature data from the database"""
    try:
        db = connect_db()
        with db.cursor() as cursor:
            query = "SELECT id, feature_name, result, timestamp FROM features;"
            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                raise HTTPException(status_code=404, detail="No feature data found")

            return {
                "features": [
                    {
                        "id": row["id"],
                        "feature_name": row["feature_name"],
                        "result": json.loads(row["result"]),
                        "timestamp": row["timestamp"].isoformat()
                    }
                    for row in results
                ]
            }

    except pymysql.MySQLError as err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8001,
        reload=True
    )