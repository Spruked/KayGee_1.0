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
import math
from pathlib import Path
from typing import List, Optional

# Add parent to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / 'Kay_Gee_1.0' / 'src'))

# Import real system
try:
    # Import from parent main.py (not this file)
    import importlib.util
    spec = importlib.util.spec_from_file_location("kaygee_main", parent_dir / "Kay_Gee_1.0" / "main.py")
    if spec is not None:
        kaygee_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(kaygee_module)
        VaultedReasoner = kaygee_module.VaultedReasonerSystem
        SYSTEM_AVAILABLE = True
    else:
        raise ImportError("Could not create module spec for kaygee_main")
except Exception as e:
    print(f"⚠️  VaultedReasoner not available: {e}")
    SYSTEM_AVAILABLE = False
    VaultedReasoner = None

# Import bio-inspired audio system
try:
    sys.path.insert(0, str(parent_dir / 'Kay_Gee_1.0' / 'api' / 'backend'))
    from audio_streaming_bridge import audio_processor
    AUDIO_SYSTEM_AVAILABLE = True
    print("✅ Bio-inspired audio system loaded (Cochlear + POM)")
except ImportError as e:
    print(f"⚠️  Audio system not available: {e}")
    AUDIO_SYSTEM_AVAILABLE = False


# Import space field visualization
try:
    # Import the space field 3D module
    spec = importlib.util.spec_from_file_location("space_field_3d", parent_dir / "space_field_3d.py")
    if spec is not None:
        space_field_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(space_field_module)
        SpaceField3D = space_field_module.SpaceField3D
        VISUALIZATION_AVAILABLE = True
        print("✅ Space field visualization loaded")
    else:
        raise ImportError("Could not load space field module")
except ImportError as e:
    print(f"⚠️  Visualization not available: {e}")
    VISUALIZATION_AVAILABLE = False
    SpaceField3D = None

# Wrapper class for the API
class SpaceFieldGenerator:
    def __init__(self):
        self.field = SpaceField3D() if SpaceField3D else None
        self.current_params = {
            'sides': 4,
            'levels': 3,
            'alpha': 0.444,
            'rotation_angle': 0
        }

    def generate(self, sides=4, levels=3, alpha=0.444, rotation_angle=0, edges_only=True, width=600, height=600, dpi=100):
        if not self.field:
            raise Exception("Space field system not available")

        # Store current parameters
        self.current_params = {
            'sides': sides,
            'levels': levels,
            'alpha': alpha,
            'rotation_angle': rotation_angle
        }

        # Generate the field
        self.field.generate_levels(
            radius=1.0,
            sides=sides,
            max_levels=levels,
            pattern="CC"  # Default pattern
        )

        # Create visualization
        fig = self.field.visualize_plotly(title=f"Space Field: O{sides}CCxx{levels}")

        # No mock metrics - real system must provide metrics
        metrics = {}

        return fig, metrics

    def get_svg_string(self, fig):
        """Create a simple SVG representation of the space field parameters"""
        sides = self.current_params['sides']
        levels = self.current_params['levels']
        
        # Create a geometric pattern based on parameters
        svg_parts = []
        svg_parts.append('<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">')
        
        # Background
        svg_parts.append('<rect width="400" height="400" fill="rgba(10, 10, 30, 0.9)"/>')
        
        # Central pattern
        center_x, center_y = 200, 200
        for level in range(levels):
            radius = 30 + level * 40
            opacity = 0.8 - level * 0.2
            
            # Draw polygon for each level
            if sides > 2:
                points = []
                for i in range(sides):
                    angle = (i * 2 * 3.14159 / sides) - 3.14159/2  # Start from top
                    x = center_x + radius * math.cos(angle)
                    y = center_y + radius * math.sin(angle)
                    points.append(f"{x},{y}")
                points_str = " ".join(points)
                svg_parts.append(f'<polygon points="{points_str}" fill="none" stroke="rgba(74, 144, 226, {opacity})" stroke-width="2"/>')
            
            # Add connecting lines for CC pattern
            if level > 0:
                for i in range(sides):
                    angle = (i * 2 * 3.14159 / sides) - 3.14159/2
                    x1 = center_x + (radius - 40) * math.cos(angle)
                    y1 = center_y + (radius - 40) * math.sin(angle)
                    x2 = center_x + radius * math.cos(angle)
                    y2 = center_y + radius * math.sin(angle)
                    svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="rgba(255, 100, 100, {opacity})" stroke-width="1"/>')
        
        # Add text label
        svg_parts.append(f'<text x="200" y="380" text-anchor="middle" fill="#4a90e2" font-size="14">O{sides}CCxx{levels} Space Field</text>')
        svg_parts.append('</svg>')
        
        return "".join(svg_parts)

# Create generator instance
generator = SpaceFieldGenerator() if VISUALIZATION_AVAILABLE else None

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
        raise HTTPException(status_code=503, detail="KayGee system not available - no mock status")
    
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
    """Process user message - transparent about system status"""
    if not kaygee:
        # No mock responses - be honest about system status
        return {
            "text": "System initialization incomplete. Real-time reasoning engine not available. Voice input acknowledged but cannot process through full cognitive architecture.",
            "confidence": 0.0,
            "status": "system_unavailable",
            "philosophical_basis": "system_integrity",
            "timestamp": time.time()
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
            "text": f"Processing failed: {str(e)}. System encountered an error during real-time reasoning.",
            "confidence": 0.0,
            "status": "processing_error",
            "error_details": str(e),
            "timestamp": time.time()
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
    if not VISUALIZATION_AVAILABLE or generator is None:
        raise HTTPException(status_code=503, detail="Visualization system not available")
    try:
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
    if not VISUALIZATION_AVAILABLE or generator is None:
        raise HTTPException(status_code=503, detail="Visualization system not available")
    try:
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
    spectralWidth: Optional[float] = None
    globalAngle: Optional[float] = None
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
