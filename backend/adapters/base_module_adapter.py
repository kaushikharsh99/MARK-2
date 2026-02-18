from abc import ABC, abstractmethod

class BaseModuleAdapter(ABC):
    @abstractmethod
    def load(self, config):
        """Initialize/Load the module with config."""
        pass

    @abstractmethod
    def unload(self):
        """Shutdown/Unload the module."""
        pass

    @abstractmethod
    def generate(self, input_data, params):
        """Process input and return output."""
        pass

    @abstractmethod
    def get_status(self):
        """Return current status and metadata."""
        pass
