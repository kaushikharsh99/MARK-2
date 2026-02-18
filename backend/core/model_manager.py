from ..adapters.bitnet_adapter import BitNetAdapter

class ModelManager:
    def __init__(self):
        self.active_adapter = None
        self.adapters = {
            "bitnet": BitNetAdapter(),
            # "llama.cpp": LlamaAdapter(), # Future
        }

    def load_model(self, config):
        backend_type = config.get("backend", "bitnet")
        if backend_type in self.adapters:
            self.active_adapter = self.adapters[backend_type]
            return self.active_adapter.load(config)
        return False

    def generate(self, prompt, params):
        if self.active_adapter:
            return self.active_adapter.generate(prompt, params)
        return "Model not loaded."

    def unload(self):
        if self.active_adapter:
            self.active_adapter.unload()
