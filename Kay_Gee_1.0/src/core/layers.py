"""
Abstract Base Classes for System Layers
Provides common interfaces and contracts for all system components
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.core.protocols import IdentityBoundComponent


class SystemLayer(IdentityBoundComponent):
    """
    Base class for all system layers
    Ensures cryptographic identity and basic lifecycle management
    """

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self._initialized = False
        self._state_hash = None

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the layer with configuration"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Return current status and health metrics"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Gracefully shutdown the layer"""
        pass

    def is_initialized(self) -> bool:
        return self._initialized


class MemoryLayer(SystemLayer):
    """
    Abstract base for memory-related components
    """

    @abstractmethod
    def store(self, key: str, data: Any) -> bool:
        """Store data in memory"""
        pass

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory"""
        pass

    @abstractmethod
    def search_similar(self, query: Any, limit: int = 10) -> list:
        """Search for similar items"""
        pass


class ReasoningLayer(SystemLayer):
    """
    Abstract base for reasoning components
    """

    @abstractmethod
    def reason(self, context: Dict[str, Any], depth_limit: int = 5) -> Dict[str, Any]:
        """Perform reasoning with depth limit"""
        pass

    @abstractmethod
    def resolve_conflict(self, conflicts: list) -> Dict[str, Any]:
        """Resolve reasoning conflicts"""
        pass


class PerceptionLayer(SystemLayer):
    """
    Abstract base for perception components
    """

    @abstractmethod
    def perceive(self, input_data: Any) -> Dict[str, Any]:
        """Process input data"""
        pass

    @abstractmethod
    def classify_intent(self, text: str) -> str:
        """Classify user intent"""
        pass


class ArticulationLayer(SystemLayer):
    """
    Abstract base for articulation/NLG components
    """

    @abstractmethod
    def articulate(self, reasoning_result: Dict[str, Any]) -> str:
        """Generate natural language response"""
        pass

    @abstractmethod
    def tune_personality(self, philosopher: str) -> None:
        """Adjust personality for specific philosopher"""
        pass


class IntegrityLayer(SystemLayer):
    """
    Abstract base for integrity and safety components
    """

    @abstractmethod
    def check_integrity(self) -> Dict[str, Any]:
        """Perform integrity checks"""
        pass

    @abstractmethod
    def enforce_boundaries(self, action: str) -> bool:
        """Enforce safety boundaries"""
        pass