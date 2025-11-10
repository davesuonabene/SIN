import abc
from typing import Any, Dict, Callable, List, Tuple
import numpy as np
from scipy.io.wavfile import write as write_wav

NODE_REGISTRY: Dict[str, 'BaseNode'] = {}

def register_node(name: str):
    def decorator(cls):
        NODE_REGISTRY[name] = cls
        return cls
    return decorator

class BaseNode(abc.ABC):
    NODE_NAME = "Base Node"
    
    def __init__(self, dpg_tag: int):
        self.dpg_tag = dpg_tag
        self.params = self.get_parameters()
        self.input_attr_map: Dict[str, int] = {}
        self.output_attr_map: Dict[str, int] = {}

    @staticmethod
    @abc.abstractmethod
    def get_attributes() -> Dict[str, Any]:
        pass

    @staticmethod
    @abc.abstractmethod
    def get_parameters() -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pass

@register_node("generator/audiocraft")
class AudioCraftNode(BaseNode):
    NODE_NAME = "AudioCraft"

    @staticmethod
    def get_attributes() -> Dict[str, Any]:
        return {
            "inputs": {},
            "outputs": {"audio_out": "audio"}
        }

    @staticmethod
    def get_parameters() -> Dict[str, Any]:
        return {"prompt": "a calm lo-fi hip hop beat"}

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.params.get("prompt", "default prompt")
        print(f"Computing AudioCraftNode {self.dpg_tag} with prompt: {prompt}")
        return {"audio_out": f"audio_from_prompt: {prompt}"}

@register_node("output/file_out")
class FileOutNode(BaseNode):
    NODE_NAME = "File Out"

    @staticmethod
    def get_attributes() -> Dict[str, Any]:
        return {
            "inputs": {"audio_in": "audio"},
            "outputs": {}
        }
    
    @staticmethod
    def get_parameters() -> Dict[str, Any]:
        return {"filename": "output.wav"}

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Computing FileOutNode {self.dpg_tag}")
        input_value = inputs.get("audio_in")
        
        if input_value is None:
            print(f"FileOutNode: No input received.")
            return {}

        try:
            if not isinstance(input_value, tuple) or len(input_value) != 2:
                print(f"FileOutNode: Error - Input must be a (array, rate) tuple.")
                return {}
                
            audio_array, sample_rate = input_value
            
            if not isinstance(audio_array, np.ndarray):
                print(f"FileOutNode: Error - Audio data is not a numpy array.")
                return {}

            if not isinstance(sample_rate, int):
                print(f"FileOutNode: Error - Sample rate is not an integer.")
                return {}

            filename = self.params.get("filename", "error.wav")
            
            write_wav(filename, sample_rate, audio_array.astype(np.float32))
            print(f"FileOutNode: Saved audio to {filename} with rate {sample_rate}")
        
        except Exception as e:
            print(f"FileOutNode: Failed to write file: {e}")

        return {}