from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    @abstractmethod
    def load(self, config):
        """Load the model with given config."""
        pass

    @abstractmethod
    def generate(self, prompt, params):
        """Generate response for a prompt."""
        pass

    @abstractmethod
    def unload(self):
        """Unload model and free resources."""
        pass
