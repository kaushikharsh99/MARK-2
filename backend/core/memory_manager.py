from typing import List, Dict
import time

class MemoryManager:
    def __init__(self):
        # Short-term sliding window memory
        self.short_term_memory: List[Dict[str, str]] = []
        self.max_history = 10  # Keep last 10 turns
        
    def add_message(self, role: str, content: str):
        self.short_term_memory.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        self._prune()

    def get_history(self) -> List[Dict[str, str]]:
        return self.short_term_memory

    def get_context_string(self) -> str:
        """Converts structured history into a prompt string."""
        context = ""
        for msg in self.short_term_memory:
            role = "User" if msg["role"] == "user" else "Jarvis"
            context += f"{role}: {msg['content']}\n"
        return context

    def clear(self):
        self.short_term_memory = []

    def _prune(self):
        if len(self.short_term_memory) > self.max_history:
            self.short_term_memory = self.short_term_memory[-self.max_history:]
