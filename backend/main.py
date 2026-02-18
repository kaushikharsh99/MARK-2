from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import os
import tempfile

from .core.config_manager import ConfigManager
from .core.module_manager import ModuleOrchestrator
from .core.hardware_utils import get_system_specs
from .core.model_provider_utils import check_model_providers, install_provider, MARKETPLACE_MODELS, download_model_task
from wake import init_wake_word_engine, wait_for_wake_word

from .api.audio_routes import router as audio_router

app = FastAPI()
app.include_router(audio_router)
config_mgr = ConfigManager()
orchestrator = ModuleOrchestrator()

# Global active websockets
active_websockets = set()

async def wake_word_task():
    """Background task to listen for the wake word."""
    porcupine = init_wake_word_engine()
    if not porcupine:
        return

    while True:
        # wait_for_wake_word is blocking, so run in thread
        if await asyncio.to_thread(wait_for_wake_word, porcupine):
            print("🔔 Wake word 'Jarvis' detected!")
            for ws in list(active_websockets):
                try:
                    await ws.send_json({
                        "sender": "System",
                        "type": "wake_word_detected",
                        "text": "Yes, sir? I'm listening."
                    })
                except:
                    active_websockets.remove(ws)
        await asyncio.sleep(0.1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(wake_word_task())

# Sync orchestrator with saved config at startup
llm_provider = config_mgr.config.get("llm", {}).get("Model Provider")
if llm_provider:
    orchestrator.switch_llm_provider(llm_provider)
    orchestrator.load_module("llm", config_mgr.config.get("llm", {}))

asr_provider = config_mgr.config.get("asr", {}).get("ASR Provider")
if asr_provider:
    orchestrator.switch_asr_provider(asr_provider)
    orchestrator.load_module("asr", config_mgr.config.get("asr", {}))

tts_provider = config_mgr.config.get("tts", {}).get("TTS Provider")
if tts_provider:
    orchestrator.switch_tts_provider(tts_provider)
    orchestrator.load_module("tts", config_mgr.config.get("tts", {}))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/system/overview")
async def get_overview():
    return orchestrator.get_system_overview()

@app.get("/api/system/specs")
async def get_specs():
    return get_system_specs()

@app.get("/api/providers")
async def get_providers():
    return check_model_providers()

@app.get("/api/marketplace/models")
async def get_marketplace_models():
    return MARKETPLACE_MODELS

@app.post("/api/marketplace/download")
async def download_marketplace_model(data: dict):
    provider = data.get("provider")
    model_name = data.get("model_name")
    url = data.get("url")
    # This should ideally be a background task, but for simplicity:
    return await asyncio.to_thread(download_model_task, provider, model_name, url)

@app.post("/api/providers/install")
async def install_provider_route(data: dict):
    provider = data.get("provider")
    password = data.get("password")
    return install_provider(provider, password)

@app.post("/api/model/load")
async def load_model_route():
    # Load settings from config
    llm_config = config_mgr.config.get("llm", {})
    success = orchestrator.load_module("llm", llm_config)
    return {"status": "success" if success else "error"}

@app.get("/api/config")
async def get_config():
    return config_mgr.config

@app.post("/api/config")
async def update_config(new_config_part: dict):
    current_config = config_mgr.config
    
    # Check if LLM settings are being updated
    llm_settings = new_config_part.get("llm")
    if llm_settings:
        active_provider = orchestrator.active_llm_provider
        old_model = current_config.get("llm", {}).get("Model")
        
        new_provider = llm_settings.get("Model Provider")
        new_model = llm_settings.get("Model")
        
        # Switch provider if it changed or doesn't match the orchestrator's state
        provider_changed = False
        if new_provider and new_provider != active_provider:
            orchestrator.switch_llm_provider(new_provider)
            provider_changed = True
            
        # If provider or model changed, trigger a reload
        if provider_changed or (new_model and new_model != old_model):
            # Merge for full config
            merged_llm = current_config.get("llm", {}).copy()
            merged_llm.update(llm_settings)
            # Run load in background thread to not block the response
            asyncio.create_task(asyncio.to_thread(orchestrator.load_module, "llm", merged_llm))
    
    # Check if ASR settings are being updated
    asr_settings = new_config_part.get("asr")
    if asr_settings:
        active_provider = orchestrator.active_asr_provider
        old_model = current_config.get("asr", {}).get("Model")
        
        new_provider = asr_settings.get("ASR Provider")
        new_model = asr_settings.get("Model")
        
        # Switch provider if it changed
        asr_provider_changed = False
        if new_provider and new_provider != active_provider:
            orchestrator.switch_asr_provider(new_provider)
            asr_provider_changed = True
            
        # Trigger reload if provider or model changed
        if asr_provider_changed or (new_model and new_model != old_model):
            merged_asr = current_config.get("asr", {}).copy()
            merged_asr.update(asr_settings)
            asyncio.create_task(asyncio.to_thread(orchestrator.load_module, "asr", merged_asr))

    # Check if TTS settings are being updated
    tts_settings = new_config_part.get("tts")
    if tts_settings:
        active_provider = orchestrator.active_tts_provider
        old_model = current_config.get("tts", {}).get("Model")
        
        new_provider = tts_settings.get("TTS Provider")
        new_model = tts_settings.get("Model")
        
        # Switch provider if it changed
        tts_provider_changed = False
        if new_provider and new_provider != active_provider:
            orchestrator.switch_tts_provider(new_provider)
            tts_provider_changed = True
            
        # Trigger reload if provider or model changed
        if tts_provider_changed or (new_model and new_model != old_model):
            merged_tts = current_config.get("tts", {}).copy()
            merged_tts.update(tts_settings)
            asyncio.create_task(asyncio.to_thread(orchestrator.load_module, "tts", merged_tts))

    # Merge the new config part into existing config
    for key, value in new_config_part.items():
        if key in current_config and isinstance(current_config[key], dict) and isinstance(value, dict):
            current_config[key].update(value)
        else:
            current_config[key] = value
            
    config_mgr.save_config(current_config)
    return {"status": "success"}

@app.post("/api/knowledge/ingest")
async def ingest_knowledge(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    orchestrator.ingest_knowledge(file.filename, text)
    return {"status": "ingested", "filename": file.filename}

@app.post("/api/memory/clear")
async def clear_memory():
    orchestrator.clear_memory()
    return {"status": "cleared"}

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            user_text = message.get("text", "")
            
            # Retrieve current system settings
            llm_settings = config_mgr.config.get("llm", {})
            personality = config_mgr.config.get("personality", {})
            system_prompt = llm_settings.get("System Prompt") or personality.get("system_prompt", "You are Jarvis.")
            
            # Map UI labels to generation params
            params = {
                "system_prompt": system_prompt,
                "temperature": float(llm_settings.get("Temperature") if llm_settings.get("Temperature") is not None else 0.7),
                "max_tokens": int(llm_settings.get("Max Tokens") if llm_settings.get("Max Tokens") is not None else 128),
                "top_p": float(llm_settings.get("Top P") if llm_settings.get("Top P") is not None else 1.0),
                "frequency_penalty": float(llm_settings.get("Frequency Penalty") if llm_settings.get("Frequency Penalty") is not None else 0.0),
                "use_rag": llm_settings.get("rag_enabled", True)
            }
            
            # Generate with context and RAG
            result = await asyncio.to_thread(
                orchestrator.generate_llm, 
                user_text, 
                params
            )
            
            response_payload = {
                "sender": "Jarvis",
                "text": result["text"],
                "sources": result.get("sources", [])
            }

            # Generate speech if requested
            if message.get("speak_response"):
                # Use a temp file for speech generation
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = tmp.name
                
                tts_path = await asyncio.to_thread(
                    orchestrator.synthesize,
                    result["text"],
                    {"output_path": tmp_path}
                )
                
                if tts_path and os.path.exists(tts_path):
                    import base64
                    with open(tts_path, "rb") as f:
                        audio_base64 = base64.b64encode(f.read()).decode("utf-8")
                    response_payload["audio"] = audio_base64
                    os.remove(tts_path)

            await websocket.send_json(response_payload)
            
    except WebSocketDisconnect:
        if websocket in active_websockets:
            active_websockets.remove(websocket)
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
