"""
KayGee 1.0 - FastAPI Backend
Real-time dashboard API with WebSocket streaming + Bio-Inspired Audio
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import time
import sys
from pathlib import Path
from typing import List

# Add parent to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / 'src'))

# Import real system
try:
    # Import from parent main.py (not this file)
    import importlib.util
    spec = importlib.util.spec_from_file_location("kaygee_main", parent_dir / "main.py")
    kaygee_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kaygee_module)
    VaultedReasoner = kaygee_module.VaultedReasoner
    SYSTEM_AVAILABLE = True
except Exception as e:
    print(f"⚠️  VaultedReasoner not available: {e}")
    SYSTEM_AVAILABLE = False
    VaultedReasoner = None

# Import bio-inspired audio system
try:
    from audio_streaming_bridge import audio_processor
    AUDIO_SYSTEM_AVAILABLE = True
    print("✅ Bio-inspired audio system loaded (Cochlear + POM)")
except ImportError as e:
    print(f"⚠️  Audio system not available: {e}")
    AUDIO_SYSTEM_AVAILABLE = False

# Import space field visualization
try:
    from visualization.space_field_generator import SpaceFieldGenerator
    VISUALIZATION_AVAILABLE = True
    print("✅ Space field visualization loaded")
except ImportError as e:
    print(f"⚠️  Visualization not available: {e}")
    VISUALIZATION_AVAILABLE = False

app = FastAPI(title="KayGee_1.0 Dashboard API", version="1.0.0")

# CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global system instance
kaygee = None

class Message(BaseModel):
    text: str

class SystemStatus(BaseModel):
    session_id: str
    interactions: int
    merkle_root: str
    personality_stability: float
    confidence: float
    philosopher: str
    drift: bool
    status: str
    timestamp: float

# WebSocket connections for live updates
connections: List[WebSocket] = []

@app.on_event("startup")
async def startup():
    """Initialize KayGee system on startup"""
    global kaygee
    
    print("\n" + "="*60)
    print("  KAYGEE 1.0 DASHBOARD API")
    print("="*60)
    
    if SYSTEM_AVAILABLE:
        try:
            print("🧠 Booting VaultedReasoner...")
            kaygee = VaultedReasoner()
            print("✅ System online")
        except Exception as e:
            print(f"⚠️  System boot failed: {e}")
            kaygee = None
    else:
        print("⚠️  Running in mock mode - install full system")
    
    print("\n🌐 API running at: http://localhost:8000")
    print("📊 Docs at: http://localhost:8000/docs")
    print("🎨 Frontend at: http://localhost:5173")
    print("="*60 + "\n")

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "KayGee 1.0 Dashboard API",
        "version": "1.0.0",
        "status": "online" if kaygee else "degraded",
        "endpoints": {
            "status": "/status",
            "speak": "/speak",
            "websocket": "/ws",
            "docs": "/docs"
        }
    }

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get current system status"""
    if not kaygee:
        return SystemStatus(
            session_id="offline",
            interactions=0,
            merkle_root="N/A",
            personality_stability=0.0,
            confidence=0.0,
            philosopher="None",
            drift=False,
            status="offline",
            timestamp=time.time()
        )
    
    try:
        merkle_root = "genesis"
        if hasattr(kaygee, 'merkle_vault'):
            try:
                merkle_root = kaygee.merkle_vault.get_current_root()[:16] + "..."
            except:
                pass
        
        return SystemStatus(
            session_id=getattr(kaygee, 'session_id', 'unknown'),
            interactions=getattr(kaygee, 'interaction_count', 0),
            merkle_root=merkle_root,
            personality_stability=0.94,  # TODO: Extract from PersonalityCore
            confidence=0.85,  # TODO: Extract from last decision
            philosopher="Balanced",
            drift=False,
            status="online",
            timestamp=time.time()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/speak")
async def speak(message: Message):
    """Process user message through KayGee reasoning"""
    if not kaygee:
        return {
            "text": "System is offline. Please start the full KayGee system.",
            "confidence": 0.0,
            "philosophical_basis": "N/A"
        }
    
    try:
        # Process through real system
        response = kaygee.process_interaction(message.text)
        
        # Broadcast to all connected WebSocket clients
        broadcast_data = {
            "type": "new_interaction",
            "user": message.text,
            "response": response.get("text", ""),
            "confidence": response.get("confidence", 1.0),
            "philosopher": response.get("philosophical_basis", "Unknown"),
            "timestamp": time.time()
        }
        await broadcast(broadcast_data)
        
        return response
        
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return {
            "text": f"I encountered an issue: {str(e)}",
            "confidence": 0.0,
            "philosophical_basis": "Error"
        }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for live system updates"""
    await websocket.accept()
    connections.append(websocket)
    
    print(f"🔌 WebSocket connected (total: {len(connections)})")
    
    # Send initial status
    try:
        status = await get_status()
        await websocket.send_text(json.dumps({
            "type": "status_update",
            "data": status.dict()
        }))
    except Exception as e:
        print(f"⚠️  Error sending initial status: {e}")
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Optional: handle direct WebSocket messages
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except:
                pass
                
    except WebSocketDisconnect:
        connections.remove(websocket)
        print(f"🔌 WebSocket disconnected (remaining: {len(connections)})")

async def broadcast(data: dict):
    """Broadcast message to all connected WebSocket clients"""
    if not connections:
        return
    
    message = json.dumps(data)
    for connection in connections[:]:  # Copy list to avoid modification during iteration
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"⚠️  Failed to send to client: {e}")
            try:
                connections.remove(connection)
            except ValueError:
                pass

# Space Field Visualization Endpoints
class SpaceFieldRequest(BaseModel):
    sides: int = 4
    levels: int = 3
    alpha: float = 0.444
    rotation_angle: float = 0
    edges_only: bool = True
    width: int = 600
    height: int = 600
    dpi: int = 100

@app.post("/visualization/space_field")
async def generate_space_field(request: SpaceFieldRequest):
    """
    Generate space field visualization from reasoning parameters.
    
    Maps KayGee cognitive state to geometric field:
    - levels = reasoning recursion depth
    - sides = active philosophical principles
    - alpha = confidence level
    - rotation_angle = emotional flow / attention shift
    """
    if not VISUALIZATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Visualization system not available")
    
    try:
        generator = SpaceFieldGenerator()
        fig, metrics = generator.generate(
            sides=request.sides,
            levels=request.levels,
            alpha=request.alpha,
            rotation_angle=request.rotation_angle,
            edges_only=request.edges_only,
            width=request.width,
            height=request.height,
            dpi=request.dpi
        )
        
        # Get SVG string for embedding
        svg_content = generator.get_svg_string(fig)
        
        import matplotlib.pyplot as plt
        plt.close(fig)
        
        return {
            "svg": svg_content,
            "metrics": metrics,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization generation failed: {str(e)}")

@app.get("/visualization/space_field/svg")
async def get_space_field_svg(
    sides: int = 4,
    levels: int = 3,
    alpha: float = 0.444,
    rotation: float = 0
):
    """Get space field as raw SVG (for direct img src)"""
    if not VISUALIZATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Visualization system not available")
    
    try:
        generator = SpaceFieldGenerator()
        fig, _ = generator.generate(
            sides=sides,
            levels=levels,
            alpha=alpha,
            rotation_angle=rotation,
            edges_only=True
        )
        
        svg_content = generator.get_svg_string(fig)
        
        import matplotlib.pyplot as plt
        plt.close(fig)
        
        from fastapi.responses import Response
        return Response(content=svg_content, media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SVG generation failed: {str(e)}")

# ============================================================================
# COGNITIVE RESONANCE ENDPOINT (Phase-Locked Loop Integration)
# ============================================================================

class ResonanceSignature(BaseModel):
    """Spectral signature from space field visualizer"""
    timestamp: float
    levels: int
    sides: int
    dominantFreq: float
    phaseCoherence: float  # PLL lock indicator (0-1)
    spectralWidth: float = None
    globalAngle: float = None
    emergentMode: bool = True

# Global resonance state (persists between calls)
current_resonance = {
    "phaseCoherence": 0.5,
    "dominantFreq": 0.0,
    "timestamp": 0,
    "harmonic_lock_count": 0,  # Consecutive frames at coherence > 0.95
    "turbulence_flag": False
}

@app.post("/api/resonance")
async def receive_resonance(signature: ResonanceSignature):
    """
    Receive spectral signature from space field visualizer
    
    This is the CLOSED-LOOP CONNECTION:
    1. JS visualizer streams phase coherence every 500ms
    2. Backend tracks harmonic lock state
    3. When phaseCoherence → 1.0: boost confidence, trigger harmonic response
    4. When phaseCoherence < 0.5: flag uncertainty, increase meta-cognitive checks
    
    The space field becomes KayGee's "emotional compass" - 
    geometric harmony reflects reasoning clarity.
    """
    global current_resonance
    
    # Update global state
    current_resonance["phaseCoherence"] = signature.phaseCoherence
    current_resonance["dominantFreq"] = signature.dominantFreq
    current_resonance["timestamp"] = signature.timestamp
    
    # Detect perfect harmonic lock
    if signature.phaseCoherence > 0.95:
        current_resonance["harmonic_lock_count"] += 1
        
        # After 3 consecutive perfect locks, trigger resonance event
        if current_resonance["harmonic_lock_count"] >= 3:
            print(f"🔥 PERFECT HARMONIC LOCK ACHIEVED")
            print(f"   Phase Coherence: {signature.phaseCoherence:.4f}")
            print(f"   Dominant Freq: {signature.dominantFreq:.2f} Hz")
            
            # Trigger KayGee response (if system available)
            if kaygee:
                asyncio.create_task(broadcast_event({
                    "type": "harmonic_lock",
                    "phaseCoherence": signature.phaseCoherence,
                    "message": "Perfect phase lock achieved - cognitive resonance at maximum"
                }))
    else:
        current_resonance["harmonic_lock_count"] = 0
    
    # Detect turbulence (low coherence)
    if signature.phaseCoherence < 0.5:
        if not current_resonance["turbulence_flag"]:
            current_resonance["turbulence_flag"] = True
            print(f"⚠️  Cognitive turbulence detected (coherence: {signature.phaseCoherence:.2f})")
    else:
        current_resonance["turbulence_flag"] = False
    
    return {
        "status": "received",
        "harmonic_lock_count": current_resonance["harmonic_lock_count"],
        "turbulence_flag": current_resonance["turbulence_flag"],
        "confidence_modifier": calculate_confidence_modifier(signature.phaseCoherence)
    }

def calculate_confidence_modifier(phase_coherence: float) -> float:
    """
    Map phase coherence to confidence modifier
    
    phaseCoherence = 1.0 → +20% confidence boost
    phaseCoherence = 0.5 → neutral (0%)
    phaseCoherence < 0.3 → -15% confidence penalty
    """
    if phase_coherence > 0.95:
        return 0.20  # Perfect lock: major boost
    elif phase_coherence > 0.8:
        return 0.10  # Good coherence: minor boost
    elif phase_coherence > 0.5:
        return 0.0   # Neutral
    elif phase_coherence > 0.3:
        return -0.10  # Turbulence: minor penalty
    else:
        return -0.15  # Severe turbulence: major penalty

@app.get("/api/resonance/status")
async def get_resonance_status():
    """Get current cognitive resonance state"""
    return current_resonance

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "system": "online" if kaygee else "offline",
        "websocket_connections": len(connections),
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
