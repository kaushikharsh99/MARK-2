import json
import os
from .hardware_utils import get_system_specs, suggest_model_config

CONFIG_PATH = "config.json"

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        else:
            return self.create_default_config()

    def create_default_config(self):
        specs = get_system_specs()
        suggestion = suggest_model_config(specs)
        
        default_config = {
            "system": specs,
            "model": suggestion,
            "personality": {
                "name": "Jarvis",
                "system_prompt": "You are Jarvis, a professional AI with a legendary sense of humor. Respond in a SINGLE, snappy, and genuinely funny sentence."
            },
            "ui": {
                "theme": "dark",
                "accent_color": "cyan"
            }
        }
        self.save_config(default_config)
        return default_config

    def save_config(self, config=None):
        if config:
            self.config = config
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)

    def update_model_config(self, new_model_settings):
        self.config["model"].update(new_model_settings)
        self.save_config()
