import abc
from typing import Any, Dict, Callable, List, Tuple

NODE_REGISTRY: Dict[str, 'BaseNode'] = {}

def register_node(name: str):
    def decorator(cls):
        NODE_REGISTRY[name] = cls
        return cls
    return decorator

class BaseNode(abc.ABC):
    NODE_NAME = "Base Node"
    
    def __init__(self, dpg_tag: int, input_attrs: Dict[str, int], output_attrs: Dict[str, int]):
        self.dpg_tag = dpg_tag
        self.input_attr_map = input_attrs
        self.output_attr_map = output_attrs

    @staticmethod
    @abc.abstractmethod
    def get_gui_definition() -> Tuple[Dict[str, Any], Dict[str, Any]]:
        pass

    @abc.abstractmethod
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pass

@register_node("generator/audiocraft")
class AudioCraftNode(BaseNode):
    NODE_NAME = "AudioCraft"

    @staticmethod
    def get_gui_definition() -> Tuple[Dict[str, Any], Dict[str, Any]]:
        inputs = {}
        outputs = {"audio_out": "audio"}
        return inputs, outputs

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Computing AudioCraftNode {self.dpg_tag}")
        prompt = "test prompt"
        return {"audio_out": f"audio_from_prompt: {prompt}"}

@register_node("output/file_out")
class FileOutNode(BaseNode):
    NODE_NAME = "File Out"

    @staticmethod
    def get_gui_definition() -> Tuple[Dict[str, Any], Dict[str, Any]]:
        inputs = {"audio_in": "audio"}
        outputs = {}
        return inputs, outputs

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Computing FileOutNode {self.dpg_tag}")
        input_value = inputs.get("audio_in")
        if input_value is not None:
            print(f"FileOutNode received: {input_value}")
        return {}