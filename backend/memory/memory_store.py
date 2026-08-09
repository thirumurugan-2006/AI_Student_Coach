from typing import Dict, Any, Optional

class MemoryStore:
    """
    Abstract repository layer for database interactions.
    Follows the Repository Pattern to isolate database logic from memory logic.
    """
    
    def __init__(self):
        # In a real implementation, this would take a database session or connection pool.
        # For now, we simulate an in-memory data store for the student memory.
        self._store: Dict[str, Dict[str, Any]] = {}

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by key."""
        return self._store.get(key)

    async def save(self, key: str, data: Dict[str, Any]) -> None:
        """Save a document by key."""
        self._store[key] = data

    async def update(self, key: str, update_data: Dict[str, Any]) -> None:
        """Update an existing document."""
        if key in self._store:
            self._store[key].update(update_data)
        else:
            self._store[key] = update_data

    async def delete(self, key: str) -> None:
        """Delete a document by key."""
        if key in self._store:
            del self._store[key]
