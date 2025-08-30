"""
Agent Progress Tracker - Real-time agent interaction tracking
Provides WebSocket/SSE streaming of actual agent progress
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class AgentStatus(Enum):
    IDLE = "idle"
    STARTING = "starting"  
    ACTIVE = "active"
    COMPLETING = "completing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentProgress:
    agent_id: str
    agent_name: str
    status: AgentStatus
    message: str
    timestamp: str
    stage: str
    progress_percent: float = 0.0
    metadata: Optional[Dict] = None

class AgentProgressTracker:
    """Tracks and broadcasts real-time agent progress"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.progress_history: Dict[str, List[AgentProgress]] = {}
        
    def start_session(self, session_id: str) -> str:
        """Start tracking a new analysis session"""
        self.active_sessions[session_id] = {
            "started_at": datetime.utcnow().isoformat(),
            "status": "active",
            "current_agent": None,
            "stage": "initializing"
        }
        self.progress_history[session_id] = []
        return session_id
    
    def log_agent_progress(self, session_id: str, agent_id: str, agent_name: str, 
                          status: AgentStatus, message: str, stage: str, 
                          progress_percent: float = 0.0, metadata: Dict = None):
        """Log agent progress for a session"""
        
        progress = AgentProgress(
            agent_id=agent_id,
            agent_name=agent_name,
            status=status,
            message=message,
            timestamp=datetime.utcnow().isoformat(),
            stage=stage,
            progress_percent=progress_percent,
            metadata=metadata or {}
        )
        
        # Store in history
        if session_id not in self.progress_history:
            self.progress_history[session_id] = []
        
        self.progress_history[session_id].append(progress)
        
        # Update session state
        if session_id in self.active_sessions:
            self.active_sessions[session_id].update({
                "current_agent": agent_id,
                "stage": stage,
                "last_update": datetime.utcnow().isoformat()
            })
    
    def get_session_progress(self, session_id: str) -> List[Dict]:
        """Get all progress for a session"""
        if session_id not in self.progress_history:
            return []
        
        return [asdict(progress) for progress in self.progress_history[session_id]]
    
    def end_session(self, session_id: str, status: str = "completed"):
        """End tracking for a session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["status"] = status
            self.active_sessions[session_id]["ended_at"] = datetime.utcnow().isoformat()
    
    async def stream_progress(self, session_id: str) -> AsyncGenerator[str, None]:
        """Stream real-time progress updates via SSE"""
        
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connection', 'session_id': session_id, 'timestamp': datetime.utcnow().isoformat()})}\n\n"
        
        # Track last sent index to avoid duplicates
        last_sent_index = -1
        
        # Stream updates while session is active
        while session_id in self.active_sessions and self.active_sessions[session_id]["status"] == "active":
            # Get new progress updates
            current_progress = self.progress_history.get(session_id, [])
            
            # Send new updates
            for i, progress in enumerate(current_progress[last_sent_index + 1:], last_sent_index + 1):
                progress_data = asdict(progress)
                progress_data['type'] = 'agent_update'
                yield f"data: {json.dumps(progress_data)}\n\n"
                last_sent_index = i
            
            # Wait before checking for new updates
            await asyncio.sleep(0.5)
        
        # Send completion message
        yield f"data: {json.dumps({'type': 'session_complete', 'session_id': session_id, 'timestamp': datetime.utcnow().isoformat()})}\n\n"

# Global tracker instance
progress_tracker = AgentProgressTracker()


# Helper functions for easy integration with existing code
def start_analysis_tracking(session_id: str = None) -> str:
    """Start tracking an analysis session"""
    if not session_id:
        session_id = str(uuid.uuid4())
    return progress_tracker.start_session(session_id)

def log_agent_activity(session_id: str, agent_id: str, agent_name: str, 
                      message: str, stage: str, status: str = "active",
                      progress: float = 0.0, **kwargs):
    """Log agent activity - simplified interface"""
    
    status_enum = AgentStatus(status) if isinstance(status, str) else status
    progress_tracker.log_agent_progress(
        session_id=session_id,
        agent_id=agent_id,
        agent_name=agent_name,
        status=status_enum,
        message=message,
        stage=stage,
        progress_percent=progress,
        metadata=kwargs
    )

def complete_analysis_tracking(session_id: str):
    """Complete tracking for an analysis session"""
    progress_tracker.end_session(session_id, "completed")