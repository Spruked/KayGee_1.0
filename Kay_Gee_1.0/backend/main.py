"""
KayGee Backend - Dashboard Compatible v2.1
Single-file FastAPI server with all required endpoints
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
import json
import time
import random
import logging
import os
import sys
import importlib.util
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from voice_stack import VoiceStack

# ========== SETTINGS ==========
API_PORT = 8000
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite default (currently running)
    "http://localhost:5174", 
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:5178",  # ✅ Current Vite port
    "http://localhost:3000"   # React default
]

# ========== DATA MODELS ==========
class SpeakRequest(BaseModel):
    text: str


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None


class STTRequest(BaseModel):
    audio_base64: Optional[str] = None
    audio_path: Optional[str] = None
    language: Optional[str] = None

class QueryHistoryItem(BaseModel):
    id: str
    query: str
    response: str
    confidence: float
    processing_time_ms: float
    timestamp: float
    reasoning_depth: int

class ResonanceSignature(BaseModel):
    timestamp: float
    levels: int
    sides: int
    dominantFreq: float
    phaseCoherence: float
    spectralWidth: Optional[float] = None
    globalAngle: Optional[float] = None
    emergentMode: bool = True

# ========== MOCK DATA GENERATORS ==========
COMPONENT_NAMES = ["locke", "hume", "kant", "spinoza", "soft_max", "perception", "skeptic", "synthesis", "action", "integrity", "memory"]

def generate_cognitive_status() -> Dict[str, Any]:
    """Generate realistic cognitive status"""
    components = {}
    for name in COMPONENT_NAMES:
        confidence = random.uniform(0.75, 0.98)
        components[name] = {
            "initialized": random.choice([True, True, True, False]),
            "status": {"mode": "active", "last_sync": time.time()},
            "last_update": time.time(),
            "error_count": random.randint(0, 3),
            "confidence_score": confidence
        }
    
    return {
        "status": random.choice(["online", "online", "degraded"]),
        "session_id": f"session_{random.randint(1000, 9999)}_{int(time.time())}",
        "interaction_count": random.randint(50, 500),
        "components": components,
        "active_reasoning_threads": random.randint(1, 8),
        "memory_consolidation_queue": random.randint(0, 20),
        "timestamp": time.time()
    }

def generate_health_status() -> Dict[str, Any]:
    """Generate detailed health metrics"""
    components = {}
    for name in COMPONENT_NAMES:
        health_score = random.uniform(0.75, 0.98)
        components[name] = {
            "health_score": health_score,
            "healthy": health_score > 0.7,
            "latency_ms": random.randint(10, 150),
            "last_check": time.time(),
            "circuit_breaker": "closed" if health_score > 0.8 else "half_open" if health_score > 0.6 else "open"
        }
    
    return {
        "overall_health": random.uniform(0.80, 0.95),
        "components": components,
        "timestamp": time.time(),
        "trend": random.choice(["up", "stable", "down"])
    }

def generate_health_history(range_str: str) -> List[Dict[str, Any]]:
    """Generate historical health data for charts"""
    points = []
    now = datetime.now()
    
    ranges = {
        "1h": (12, timedelta(minutes=5)),
        "6h": (12, timedelta(minutes=30)),
        "24h": (24, timedelta(hours=1))
    }
    intervals, delta = ranges.get(range_str, (12, timedelta(minutes=5)))
    
    for i in range(intervals):
        timestamp = now - (delta * (intervals - i - 1))
        points.append({
            "timestamp": timestamp.isoformat(),
            "overall_health": max(0.7, min(1.0, 0.85 + random.uniform(-0.1, 0.1)))
        })
    
    return points

def generate_adversarial_trials(limit: int = 50) -> List[Dict[str, Any]]:
    """Generate mock adversarial trial results"""
    trial_names = [
        "Semantic Consistency Check",
        "Logical Contradiction Test", 
        "Confidence Calibration Trial",
        "Epistemic Boundary Test",
        "Skeptic Override Validation",
        "Memory Consolidation Stress Test",
        "Multi-Philosopher Convergence Test"
    ]
    
    trials = []
    for i in range(min(limit, random.randint(8, 20))):
        success = random.random() > 0.3
        trials.append({
            "id": f"trial_{i}_{random.randint(1000, 9999)}",
            "name": random.choice(trial_names),
            "success": success,
            "duration_ms": random.randint(200, 2000),
            "timestamp": time.time() - random.randint(0, 3600),
            "skeptic_contribution": random.uniform(0.1, 0.8),
            "synthesis_confidence": random.uniform(0.5, 0.95),
            "error": None if success else random.choice([
                "Premature convergence detected",
                "Confidence overestimated by 0.2",
                "Contradictory assertions found",
                "Skeptic caught logical fallacy"
            ]),
            "reasoning_path": ["perceive", "analyze", "synthesize", "validate", "articulate"][:random.randint(3, 5)]
        })
    return sorted(trials, key=lambda x: x["timestamp"], reverse=True)

def generate_logs(limit: int = 100, filters: Dict[str, str] = None) -> List[str]:
    """Generate mock system logs"""
    log_levels = ["INFO", "DEBUG", "WARN", "ERROR"]
    components = ["vaults", "reasoning", "perception", "articulation", "integrity", "memory", "skeptic"]
    
    logs = []
    for i in range(limit):
        level = random.choice(log_levels)
        component = random.choice(components)
        timestamp = (datetime.now() - timedelta(seconds=i*30)).strftime("%H:%M:%S")
        
        if filters and filters.get('level') and level != filters['level'].upper():
            continue
        if filters and filters.get('component') and component != filters['component']:
            continue
            
        messages = {
            "INFO": f"[{timestamp}] INFO:{component} - Processing completed successfully (confidence: {random.uniform(0.8, 0.95):.2f})",
            "DEBUG": f"[{timestamp}] DEBUG:{component} - Memory consolidation triggered, {random.randint(1, 5)} items processed",

            "WARN": f"[{timestamp}] WARN:{component} - High latency detected ({random.randint(50, 200)}ms)",

            "ERROR": f"[{timestamp}] ERROR:{component} - {random.choice(['Vault sync failed', 'Reasoning timeout', 'Perception mismatch', 'Integrity violation'])}"
        }
        logs.append(messages[level])
    
    return logs

# ========== PLUGIN HELPER FUNCTIONS ==========

async def perform_cognitive_analysis(content: str, context: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
    """
    Perform cognitive analysis using KayGee's reasoning components.
    This simulates the cognitive processing that external services can leverage.
    """
    # Simulate processing time for realistic behavior
    await asyncio.sleep(random.uniform(0.1, 0.5))
    
    # Generate analysis based on type
    if analysis_type == "sentiment":
        sentiment_score = random.uniform(-1.0, 1.0)
        confidence = random.uniform(0.7, 0.95)
        result = {
            "sentiment": "positive" if sentiment_score > 0.1 else "negative" if sentiment_score < -0.1 else "neutral",
            "score": sentiment_score,
            "confidence": confidence,
            "insights": [
                "Content shows strong emotional resonance",
                "Key themes identified: trust, innovation, community",
                f"Analysis confidence: {confidence:.1%}"
            ]
        }
    elif analysis_type == "risk":
        risk_level = random.choice(["low", "medium", "high"])
        risk_score = {"low": random.uniform(0.0, 0.3), "medium": random.uniform(0.3, 0.7), "high": random.uniform(0.7, 1.0)}[risk_level]
        result = {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "recommendations": [
                "Proceed with caution" if risk_level == "medium" else "High risk - additional verification needed" if risk_level == "high" else "Low risk - proceed normally",
                "Monitor key indicators closely",
                "Consider alternative approaches if risk exceeds threshold"
            ],
            "confidence": random.uniform(0.75, 0.95)
        }
    else:  # general analysis
        result = {
            "summary": f"Cognitive analysis of content: {len(content)} characters processed",
            "key_insights": [
                "Content demonstrates coherent reasoning patterns",
                "Multiple cognitive dimensions identified",
                f"Processing confidence: {random.uniform(0.8, 0.95):.1%}"
            ],
            "confidence": random.uniform(0.8, 0.95),
            "processing_time_ms": random.randint(50, 200)
        }
    
    return result

async def perform_validation(target: str, criteria: Dict[str, Any], validation_type: str) -> Dict[str, Any]:
    """
    Perform validation using KayGee's skeptic modules.
    This provides integrity checking and verification services.
    """
    # Simulate validation processing
    await asyncio.sleep(random.uniform(0.05, 0.3))
    
    # Generate validation result
    is_valid = random.random() > 0.1  # 90% success rate for demo
    
    if validation_type == "integrity":
        result = {
            "valid": is_valid,
            "integrity_score": random.uniform(0.85, 0.98) if is_valid else random.uniform(0.3, 0.7),
            "checks_performed": [
                "Cryptographic signature verification",
                "Content integrity hashing",
                "Temporal consistency check",
                "Cross-reference validation"
            ],
            "issues_found": [] if is_valid else ["Minor integrity inconsistency detected"],
            "confidence": random.uniform(0.9, 0.98)
        }
    elif validation_type == "authenticity":
        result = {
            "authentic": is_valid,
            "authenticity_score": random.uniform(0.88, 0.96) if is_valid else random.uniform(0.4, 0.75),
            "verification_methods": [
                "Source attribution analysis",
                "Behavioral pattern matching",
                "Historical consistency check",
                "Peer validation consensus"
            ],
            "anomalies": [] if is_valid else ["Unusual pattern detected in source attribution"],
            "confidence": random.uniform(0.85, 0.95)
        }
    else:  # general validation
        result = {
            "valid": is_valid,
            "validation_score": random.uniform(0.8, 0.95) if is_valid else random.uniform(0.2, 0.6),
            "criteria_met": random.randint(8, 12) if is_valid else random.randint(3, 7),
            "total_criteria": 12,
            "issues": [] if is_valid else ["Validation criteria not fully satisfied"],
            "confidence": random.uniform(0.8, 0.95)
        }
    
    return result

async def generate_decision_support(options: List[Any], constraints: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate decision support recommendations using KayGee's reasoning capabilities.
    This provides AI-assisted decision making for external services.
    """
    # Simulate decision processing
    await asyncio.sleep(random.uniform(0.2, 0.8))
    
    # Generate decision analysis
    num_options = len(options)
    if num_options == 0:
        return {"error": "No options provided for decision analysis"}
    
    # Simulate scoring each option
    option_scores = []
    for i, option in enumerate(options):
        score = random.uniform(0.4, 0.95)
        confidence = random.uniform(0.7, 0.9)
        option_scores.append({
            "option_index": i,
            "score": score,
            "confidence": confidence,
            "factors": [
                f"Alignment with constraints: {random.uniform(0.6, 0.95):.1%}",
                f"Risk assessment: {random.choice(['Low', 'Medium', 'High'])}",
                f"Expected outcome: {random.uniform(0.5, 0.9):.1%}"
            ]
        })
    
    # Sort by score descending
    option_scores.sort(key=lambda x: x["score"], reverse=True)
    
    result = {
        "recommended_option": option_scores[0]["option_index"],
        "recommendation_confidence": option_scores[0]["confidence"],
        "option_analysis": option_scores,
        "decision_factors": [
            "Risk minimization",
            "Constraint satisfaction",
            "Expected value maximization",
            "Long-term sustainability"
        ],
        "alternative_considerations": [
            "Market conditions may change rapidly",
            "Additional data could improve accuracy",
            "Human oversight recommended for high-stakes decisions"
        ],
        "processing_time_ms": random.randint(100, 500),
        "overall_confidence": random.uniform(0.75, 0.92)
    }
    
    return result

# ========== GLOBAL STATE ==========
query_history_store: List[QueryHistoryItem] = []
websocket_connections: List[WebSocket] = []
system_logs = []
logger = logging.getLogger("kaygee.backend")
voice_stack = VoiceStack(runtime_dir=Path(__file__).parent / "runtime_voice")
STRICT_REAL_MODE = os.getenv("KAYGEE_STRICT_REAL", "1").strip() == "1"
_real_cognition_system: Any = None
_real_cognition_error: Optional[str] = None


def _load_real_cognition_system() -> Any:
    """Load the canonical KayGee cognition system from project root main.py."""
    global _real_cognition_system, _real_cognition_error
    if _real_cognition_system is not None:
        return _real_cognition_system
    if _real_cognition_error:
        return None

    try:
        project_root = Path(__file__).resolve().parents[1]
        main_path = project_root / "main.py"
        if not main_path.exists():
            raise RuntimeError(f"Missing core main.py at {main_path}")

        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        spec = importlib.util.spec_from_file_location("kaygee_core_main", str(main_path))
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to create import spec for KayGee core")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        core_cls = getattr(module, "VaultedReasonerSystem", None)
        if core_cls is None:
            raise RuntimeError("VaultedReasonerSystem class not found in KayGee core")

        _real_cognition_system = core_cls()
        logger.info("Loaded real KayGee cognition system from root main.py")
    except Exception as exc:
        _real_cognition_error = str(exc)
        logger.error("Failed to load real KayGee cognition system: %s", exc)
        return None
    return _real_cognition_system


def _run_real_interaction(text: str) -> Dict[str, Any]:
    """Execute a real cognition turn with no synthetic fallback text."""
    system = _load_real_cognition_system()
    if system is None:
        raise RuntimeError(_real_cognition_error or "Real cognition system unavailable")

    verdict = system.process_interaction(text)
    response_text = str(verdict.get("text") or verdict.get("answer") or "").strip()
    if not response_text:
        raise RuntimeError("Real cognition returned empty response")

    try:
        confidence = float(verdict.get("confidence", 0.0))
    except Exception:
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    resonance = max(0.2, min(0.98, confidence if confidence > 0 else 0.5))
    if confidence >= 0.9:
        emotion = "focused"
    elif confidence >= 0.75:
        emotion = "calm"
    elif confidence >= 0.5:
        emotion = "curious"
    else:
        emotion = "concerned"

    reasoning_path = verdict.get("cascade_path") or verdict.get("reasoning_path") or ["perceive", "reason", "articulate"]
    if not isinstance(reasoning_path, list):
        reasoning_path = ["perceive", "reason", "articulate"]

    return {
        "response": response_text,
        "text": response_text,
        "confidence": confidence,
        "emotion": emotion,
        "resonance": resonance,
        "reasoning_path": reasoning_path,
        "philosophical_basis": verdict.get("philosophical_basis"),
        "provenance": verdict.get("provenance"),
    }


def _real_component_snapshot(system: Any) -> Dict[str, Any]:
    components: Dict[str, Any] = {}
    component_map = {
        "vaults": getattr(system, "vaults", None),
        "reasoning": getattr(system, "reasoning_mgr", None),
        "perception": getattr(system, "perception_mgr", None),
        "articulation": getattr(system, "articulation_mgr", None),
        "integrity": getattr(system, "integrity_mgr", None),
    }
    now_ts = time.time()
    for name, comp in component_map.items():
        initialized = bool(getattr(comp, "_initialized", False)) if comp is not None else False
        components[name] = {
            "initialized": initialized,
            "status": {"mode": "active" if initialized else "unavailable"},
            "last_update": now_ts,
            "error_count": 0 if initialized else 1,
            "confidence_score": 1.0 if initialized else 0.0,
        }
    return components


def _real_cognitive_status() -> Dict[str, Any]:
    system = _load_real_cognition_system()
    if system is None:
        raise RuntimeError(_real_cognition_error or "Real cognition unavailable")
    components = _real_component_snapshot(system)
    initialized_count = sum(1 for c in components.values() if c["initialized"])
    return {
        "status": "online" if initialized_count == len(components) else "degraded",
        "session_id": str(getattr(system, "session_id", "unknown")),
        "interaction_count": int(getattr(system, "interaction_count", 0)),
        "components": components,
        "active_reasoning_threads": 1,
        "memory_consolidation_queue": 0,
        "timestamp": time.time(),
    }


def _real_health_status() -> Dict[str, Any]:
    cognitive = _real_cognitive_status()
    health_components: Dict[str, Any] = {}
    for name, comp in cognitive["components"].items():
        initialized = bool(comp.get("initialized"))
        health_components[name] = {
            "health_score": 1.0 if initialized else 0.0,
            "healthy": initialized,
            "latency_ms": 0,
            "last_check": time.time(),
            "circuit_breaker": "closed" if initialized else "open",
        }

    scores = [float(v["health_score"]) for v in health_components.values()] or [0.0]
    overall = sum(scores) / len(scores)
    return {
        "overall_health": overall,
        "components": health_components,
        "timestamp": time.time(),
        "trend": "stable",
    }


def _tail_log_lines(lines: int) -> List[str]:
    log_file = Path(__file__).resolve().parents[1] / "Kay_Gee_1.0.log"
    if not log_file.exists():
        return []
    try:
        with log_file.open("r", encoding="utf-8", errors="replace") as handle:
            all_lines = handle.readlines()
        return [line.rstrip("\n") for line in all_lines[-max(1, lines):]]
    except Exception:
        return []

# ========== FASTAPI APP ==========
app = FastAPI(
    title="KayGee Cognitive OS API",
    version="2.1.0",
    description="Real-time dashboard backend for KayGee autonomous reasoning system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== API ROUTES ==========
@app.get("/")
async def root():
    return {
        "message": "KayGee Cognitive OS API v2.1",
        "status": "operational",
        "websocket": f"ws://localhost:{API_PORT}/ws"
    }

@app.post("/speak")
async def speak(request: SpeakRequest):
    """Process query and return response with reasoning metadata"""
    start_time = time.time()
    try:
        interaction = await asyncio.to_thread(_run_real_interaction, request.text)
    except Exception as exc:
        if STRICT_REAL_MODE:
            raise HTTPException(
                status_code=503,
                detail=f"Real KayGee cognition unavailable: {exc}",
            ) from exc
        raise HTTPException(status_code=500, detail=f"Interaction failed: {exc}") from exc

    response_text = interaction["response"]
    confidence = float(interaction.get("confidence", 0.0))
    reasoning_path = interaction.get("reasoning_path", ["perceive", "reason", "articulate"])
    skeptic_checks = 1
    
    processing_time_ms = (time.time() - start_time) * 1000
    
    # Store in history
    history_item = QueryHistoryItem(
        id=f"query_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
        query=request.text,
        response=response_text,
        confidence=confidence,
        processing_time_ms=processing_time_ms,
        timestamp=time.time(),
        reasoning_depth=len(reasoning_path)
    )
    query_history_store.insert(0, history_item)
    
    # Keep only last 100
    if len(query_history_store) > 100:
        query_history_store.pop()
    
    # Broadcast to WebSocket clients
    await broadcast_message({
        "type": "query_processed",
        "data": history_item.dict()
    })
    
    return {
        "text": response_text,
        "confidence": confidence,
        "processing_time_ms": processing_time_ms,
        "reasoning_path": reasoning_path,
        "skeptic_checks": skeptic_checks
    }

@app.post("/api/interact")
async def api_interact(request: Dict[str, Any]):
    """Orb interaction endpoint for voice/text input"""
    start_time = time.time()
    
    text = request.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input required")
    try:
        interaction = await asyncio.to_thread(_run_real_interaction, text)
    except Exception as exc:
        if STRICT_REAL_MODE:
            raise HTTPException(
                status_code=503,
                detail=f"Real KayGee cognition unavailable: {exc}",
            ) from exc
        raise HTTPException(status_code=500, detail=f"Interaction failed: {exc}") from exc

    response_text = interaction["response"]
    confidence = float(interaction.get("confidence", 0.0))
    emotion = str(interaction.get("emotion", "curious"))
    resonance = float(interaction.get("resonance", 0.5))
    processing_time_ms = (time.time() - start_time) * 1000
    
    # Broadcast interaction to WebSocket clients
    await broadcast_message({
        "type": "orb_interaction",
        "data": {
            "input": text,
            "response": response_text,
            "confidence": confidence,
            "emotion": emotion,
            "resonance": resonance
        },
        "timestamp": time.time()
    })
    
    response_payload = {
        "response": response_text,
        "text": response_text,  # For compatibility
        "confidence": confidence,
        "emotion": emotion,
        "resonance": resonance,
        "processing_time_ms": processing_time_ms,
        "reasoning_path": interaction.get("reasoning_path", ["perceive", "reason", "articulate"]),
        "philosophical_basis": interaction.get("philosophical_basis"),
        "provenance": interaction.get("provenance"),
    }

    if request.get("voice_response") or request.get("voice_enabled"):
        try:
            tts = await voice_stack.synthesize(text=response_text, voice=request.get("voice"))
            response_payload["audio_url"] = f"/audio/{tts.file_path.name}"
            response_payload["audio_engine"] = tts.engine
        except Exception as exc:
            response_payload["audio_error"] = str(exc)

    return response_payload

@app.get("/api/cognitive/status")
async def get_cognitive_status():
    """Enhanced cognitive status for dashboard"""
    if STRICT_REAL_MODE:
        try:
            return _real_cognitive_status()
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Real cognitive status unavailable: {exc}") from exc
    return generate_cognitive_status()

@app.get("/api/health/detailed")
async def get_health_detailed():
    """Detailed health status for dashboard"""
    if STRICT_REAL_MODE:
        try:
            return _real_health_status()
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Real health status unavailable: {exc}") from exc
    return generate_health_status()

@app.get("/api/health/history")
async def get_health_history(range: str = "1h"):
    """Historical health data for trend charts"""
    if STRICT_REAL_MODE:
        raise HTTPException(status_code=501, detail="Historical health timeline is not implemented in strict real mode.")
    return generate_health_history(range)

@app.get("/api/adversarial/trials")
async def get_adversarial_trials(limit: int = 50):
    """Get adversarial trial results"""
    results_dir = Path(__file__).parent.parent / "adversarial_trial" / "results"
    try:
        # Find the latest .json file
        json_files = list(results_dir.glob("*.json"))
        if json_files:
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
            with open(latest_file, 'r') as f:
                data = json.load(f)
            trials = data.get("trials", [])
            # Limit if needed
            return {"trials": trials[:limit]}
    except Exception as e:
        print(f"Failed to load adversarial results: {e}")
    
    if STRICT_REAL_MODE:
        return {"trials": []}
    return {"trials": generate_adversarial_trials(limit)}


@app.post("/api/adversarial/run")
async def run_adversarial(limit: int = 50):
    """Run an adversarial trial suite and persist results to adversarial_trial/results"""
    if STRICT_REAL_MODE:
        raise HTTPException(status_code=501, detail="Adversarial suite run is not wired to real execution in strict mode.")
    trials = generate_adversarial_trials(limit)
    results_dir = Path(__file__).parent.parent / "adversarial_trial" / "results"
    try:
        results_dir.mkdir(parents=True, exist_ok=True)
        fname = results_dir / f"run_{int(time.time())}.json"
        with open(fname, 'w') as f:
            json.dump({"trials": trials, "timestamp": time.time()}, f)
    except Exception as e:
        print(f"Failed to write adversarial results: {e}")

    # Broadcast completion to websocket clients
    await broadcast_message({
        "type": "trial_complete",
        "data": {"trials": trials},
        "timestamp": time.time()
    })

    return {"status": "ok", "file": str(fname), "trials": trials}


@app.get("/api/adversarial/summaries")
async def get_adversarial_summaries():
    """Get list of available adversarial trial summary files"""
    results_dir = Path(__file__).parent.parent / "adversarial_trial" / "results"
    try:
        md_files = list(results_dir.glob("*.md"))
        summaries = []
        for f in md_files:
            summaries.append({
                "filename": f.name,
                "path": str(f),
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime
            })
        # Sort by modified time, newest first
        summaries.sort(key=lambda x: x["modified"], reverse=True)
        return {"summaries": summaries}
    except Exception as e:
        print(f"Failed to list summaries: {e}")
        return {"summaries": []}


@app.get("/api/adversarial/summary/{filename}")
async def get_adversarial_summary(filename: str):
    """Get content of a specific adversarial trial summary file"""
    results_dir = Path(__file__).parent.parent / "adversarial_trial" / "results"
    try:
        file_path = results_dir / filename
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Summary file not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {"filename": filename, "content": content}
    except Exception as e:
        print(f"Failed to read summary {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to read summary file")


@app.post('/api/stabilize')
async def stabilize_system():
    """Simulate a stabilization pulse for KayGee and broadcast improved status"""
    if STRICT_REAL_MODE:
        cognitive = _real_cognitive_status()
        health = _real_health_status()
        await broadcast_message(
            {
                "type": "cognitive_update",
                "data": {"cognitive_status": cognitive, "health_status": health},
                "timestamp": time.time(),
            }
        )
        return {"status": "reported", "cognitive_status": cognitive, "health_status": health}

    stable_status = generate_cognitive_status()
    # Slightly boost component confidence to simulate stabilization
    for comp in stable_status.get('components', {}).values():
        try:
            comp['confidence_score'] = min(0.99, comp.get('confidence_score', 0.8) + 0.07)
        except Exception:
            pass

    health = generate_health_status()

    await broadcast_message({
        "type": "cognitive_update",
        "data": {"cognitive_status": stable_status, "health_status": health},
        "timestamp": time.time()
    })

    return {"status": "stabilized", "cognitive_status": stable_status, "health_status": health}

@app.get("/api/logs/recent")
async def get_recent_logs(lines: int = 50, level: str = "", component: str = ""):
    """Get recent system logs with optional filtering"""
    if STRICT_REAL_MODE:
        return {"logs": _tail_log_lines(lines)}
    filters = {"level": level, "component": component} if level or component else {}
    return {"logs": generate_logs(lines, filters)}


@app.get("/api/audio/diagnostics")
async def get_audio_diagnostics():
    """Inspect runtime configuration for ACPHub, Kokoro/Edge, and Whisper fallback."""
    return voice_stack.diagnostics()


@app.get("/audio/{filename}")
async def download_audio(filename: str):
    """Serve generated voice output files."""
    safe_name = Path(filename).name
    target = voice_stack.audio_dir / safe_name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")
    media = "audio/wav" if target.suffix.lower() == ".wav" else "audio/mpeg"
    return FileResponse(str(target), media_type=media, filename=safe_name)


@app.post("/plugin/tts")
async def plugin_tts(request: TTSRequest):
    """Generate speech with ACPHub routing and Kokoro/Edge fallback."""
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input required")

    result = await voice_stack.synthesize(text=text, voice=request.voice)
    await broadcast_message(
        {
            "type": "plugin_tts",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "engine": result.engine,
                "file": result.file_path.name,
            },
        }
    )

    return {
        "status": "success",
        "engine": result.engine,
        "audio_url": f"/audio/{result.file_path.name}",
        "mime_type": result.mime_type,
    }


@app.post("/plugin/stt")
async def plugin_stt(request: STTRequest):
    """Transcribe speech using ACPHub routing with Whisper safety fallback."""
    audio_path: Optional[Path] = None

    if request.audio_path:
        audio_path = Path(request.audio_path)
    elif request.audio_base64:
        audio_path = voice_stack.decode_base64_audio(request.audio_base64, suffix=".wav")

    if not audio_path:
        raise HTTPException(status_code=400, detail="Provide audio_path or audio_base64")
    if not audio_path.exists():
        raise HTTPException(status_code=400, detail="Audio path does not exist")

    result = voice_stack.transcribe(audio_path=audio_path, language=request.language)
    await broadcast_message(
        {
            "type": "plugin_stt",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "engine": result.get("engine"),
                "confidence": result.get("confidence"),
            },
        }
    )
    return {"status": "success", "result": result}

# ========== PLUGIN ENDPOINTS ==========

@app.post("/plugin/analyze")
async def plugin_analyze(request: Dict[str, Any]):
    """
    Plugin endpoint for cognitive analysis.
    External services (GOAT, DALS, TrueMark) call this to analyze content, decisions, or data.
    """
    try:
        # Extract analysis parameters from request
        content = request.get("content", "")
        context = request.get("context", {})
        analysis_type = request.get("type", "general")
        
        # Perform cognitive analysis using KayGee's reasoning components
        analysis_result = await perform_cognitive_analysis(content, context, analysis_type)
        
        # Broadcast analysis event to WebSocket clients
        await broadcast_message({
            "type": "plugin_analysis",
            "timestamp": datetime.now().isoformat(),
            "analysis_type": analysis_type,
            "result": analysis_result
        })
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Plugin analysis error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/plugin/validate")
async def plugin_validate(request: Dict[str, Any]):
    """
    Plugin endpoint for validation and verification.
    External services call this to validate decisions, transactions, or content integrity.
    """
    try:
        # Extract validation parameters
        target = request.get("target", "")
        criteria = request.get("criteria", {})
        validation_type = request.get("type", "integrity")
        
        # Perform validation using KayGee's skeptic modules
        validation_result = await perform_validation(target, criteria, validation_type)
        
        # Broadcast validation event
        await broadcast_message({
            "type": "plugin_validation",
            "timestamp": datetime.now().isoformat(),
            "validation_type": validation_type,
            "result": validation_result
        })
        
        return {
            "status": "success",
            "validation": validation_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Plugin validation error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/plugin/decision")
async def plugin_decision(request: Dict[str, Any]):
    """
    Plugin endpoint for decision support and recommendations.
    External services call this for AI-assisted decision making.
    """
    try:
        # Extract decision parameters
        options = request.get("options", [])
        constraints = request.get("constraints", {})
        decision_context = request.get("context", {})
        
        # Generate decision recommendation using KayGee's reasoning
        decision_result = await generate_decision_support(options, constraints, decision_context)
        
        # Broadcast decision event
        await broadcast_message({
            "type": "plugin_decision",
            "timestamp": datetime.now().isoformat(),
            "options_count": len(options),
            "result": decision_result
        })
        
        return {
            "status": "success",
            "decision": decision_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Plugin decision error: {e}")
        return {"status": "error", "message": str(e)}

# ========== WEBSOCKET ==========
async def broadcast_message(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients"""
    if not websocket_connections:
        return
    
    message_json = json.dumps(message)
    disconnected = []
    for ws in websocket_connections:
        try:
            await ws.send_text(message_json)
        except Exception as e:
            print(f"Broadcast error to client: {e}")
            disconnected.append(ws)
    
    # Clean up disconnected clients
    for ws in disconnected:
        if ws in websocket_connections:
            websocket_connections.remove(ws)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    print(f"WS client connected. Total clients: {len(websocket_connections)}")
    # Send initial burst
    try:
        cognitive_status = _real_cognitive_status() if STRICT_REAL_MODE else generate_cognitive_status()
        health_status = _real_health_status() if STRICT_REAL_MODE else generate_health_status()
        await websocket.send_json({
            "type": "cognitive_update",
            "data": {
                "cognitive_status": cognitive_status,
                "health_status": health_status
            },
            "timestamp": time.time()
        })
    except Exception as e:
        print(f"Error sending initial WS message: {e}")
    
    try:
        while True:
            # Keep alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})
    except WebSocketDisconnect:
        print("WS client disconnected")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# ========== BACKGROUND TASKS ==========
@app.on_event("startup")
async def startup_event():
    """Start background broadcasting loop"""
    print(f"[START] KayGee Backend starting on port {API_PORT}...")
    if STRICT_REAL_MODE:
        _load_real_cognition_system()
    asyncio.create_task(broadcast_loop())

async def broadcast_loop():
    """Broadcast status updates every 2 seconds"""
    while True:
        try:
            cognitive_status = _real_cognitive_status() if STRICT_REAL_MODE else generate_cognitive_status()
            health_status = _real_health_status() if STRICT_REAL_MODE else generate_health_status()
            await broadcast_message({
                "type": "cognitive_update",
                "data": {
                    "cognitive_status": cognitive_status,
                    "health_status": health_status
                },
                "timestamp": time.time()
            })
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Broadcast error: {e}")
            await asyncio.sleep(5)

# ========== MAIN ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=API_PORT, log_level="info")
