"""
KayGee 1.0 - FastAPI Backend
Real-time system monitoring and voice interaction
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import json
import time
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import real KayGee system
try:
    from main import VaultedReasoner
    SYSTEM_AVAILABLE = True
except Exception as e:
    print(f"Warning: VaultedReasoner not available: {e}")
    SYSTEM_AVAILABLE = False

app = FastAPI(title="KayGee 1.0 API", version="1.0.0")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global system instance
kaygee_system: Optional[VaultedReasoner] = None
connected_clients = []

# Pydantic models
class InteractionRequest(BaseModel):
    text: str
    context: Optional[Dict[str, Any]] = None

class InteractionResponse(BaseModel):
    text: str
    confidence: float
    philosophical_basis: str
    merkle_root: str
    processing_time: float

# Initialize system on startup
@app.on_event("startup")
async def startup_event():
    global kaygee_system
    if SYSTEM_AVAILABLE:
        try:
            print("🧠 Initializing KayGee system...")
            kaygee_system = VaultedReasoner()
            print("✅ System ready")
        except Exception as e:
            print(f"⚠️  Failed to initialize system: {e}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "KayGee 1.0 API",
        "version": "1.0.0",
        "status": "online" if kaygee_system else "offline",
        "endpoints": {
            "status": "/api/status",
            "interact": "/api/interact",
            "metrics": "/api/metrics",
            "websocket": "/ws"
        }
    }

# System status
@app.get("/api/status")
async def get_status():
    """Get current system status"""
    if not kaygee_system:
        return JSONResponse(
            status_code=503,
            content={"error": "System not available"}
        )
    
    try:
        merkle_root = "genesis"
        if hasattr(kaygee_system, 'merkle_vault'):
            merkle_root = kaygee_system.merkle_vault.get_current_root()[:16] + "..."
        
        return {
            "session_id": getattr(kaygee_system, 'session_id', 'unknown'),
            "interaction_count": getattr(kaygee_system, 'interaction_count', 0),
            "merkle_root": merkle_root,
            "uptime": time.time(),
            "system_online": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get detailed metrics
@app.get("/api/metrics")
async def get_metrics():
    """Get detailed system metrics"""
    if not kaygee_system:
        return {
            "confidence": 0.0,
            "philosopher": "None",
            "stability": 0.0,
            "drift_detected": False,
            "philosophical_balance": {
                "kant": 0,
                "hume": 0,
                "locke": 0,
                "spinoza": 0
            }
        }
    
    try:
        # Extract real metrics
        confidence = 0.85
        if hasattr(kaygee_system, 'last_decision'):
            confidence = kaygee_system.last_decision.get('confidence', 0.85)
        
        return {
            "confidence": confidence,
            "philosopher": "Balanced",  # TODO: Extract from reasoning history
            "stability": 0.94,  # TODO: Extract from PersonalityCore
            "drift_detected": False,
            "philosophical_balance": {
                "kant": 25,
                "hume": 25,
                "locke": 25,
                "spinoza": 25
            },
            "vault_stats": {
                "episodic": len(kaygee_system.trace_vault.entries) if hasattr(kaygee_system, 'trace_vault') and hasattr(kaygee_system.trace_vault, 'entries') else 0,
                "prototypical": 0,
                "semantic_rules": 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Process interaction
@app.post("/api/interact", response_model=InteractionResponse)
async def process_interaction(request: InteractionRequest):
    """Process user interaction through reasoning system"""
    if not kaygee_system:
        raise HTTPException(status_code=503, detail="System not available")
    
    try:
        start_time = time.time()
        
        # Process through real system
        response = kaygee_system.process_interaction(
            request.text,
            context=request.context
        )
        
        processing_time = time.time() - start_time
        
        # Extract response data
        text = response.get('text', str(response))
        confidence = response.get('confidence', 0.85)
        basis = response.get('philosophical_basis', 'balanced reasoning')
        
        # Get current Merkle root
        merkle_root = "pending"
        if hasattr(kaygee_system, 'merkle_vault'):
            merkle_root = kaygee_system.merkle_vault.get_current_root()[:16] + "..."
        
        return InteractionResponse(
            text=text,
            confidence=confidence,
            philosophical_basis=basis,
            merkle_root=merkle_root,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# WebSocket for live updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time system updates"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            # Send system status every second
            if kaygee_system:
                status = await get_status()
                metrics = await get_metrics()
                
                await websocket.send_json({
                    "type": "update",
                    "status": status,
                    "metrics": metrics,
                    "timestamp": time.time()
                })
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "system_available": kaygee_system is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
