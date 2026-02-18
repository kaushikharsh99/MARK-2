import subprocess
import shutil
import os
import platform
import json
import requests
import time

def ensure_ollama_running():
    """Checks if Ollama is running, if not, starts it."""
    try:
        res = requests.get("http://127.0.0.1:11434/api/tags", timeout=1)
        if res.status_code == 200:
            return True
    except:
        pass
    
    print("🚀 Starting Ollama server...")
    try:
        # Start as detached process
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid if platform.system() == "Linux" else None,
        )
        
        # Poll for readiness
        for _ in range(10):
            try:
                res = requests.get("http://127.0.0.1:11434/api/tags", timeout=1)
                if res.status_code == 200:
                    return True
            except:
                pass
            time.sleep(1)
    except Exception as e:
        print(f"❌ Failed to start Ollama: {e}")
    
    return False

def get_ollama_models():
    try:
        res = subprocess.check_output(["ollama", "list", "--format", "json"], stderr=subprocess.STDOUT)
        data = json.loads(res.decode("utf-8"))
        return [m["name"] for m in data.get("models", [])]
    except:
        try:
            res = subprocess.check_output(["ollama", "list"], stderr=subprocess.STDOUT)
            lines = res.decode("utf-8").strip().split("\n")[1:] # Skip header
            return [line.split()[0] for line in lines if line]
        except:
            return []

def get_local_models(path):
    if not os.path.exists(path):
        return []
    models = []
    for f in os.listdir(path):
        if f.endswith(".gguf") or f.endswith(".bin"):
            models.append(f)
        elif os.path.isdir(os.path.join(path, f)):
            if os.path.exists(os.path.join(path, f, "config.json")):
                models.append(f)
    return models

def get_hf_models():
    hf_home = os.path.expanduser("~/.cache/huggingface/hub")
    if not os.path.exists(hf_home):
        return []
    models = []
    try:
        for d in os.listdir(hf_home):
            if d.startswith("models--"):
                parts = d.replace("models--", "").split("--")
                if len(parts) >= 2:
                    models.append("/".join(parts))
    except:
        pass
    return models

MARKETPLACE_MODELS = {
    "Ollama": [
        {"name": "llama3.2:3b", "size": "2.0GB", "description": "Meta's latest 3B model."},
        {"name": "llama3.1:8b", "size": "4.7GB", "description": "Standard 8B Llama 3.1."},
        {"name": "phi3:mini", "size": "2.3GB", "description": "Microsoft's lightweight model."},
        {"name": "gemma2:2b", "size": "1.6GB", "description": "Google's high-performance 2B model."},
    ],
    "Llama.cpp": [
        {"name": "Llama-3.2-3B-Instruct-Q4_K_M.gguf", "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf", "size": "2.0GB", "description": "Llama 3.2 3B - Q4 Quant"},
        {"name": "Phi-3.5-mini-instruct-Q4_K_M.gguf", "url": "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf", "size": "2.2GB", "description": "Phi-3.5 Mini - Q4 Quant"},
    ],
    "vLLM": [
        {"name": "meta-llama/Llama-3.2-3B-Instruct", "size": "6GB", "description": "Meta Llama 3.2 3B (Full)"},
        {"name": "microsoft/Phi-3.5-mini-instruct", "size": "7.5GB", "description": "Microsoft Phi-3.5 Mini (Full)"},
    ],
    "Whisper.cpp": [
        {"name": "ggml-tiny.en.bin", "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin", "size": "75MB", "description": "Tiny English model (Fastest)."},
        {"name": "ggml-base.en.bin", "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin", "size": "140MB", "description": "Base English model (Recommended)."},
        {"name": "ggml-small.en.bin", "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin", "size": "460MB", "description": "Small English model (Accurate)."},
        {"name": "ggml-tiny.bin", "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin", "size": "75MB", "description": "Tiny Multilingual model."},
        {"name": "ggml-base.bin", "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin", "size": "140MB", "description": "Base Multilingual model."},
        {"name": "ggml-small.bin", "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin", "size": "460MB", "description": "Small Multilingual model."},
    ],
    "Faster-Whisper": [
        {"name": "base", "size": "140MB", "description": "Faster-Whisper base model."},
        {"name": "small", "size": "460MB", "description": "Faster-Whisper small model."},
    ],
    "Vosk": [
        {"name": "vosk-model-small-en-us-0.15", "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip", "size": "40MB", "description": "Lightweight English model."},
    ],
    "Piper (Local)": [
        {"name": "en_US-ryan-high", "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx", "size": "28MB", "description": "Ryan - Professional male (Recommended)."},
        {"name": "en_US-amy-medium", "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx", "size": "15MB", "description": "Amy - Natural female voice."},
        {"name": "en_GB-alan-medium", "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/alan/medium/en_GB-alan-medium.onnx", "size": "15MB", "description": "Alan - British male accent."},
        {"name": "en_US-lessac-medium", "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx", "size": "15MB", "description": "Lessac - Balanced academic voice."},
        {"name": "en_US-joe-medium", "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/joe/medium/en_US-joe-medium.onnx", "size": "15MB", "description": "Joe - Friendly everyday male."},
        {"name": "en_US-linda-x_low", "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/linda/x_low/en_US-linda-x_low.onnx", "size": "3MB", "description": "Linda - Extremely fast & lightweight."},
        {"name": "en_US-arctic-medium", "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/arctic/medium/en_US-arctic-medium.onnx", "size": "15MB", "description": "Arctic - Clear US male."},
        {"name": "en_US-hfc_male-medium", "url": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/hfc_male/medium/en_US-hfc_male-medium.onnx", "size": "15MB", "description": "Deep Male - Deep resonant voice."},
    ],
    "Coqui TTS": [
        {"name": "tts_models/en/ljspeech/vits", "size": "150MB", "description": "High-quality VITS model."},
    ]
}

def download_model_task(provider, model_name, url=None):
    if provider == "Ollama":
        ensure_ollama_running()
        try:
            subprocess.run(["ollama", "pull", model_name], check=True)
            return {"status": "success", "message": f"Pulled {model_name} via Ollama."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    elif provider == "Llama.cpp":
        os.makedirs("llama_models", exist_ok=True)
        dest = os.path.join("llama_models", model_name)
        if download_file(url, dest): return {"status": "success", "message": f"Downloaded {model_name}."}
    elif provider == "Whisper.cpp":
        os.makedirs("whisper_models", exist_ok=True)
        dest = os.path.join("whisper_models", model_name)
        if download_file(url, dest): return {"status": "success", "message": f"Downloaded {model_name}."}
    elif provider == "Vosk":
        os.makedirs("vosk_models", exist_ok=True)
        dest = os.path.join("vosk_models", model_name + ".zip")
        if download_file(url, dest):
            subprocess.run(["unzip", dest, "-d", "vosk_models"], check=True)
            os.remove(dest)
            return {"status": "success", "message": f"Downloaded and extracted {model_name}."}
    elif provider == "Piper (Local)":
        voice_dir = os.path.join(os.getcwd(), "piper", "voices")
        os.makedirs(voice_dir, exist_ok=True)
        dest = os.path.join(voice_dir, model_name + ".onnx")
        config_url = url + ".json"
        config_dest = os.path.join(voice_dir, model_name + ".onnx.json")
        if download_file(url, dest) and download_file(config_url, config_dest):
            return {"status": "success", "message": f"Downloaded voice {model_name}."}
    return {"status": "error", "message": "Failed or invalid provider."}

def download_file(url, dest):
    try:
        subprocess.run(["curl", "-L", url, "-o", dest], check=True)
        return True
    except:
        return False

def check_model_providers():
    providers = {
        "Ollama": {"installed": False, "models": []},
        "Llama.cpp": {"installed": False, "models": []},
        "BitNet": {"installed": False, "models": []},
        "vLLM": {"installed": False, "models": []},
        "Whisper.cpp": {"installed": False, "models": []},
        "Faster-Whisper": {"installed": False, "models": []},
        "Vosk": {"installed": False, "models": []},
        "Piper (Local)": {"installed": False, "models": []},
        "Coqui TTS": {"installed": False, "models": []},
        "XTTS": {"installed": False, "models": []},
    }
    
    if shutil.which("ollama"):
        ensure_ollama_running()
        providers["Ollama"]["installed"] = True
        providers["Ollama"]["models"] = get_ollama_models()

    if shutil.which("llama-server") or os.path.exists("llama.cpp/build/bin/llama-server"):
        providers["Llama.cpp"]["installed"] = True
        providers["Llama.cpp"]["models"] = list(set(get_local_models("llama_models") + get_local_models("llama.cpp/models")))

    if os.path.exists("BitNet"):
        providers["BitNet"]["installed"] = True
        providers["BitNet"]["models"] = get_local_models("BitNet/models")

    try:
        import vllm
        providers["vLLM"]["installed"] = True
        providers["vLLM"]["models"] = list(set(get_hf_models() + get_local_models("vllm_models")))
    except ImportError:
        if shutil.which("vllm"):
            providers["vLLM"]["installed"] = True
            providers["vLLM"]["models"] = list(set(get_hf_models() + get_local_models("vllm_models")))

    if os.path.exists("whisper.cpp"):
        providers["Whisper.cpp"]["installed"] = True
        # Recursive search for models
        whisper_models = get_local_models("whisper_models")
        if os.path.exists("whisper.cpp/models"):
            for root, dirs, files in os.walk("whisper.cpp/models"):
                for f in files:
                    if f.endswith(".bin") and "ggml" in f:
                        whisper_models.append(f)
        providers["Whisper.cpp"]["models"] = list(set(whisper_models))

    try:
        import faster_whisper
        providers["Faster-Whisper"]["installed"] = True
    except ImportError: pass

    try:
        import vosk
        providers["Vosk"]["installed"] = True
        providers["Vosk"]["models"] = [d for d in os.listdir("vosk_models") if os.path.isdir(os.path.join("vosk_models", d))] if os.path.exists("vosk_models") else []
    except ImportError: pass

    # PIPER DETECTION: Look for binary in MARK-3/piper/piper
    piper_bin = os.path.join(os.getcwd(), "piper", "piper")
    if os.path.exists(piper_bin):
        providers["Piper (Local)"]["installed"] = True
        voice_dir = os.path.join(os.getcwd(), "piper", "voices")
        if os.path.exists(voice_dir):
            providers["Piper (Local)"]["models"] = [f.replace(".onnx", "") for f in os.listdir(voice_dir) if f.endswith(".onnx")]
    elif shutil.which("piper"):
        providers["Piper (Local)"]["installed"] = True

    try:
        import TTS
        providers["Coqui TTS"]["installed"] = True
        providers["XTTS"]["installed"] = True
    except ImportError: pass

    return providers

def install_provider(provider_name, password=None):
    if platform.system() != "Linux": return {"status": "error", "message": "Linux only."}
    
    try:
        if provider_name == "Ollama":
            cmd = "curl -fsSL https://ollama.com/install.sh | sh"
            if password: subprocess.run(f"sudo -S sh -c '{cmd}'", shell=True, input=password.encode()+b"\n", check=True)
            else: subprocess.run(cmd, shell=True, check=True)
        elif provider_name == "Llama.cpp":
            os.makedirs("llama_models", exist_ok=True)
            # build logic...
        elif provider_name == "Faster-Whisper":
            subprocess.run(["pip", "install", "faster-whisper"], check=True)
        elif provider_name == "Vosk":
            subprocess.run(["pip", "install", "vosk"], check=True)
            os.makedirs("vosk_models", exist_ok=True)
        elif provider_name == "vLLM":
            os.makedirs("vllm_models", exist_ok=True)
            subprocess.run(["pip", "install", "vllm"], check=True)
        elif provider_name == "Coqui TTS" or provider_name == "XTTS":
            subprocess.run(["pip", "install", "TTS"], check=True)
            os.makedirs("coqui_models", exist_ok=True)
        elif provider_name == "Piper (Local)":
            piper_dir = os.path.join(os.getcwd(), "piper")
            voice_dir = os.path.join(piper_dir, "voices")
            os.makedirs(voice_dir, exist_ok=True)
            
            piper_bin = os.path.join(piper_dir, "piper")
            if not os.path.exists(piper_bin):
                url = "https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz"
                subprocess.run(["curl", "-L", url, "-o", "piper.tar.gz"], check=True)
                os.makedirs("piper_tmp", exist_ok=True)
                subprocess.run(["tar", "-xzf", "piper.tar.gz", "-C", "piper_tmp"], check=True)
                
                extracted_dir = os.path.join("piper_tmp", "piper")
                if os.path.exists(extracted_dir):
                    # Move everything from extracted_dir to piper_dir
                    for item in os.listdir(extracted_dir):
                        s = os.path.join(extracted_dir, item)
                        d = os.path.join(piper_dir, item)
                        if os.path.isdir(s):
                            if os.path.exists(d): shutil.rmtree(d)
                            shutil.copytree(s, d)
                        else:
                            shutil.copy2(s, d)
                
                if os.path.exists(piper_bin):
                    os.chmod(piper_bin, 0o755)
                
                shutil.rmtree("piper_tmp")
                os.remove("piper.tar.gz")
            
            # Download default voice to piper/voices/
            download_model_task("Piper (Local)", "en_US-ryan-high", "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx")
            return {"status": "success", "message": "Piper (Local) installed successfully in MARK-3/piper directory."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
