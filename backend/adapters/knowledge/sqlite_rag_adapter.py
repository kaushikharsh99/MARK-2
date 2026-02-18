import sqlite3
import os
from typing import List, Dict, Any
from .base_knowledge_adapter import BaseKnowledgeAdapter

class SQLiteRAGAdapter(BaseKnowledgeAdapter):
    def __init__(self, db_path="knowledge.db"):
        self.db_path = db_path
        self._init_db()
        self.status = "Indexed"

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    content TEXT,
                    metadata TEXT
                )
            """)
            # Basic Full Text Search if available
            conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(content, content_id UNINDEXED)")

    def ingest(self, source: str, content: str, metadata: Dict[str, Any] = None):
        """Simple ingestion: splits by newline/paragraphs."""
        chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 20]
        
        with sqlite3.connect(self.db_path) as conn:
            for chunk in chunks:
                cursor = conn.execute(
                    "INSERT INTO knowledge_chunks (source, content, metadata) VALUES (?, ?, ?)",
                    (source, chunk, str(metadata))
                )
                chunk_id = cursor.lastrowid
                conn.execute("INSERT INTO fts_chunks (content, content_id) VALUES (?, ?)", (chunk, chunk_id))
        return True

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Keyword-based retrieval using SQLite FTS."""
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Fallback simple LIKE if FTS fails or for demo
                cursor = conn.execute("""
                    SELECT source, content FROM knowledge_chunks 
                    WHERE content LIKE ? LIMIT ?
                """, (f"%{query}%", top_k))
                
                for row in cursor:
                    results.append({
                        "source": row[0],
                        "content": row[1],
                        "score": 1.0 # Placeholder score
                    })
        except: pass
        return results

    def get_status(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM knowledge_chunks").fetchone()[0]
        return {
            "status": self.status,
            "documents": count,
            "chunks": count,
            "provider": "SQLite (Keyword Search)"
        }

    def clear(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self._init_db()
