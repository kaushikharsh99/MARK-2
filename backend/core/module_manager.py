from ..adapters.llm.bitnet_adapter import BitNetAdapter
from ..adapters.llm.ollama_adapter import OllamaAdapter
from ..adapters.llm.llama_cpp_adapter import LlamaCppAdapter
from ..adapters.llm.vllm_adapter import VLLMAdapter
from ..adapters.asr.whisper_adapter import WhisperAdapter
from ..adapters.asr.faster_whisper_adapter import FasterWhisperAdapter
from ..adapters.asr.vosk_adapter import VoskAdapter
from ..adapters.tts.piper_adapter import PiperAdapter
from ..adapters.tts.coqui_tts_adapter import CoquiTTSAdapter
from ..adapters.knowledge.sqlite_rag_adapter import SQLiteRAGAdapter
from .memory_manager import MemoryManager

class ModuleOrchestrator:
    def __init__(self):
        self.llm_adapters = {
            "BitNet": BitNetAdapter(),
            "Ollama": OllamaAdapter(),
            "Llama.cpp": LlamaCppAdapter(),
            "vLLM": VLLMAdapter()
        }
        self.active_llm_provider = "BitNet"
        self.llm = self.llm_adapters[self.active_llm_provider]
        
        self.asr_adapters = {
            "Whisper.cpp": WhisperAdapter(),
            "Faster-Whisper": FasterWhisperAdapter(),
            "Vosk": VoskAdapter()
        }
        self.active_asr_provider = "Whisper.cpp"
        self.asr = self.asr_adapters[self.active_asr_provider]
        
        self.tts_adapters = {
            "Piper (Local)": PiperAdapter(),
            "Coqui TTS": CoquiTTSAdapter(),
            "XTTS": CoquiTTSAdapter() # XTTS is part of Coqui
        }
        self.active_tts_provider = "Piper (Local)"
        self.tts = self.tts_adapters[self.active_tts_provider]
        
        self.knowledge = SQLiteRAGAdapter()
        self.memory = MemoryManager()
        
        # Modules state
        self.enabled = {
            "llm": True,
            "asr": True,
            "tts": True,
            "knowledge": True
        }

    def switch_llm_provider(self, provider_name):
        if provider_name in self.llm_adapters:
            if self.active_llm_provider != provider_name:
                self.llm.unload()
                self.active_llm_provider = provider_name
                self.llm = self.llm_adapters[self.active_llm_provider]
                return True
        return False

    def switch_asr_provider(self, provider_name):
        if provider_name in self.asr_adapters:
            if self.active_asr_provider != provider_name:
                self.asr.unload()
                self.active_asr_provider = provider_name
                self.asr = self.asr_adapters[self.active_asr_provider]
                return True
        return False

    def switch_tts_provider(self, provider_name):
        if provider_name in self.tts_adapters:
            if self.active_tts_provider != provider_name:
                self.tts.unload()
                self.active_tts_provider = provider_name
                self.tts = self.tts_adapters[self.active_tts_provider]
                return True
        return False

    def get_system_overview(self):
        return {
            "llm": { 
                "enabled": self.enabled["llm"], 
                "active_provider": self.active_llm_provider,
                **self.llm.get_status() 
            },
            "asr": { 
                "enabled": self.enabled["asr"], 
                "active_provider": self.active_asr_provider,
                **self.asr.get_status() 
            },
            "tts": { 
                "enabled": self.enabled["tts"], 
                "active_provider": self.active_tts_provider,
                **self.tts.get_status() 
            },
            "knowledge": { "enabled": self.enabled["knowledge"], **self.knowledge.get_status() }
        }

    def load_module(self, module_type, config):
        # Normalize config keys (e.g., "Model Provider" -> "model_provider")
        normalized_config = {k.lower().replace(" ", "_"): v for k, v in config.items()}
        
        if module_type == "llm": 
            return self.llm.load(normalized_config)
        if module_type == "asr": 
            return self.asr.load(normalized_config)
        if module_type == "tts": 
            return self.tts.load(normalized_config)
        return False

    def generate_llm(self, user_input, params):
        if not self.enabled["llm"]: return "LLM Module is disabled."
        
        # 1. RAG Retrieval (If enabled)
        context = ""
        sources = []
        if self.enabled["knowledge"] and params.get("use_rag", True):
            retrieved = self.knowledge.retrieve(user_input)
            if retrieved:
                context = "\nRELEVANT CONTEXT FROM KNOWLEDGE BASE:\n"
                for item in retrieved:
                    context += f"--- Source: {item['source']} ---\n{item['content']}\n"
                    sources.append(item['source'])
                context += "\nEND OF CONTEXT.\n"

        # 2. Update Memory
        self.memory.add_message("user", user_input)
        
        # 3. Build Contextual Prompt
        history = self.memory.get_context_string()
        system_prompt = params.get("system_prompt", "You are Jarvis.")
        full_prompt = f"{system_prompt}\n{context}\n{history}Jarvis:"
        
        # 4. Generate
        response = self.llm.generate(full_prompt, params)
        
        # 5. Save Response
        if response and not response.startswith("Error"):
            self.memory.add_message("assistant", response)
            
        return {
            "text": response,
            "sources": sources
        }

    def transcribe(self, wav_path, params):
        if not self.enabled["asr"]: return None
        return self.asr.generate(wav_path, params)

    def synthesize(self, text, params):
        if not self.enabled["tts"]: return None
        return self.tts.generate(text, params)
    
    def ingest_knowledge(self, source: str, content: str):
        return self.knowledge.ingest(source, content)

    def clear_memory(self):
        self.memory.clear()
