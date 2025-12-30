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
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Determine whether to enable the full KayGee system at startup.
# To keep the API responsive during local development (and avoid importing
# heavy ML dependencies such as scikit-learn/scipy/torch), default to
# fallback mode. Install optional dependencies and set an explicit flag
# if you want the full system loaded.
_load_full = os.getenv("KAYGEE_LOAD_FULL", "0").lower() in ("1", "true", "yes", "y")
if _load_full:
    try:
        # Import components directly to avoid circular imports
        from src.handshake.manager import HandshakeProtocol
        from src.vaults import VaultManager

        # Import ReasoningManager directly from file to avoid package confusion
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "reasoning",
            str(Path(__file__).parent.parent / "src" / "reasoning.py")
        )
        reasoning_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reasoning_module)
        ReasoningManager = reasoning_module.ReasoningManager

        # Import PerceptionManager
        spec_perception = importlib.util.spec_from_file_location(
            "perception",
            str(Path(__file__).parent.parent / "src" / "perception.py")
        )
        perception_module = importlib.util.module_from_spec(spec_perception)
        spec_perception.loader.exec_module(perception_module)
        PerceptionManager = perception_module.PerceptionManager

        # Import ArticulationManager
        spec_articulation = importlib.util.spec_from_file_location(
            "articulation",
            str(Path(__file__).parent.parent / "src" / "articulation.py")
        )
        articulation_module = importlib.util.module_from_spec(spec_articulation)
        spec_articulation.loader.exec_module(articulation_module)
        ArticulationManager = articulation_module.ArticulationManager

        # Import IntegrityManager
        spec_integrity = importlib.util.spec_from_file_location(
            "integrity",
            str(Path(__file__).parent.parent / "src" / "integrity.py")
        )
        integrity_module = importlib.util.module_from_spec(spec_integrity)
        spec_integrity.loader.exec_module(integrity_module)
        IntegrityManager = integrity_module.IntegrityManager

        # Import PruningEngine
        spec_pruning = importlib.util.spec_from_file_location(
            "pruning",
            str(Path(__file__).parent.parent / "src" / "pruning.py")
        )
        pruning_module = importlib.util.module_from_spec(spec_pruning)
        spec_pruning.loader.exec_module(pruning_module)
        PruningEngine = pruning_module.PruningEngine

        # Import SKGHealthMonitor
        spec_health = importlib.util.spec_from_file_location(
            "health_monitor",
            str(Path(__file__).parent.parent / "src" / "health_monitor.py")
        )
        health_module = importlib.util.module_from_spec(spec_health)
        spec_health.loader.exec_module(health_module)
        SKGHealthMonitor = health_module.SKGHealthMonitor

        from src.temporal.context import TemporalContextLayer
        from src.meta.cognition import MetaCognitiveMonitor

        SYSTEM_AVAILABLE = True
        print("Notice: KAYGEE_LOAD_FULL=1 set — attempted to load full cognitive system.")
    except Exception as e:
        print(f"Warning: Full system import failed: {e}. Running in fallback mode.")
        SYSTEM_AVAILABLE = False
else:
    SYSTEM_AVAILABLE = False
    print("Notice: Running in fallback mode. To enable full system, set env var KAYGEE_LOAD_FULL=1 and install optional dependencies.")

# Fallback simple system if full system not available
class SimpleKayGeeSystem:
    """Simple fallback system for basic text communication"""
    
    def __init__(self):
        self.initialized = True
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a text query and return response"""
        # Simple echo response for now
        return {
            "response": f"I received your message: '{query}'. The full KayGee system is currently initializing. Please try again in a moment.",
            "confidence": 0.5,
            "timestamp": time.time()
        }

app = FastAPI(title="KayGee 1.0 API", version="1.0.0")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple system class to avoid circular imports
class KayGeeSystem:
    def __init__(self):
        if SYSTEM_AVAILABLE:
            self.handshake_protocol = HandshakeProtocol()
            config = {'handshake_protocol': self.handshake_protocol}
            
            # Initialize managers
            self.vaults = VaultManager()
            self.reasoning_mgr = ReasoningManager()
            self.perception_mgr = PerceptionManager()
            self.articulation_mgr = ArticulationManager()
            self.integrity_mgr = IntegrityManager()
            
            managers = [self.vaults, self.reasoning_mgr, self.perception_mgr, 
                       self.articulation_mgr, self.integrity_mgr]
            
            # Initialize managers defensively; fall back if any fail
            failed_managers = []
            for manager in managers:
                try:
                    ok = manager.initialize(config)
                except Exception as e:
                    print(f"Error initializing {getattr(manager, 'name', type(manager).__name__)}: {e}")
                    ok = False
                if not ok:
                    failed_managers.append(getattr(manager, 'name', type(manager).__name__))

            if failed_managers:
                print(f"⚠️  Failed to initialize managers: {failed_managers}. Falling back to SimpleKayGeeSystem.")
                self.fallback_system = SimpleKayGeeSystem()
                self.full_system = False
                return

            # Initialize other components
            try:
                self.pruning_engine = PruningEngine(self.vaults)
                self.skg_health_monitor = SKGHealthMonitor(self.vaults, self.reasoning_mgr, self.pruning_engine)
                self.temporal = TemporalContextLayer()
                self.metacognition = MetaCognitiveMonitor()
            except Exception as e:
                print(f"⚠️  Failed to initialize auxiliary components: {e}. Falling back to SimpleKayGeeSystem.")
                self.fallback_system = SimpleKayGeeSystem()
                self.full_system = False
                return

            self.session_id = f"api_session_{int(time.time())}"
            self.interaction_count = 0
            try:
                self.temporal.initialize_session(self.session_id)
            except Exception as e:
                print(f"Warning: temporal session initialization failed: {e}")
            self.full_system = True
        else:
            # Use fallback system
            self.fallback_system = SimpleKayGeeSystem()
            self.full_system = False
    
    def process_interaction(self, user_input: str, context=None):
        """Process interaction using managers"""
        if self.full_system:
            self.interaction_count += 1
            
            try:
                # Use managers for processing
                perception_result = self.perception_mgr.perceive(user_input)
                intent = self.perception_mgr.classify_intent(user_input)
                
                reasoning_result = self.reasoning_mgr.query({
                    "query": user_input,
                    "perception": perception_result,
                    "intent": intent
                }, vault_manager=self.vaults)
                
                action = reasoning_result.get("result", {}).get("action", "respond")
                boundary_ok = self.integrity_mgr.enforce_boundaries(action)
                
                response_text = self.articulation_mgr.articulate(reasoning_result.get("result", {}))
                
                return {
                    "text": response_text,
                    "confidence": reasoning_result.get("resonance_score", 0.8),
                    "philosophical_basis": reasoning_result.get("result", {}).get("philosopher", "integrated"),
                    "merkle_root": "placeholder",  # Would be actual merkle root
                    "processing_time": 0.1,
                    "reasoning_used": True
                }
                
            except Exception as e:
                return {
                    "text": "I apologize, but I'm having trouble processing that right now.",
                    "confidence": 0.0,
                    "philosophical_basis": "error",
                    "merkle_root": "error",
                    "processing_time": 0.0,
                    "reasoning_used": False,
                    "error": str(e)
                }
        else:
            # Use fallback system
            return self.fallback_system.process_query(user_input)

# Global system instance
kaygee_system: Optional[KayGeeSystem] = None
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
            kaygee_system = KayGeeSystem()
            print("✅ System ready")
        except Exception as e:
            print(f"⚠️  Failed to initialize system: {e}")
            import traceback
            traceback.print_exc()

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

# Frontend compatibility endpoints (stubs)
@app.get("/api/resonance/status")
async def get_resonance_status():
    """Return a simple resonance status expected by the frontend"""
    return {
        "phaseCoherence": 0.85,
        "dominantFreq": 2.4,
        "timestamp": time.time(),
        "harmonic_lock_count": 3,
        "turbulence_flag": False
    }


@app.post("/api/resonance")
async def post_resonance(signature: Dict[str, Any]):
    """Accept resonance signatures from the frontend (no-op stub)"""
    # In a full system this would be processed by DALS/metrics; here we accept and return ack
    return {"status": "received", "received": signature, "timestamp": time.time()}


@app.post("/visualization/space_field")
async def generate_space_field(params: Dict[str, Any]):
    """Generate a space field visualization.

    Attempts to delegate generation to the top-level `spacefield_generator/main.py`
    if present; otherwise falls back to a simple SVG stub.
    """
    try:
        # Try to import the external spacefield generator module from workspace root
        import importlib.util
        from pathlib import Path

        spacefield_path = Path(__file__).parent.parent.parent / "spacefield_generator" / "main.py"
        if spacefield_path.exists():
            spec = importlib.util.spec_from_file_location("spacefield_generator_main", spacefield_path)
            sf_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sf_mod)

            # Prefer an existing generator instance, else instantiate the class
            gen = None
            if hasattr(sf_mod, 'generator') and getattr(sf_mod, 'generator'):
                gen = getattr(sf_mod, 'generator')
            elif hasattr(sf_mod, 'SpaceFieldGenerator'):
                gen = sf_mod.SpaceFieldGenerator()

            if gen:
                # Map expected params and call generator
                sides = int(params.get('sides', 4))
                levels = int(params.get('levels', 3))
                alpha = float(params.get('alpha', 0.444))
                rotation_angle = float(params.get('rotation_angle', 0))
                edges_only = bool(params.get('edges_only', True))
                width = int(params.get('width', 400))
                height = int(params.get('height', 200))
                dpi = int(params.get('dpi', 100))

                fig, metrics = gen.generate(
                    sides=sides,
                    levels=levels,
                    alpha=alpha,
                    rotation_angle=rotation_angle,
                    edges_only=edges_only,
                    width=width,
                    height=height,
                    dpi=dpi
                )

                # Prefer generator-provided SVG helper if available
                if hasattr(gen, 'get_svg_string'):
                    svg_content = gen.get_svg_string(fig)
                else:
                    # Basic fallback serialization
                    svg_content = f"<svg width='{width}' height='{height}' xmlns='http://www.w3.org/2000/svg'><rect width='100%' height='100%' fill='#0b1226'/><text x='10' y='20' fill='#9bf'>Space Field Generated</text></svg>"

                # Try to close matplotlib figure if one was returned
                try:
                    import matplotlib.pyplot as plt
                    plt.close(fig)
                except Exception:
                    pass

                return {"svg": svg_content, "metrics": metrics, "timestamp": time.time()}

    except Exception as e:
        # Log and fall back to template stub
        print(f"⚠️  Space field generation via external module failed: {e}")

    # Fallback stub (keeps same shape as earlier simple stub)
    svg = "<svg xmlns='http://www.w3.org/2000/svg' width='400' height='200'>" \
          "<rect width='100%' height='100%' fill='#0b1226'/>" \
          "<text x='50' y='100' fill='#9bf' font-size='18'>Space Field Visualization (stub)</text></svg>"
    return {"svg": svg, "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
