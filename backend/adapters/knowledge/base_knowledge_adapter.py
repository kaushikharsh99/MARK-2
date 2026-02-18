from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseKnowledgeAdapter(ABC):
    @abstractmethod
    def ingest(self, source: str, content: Any, metadata: Dict[str, Any] = None):
        """Chunk and index content into the vector store."""
        pass

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant context based on the query."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Return indexing status and statistics."""
        pass

    @abstractmethod
    def clear(self):
        """Wipe the current index."""
        pass
