import psutil
import platform
import subprocess
import re

def get_system_specs():
    """Detects CPU, RAM, and VRAM specs."""
    specs = {
        "os": platform.system(),
        "cpu": {
            "name": platform.processor(),
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
        },
        "ram": {
            "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        },
        "gpu": None
    }

    # Basic NVIDIA VRAM detection for Linux
    try:
        if specs["os"] == "Linux":
            res = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])
            name, vram = res.decode("utf-8").strip().split(",")
            specs["gpu"] = {
                "name": name.strip(),
                "vram_gb": round(int(vram.strip()) / 1024, 2)
            }
    except Exception:
        pass # No NVIDIA GPU or nvidia-smi not found

    return specs

def suggest_model_config(specs):
    """Suggests model settings based on hardware."""
    ram = specs["ram"]["total_gb"]
    vram = specs["gpu"]["vram_gb"] if specs["gpu"] else 0
    
    suggestion = {
        "backend": "bitnet",
        "model_path": "",
        "threads": specs["cpu"]["cores"],
        "gpu_layers": 0,
        "mode": "Low-End"
    }

    if vram >= 12:
        suggestion["mode"] = "High-End"
        suggestion["gpu_layers"] = 35
    elif vram >= 6:
        suggestion["mode"] = "Mid-Range"
        suggestion["gpu_layers"] = 20
    elif ram >= 16:
        suggestion["mode"] = "Mid-Range (RAM)"
    
    return suggestion

if __name__ == "__main__":
    import json
    print(json.dumps(get_system_specs(), indent=4))
