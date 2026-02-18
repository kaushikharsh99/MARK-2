from fastapi import APIRouter, UploadFile, File, Response
import tempfile
import os
import subprocess
from ..core.config_manager import ConfigManager

router = APIRouter()
config_mgr = ConfigManager()

# We'll import the orchestrator instance from main or use a global one
# For simplicity in this session, we'll re-import or access it
from ..main import orchestrator

@router.post("/api/audio/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribes uploaded audio blob."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        clean_wav = tmp_path + "_clean.wav"
        subprocess.run(["ffmpeg", "-y", "-i", tmp_path, "-ar", "16000", "-ac", "1", clean_wav], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        text = orchestrator.transcribe(clean_wav, {"threads": 4}) 
        return {"text": text}
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)
        if os.path.exists(clean_wav): os.remove(clean_wav)

@router.post("/api/audio/speech")
async def text_to_speech(data: dict):
    """Generates speech and returns audio file for the browser."""
    text = data.get("text", "")
    if not text: return {"error": "No text provided"}
    
    output_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    
    # Generate via orchestrator
    result_path = orchestrator.synthesize(text, {"output_path": output_wav})
    
    if not result_path or not os.path.exists(result_path):
        return {"error": "TTS Generation Failed"}
        
    with open(result_path, "rb") as f:
        audio_content = f.read()
    
    os.remove(result_path)
    return Response(content=audio_content, media_type="audio/wav")
