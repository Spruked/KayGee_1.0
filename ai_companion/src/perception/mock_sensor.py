"""
Mock Sensor - Simulates mic/camera for development
No hardware required
"""

import asyncio
import random


class MockSensor:
    """Simulates mic/camera for development"""
    
    async def listen(self):
        """Simulates speech input"""
        await asyncio.sleep(0.5)  # Simulate processing delay
        scenarios = [
            {"text": "I'm stressed about work", "mood": "stressed", "context": "work"},
            {"text": "Tell me a joke", "mood": "bored", "context": "leisure"},
            {"text": "Should I lie to protect someone's feelings?", "mood": "conflicted", "context": "social"},
            {"text": "I'm worried about a health issue", "mood": "anxious", "context": "medical"},
            {"text": "Help me make a decision", "mood": "uncertain", "context": "general"},
        ]
        return random.choice(scenarios)
    
    async def see(self):
        """Simulates camera"""
        return {"objects": ["laptop", "coffee"], "scene": "workspace"}
