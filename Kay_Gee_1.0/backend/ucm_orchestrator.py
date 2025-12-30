"""
UCM Orchestrator - Unified Cognitive Manifestation
The SOLE AUTHORITY for KayGee's presence state.
"""

from typing import Dict, List
from fastapi import WebSocket, HTTPException
import json
import asyncio
from datetime import datetime

class PresenceStore:
    """Single source of truth for KayGee's manifestation state"""

    def __init__(self):
        self.presence = {
            'authority': 'observer',
            'focus': 'local',
            'visibility': 'latent',
            'cognition': 'idle',
            'speech': 'silent',
            'resonance': 0.0,
            'reasoningPath': [],
            'lastUpdate': datetime.now().isoformat()
        }
        self.listeners: List[WebSocket] = []

    def get(self):
        return self.presence.copy()

    def set(self, updates: dict):
        """ONLY THIS METHOD CAN CHANGE PRESENCE STATE"""
        self.presence.update(updates)
        self.presence['lastUpdate'] = datetime.now().isoformat()

        # Broadcast to all subscribers
        update_msg = {
            'type': 'presence_update',
            'presence': self.presence
        }

        for ws in self.listeners[:]:
            try:
                asyncio.create_task(ws.send_json(update_msg))
            except:
                self.listeners.remove(ws)

        print(f"[PresenceStore] STATE UPDATE: {updates}")

    def subscribe(self, websocket: WebSocket):
        self.listeners.append(websocket)

    def unsubscribe(self, websocket: WebSocket):
        if websocket in self.listeners:
            self.listeners.remove(websocket)

# Global singleton
presence_store = PresenceStore()

class UCMOrchestrator:
    """Unified Cognitive Manifestation - Sole Authority"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.bubble_registry: Dict[str, Dict] = {}
        self.presence_store = presence_store

    async def initialize(self):
        """Load Seed vaults and initialize global SKG state"""
        print("🔧 UCM: Initializing presence store...")
        # Load any persisted state if needed

    async def connect(self, websocket: WebSocket, app_id: str):
        await websocket.accept()
        self.active_connections[app_id] = websocket
        self.presence_store.subscribe(websocket)
        print(f"🔌 UCM: {app_id} connected")

    def disconnect(self, app_id: str):
        if app_id in self.active_connections:
            ws = self.active_connections[app_id]
            self.presence_store.unsubscribe(ws)
            del self.active_connections[app_id]
            self.bubble_registry.pop(app_id, None)
            print(f"🔌 UCM: {app_id} disconnected")

    async def handle_message(self, app_id: str, data: dict):
        """UCM is the ONLY component that calls PresenceStore.set()"""

        if data["type"] == "ESCALATION_REQUEST":
            await self.handle_escalation(app_id, data)

        elif data["type"] == "VOICE_QUERY":
            await self.handle_voice(app_id, data)

        elif data["type"] == "DEMANIFEST_REQUEST":
            await self.handle_demanifest(app_id, data)

    async def handle_escalation(self, app_id: str, data: dict):
        # Validate request
        if not self.validate_permission(app_id, 'escalate_to_orb'):
            return

        # Run reasoning (full cascade)
        decision = await self.full_kaygee_reasoning(data['context'])

        # UCM SOLE AUTHORITY: Update presence
        self.presence_store.set({
            'authority': 'supervisory',
            'focus': 'escalated',
            'visibility': 'manifested',
            'cognition': 'reasoning',
            'speech': 'silent',
            'resonance': decision.confidence
        })

        # After reasoning completes
        await asyncio.sleep(2)  # Simulate reasoning time
        self.presence_store.set({
            'authority': 'advisory',
            'cognition': 'idle',
            'speech': 'speaking',
            'resonance': decision.confidence,
            'reasoningPath': decision.path
        })

    async def handle_voice(self, app_id: str, data: dict):
        # Start listening
        self.presence_store.set({ 'speech': 'listening' })

        # Process voice query
        decision = await self.full_kaygee_reasoning({'query': data['text']})

        # Complete interaction
        self.presence_store.set({
            'speech': 'speaking',
            'resonance': decision.confidence
        })

        # Send response back
        if app_id in self.active_connections:
            await self.active_connections[app_id].send_json({
                'type': 'VOICE_RESPONSE',
                'decision': decision
            })

    async def handle_demanifest(self, app_id: str, data: dict):
        # Reset to latent state
        self.presence_store.set({
            'authority': 'observer',
            'focus': 'local',
            'visibility': 'latent',
            'cognition': 'idle',
            'speech': 'silent',
            'resonance': 0.0
        })

    def validate_permission(self, app_id: str, permission: str) -> bool:
        """Check if bubble has required permission"""
        bubble = self.bubble_registry.get(app_id, {})
        permissions = bubble.get('permissions', [])
        return permission in permissions

    async def full_kaygee_reasoning(self, context: dict) -> dict:
        """Run full KayGee reasoning cascade"""
        # Mock implementation - replace with real reasoning
        return {
            'answer': 'I have analyzed this situation through multiple philosophical frameworks.',
            'confidence': 0.87,
            'path': ['Kant', 'Mill', 'Rawls', 'Harmonic_Convergence']
        }

# Global UCM instance
ucm_orchestrator = UCMOrchestrator()