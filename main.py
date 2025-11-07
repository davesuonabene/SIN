import dearpygui.dearpygui as dpg
from audio_engine import AudioEngine
import queue

def start_engine_callback():
    print("GUI: Starting engine...")
    audio_engine.start()

def stop_engine_callback():
    print("GUI: Stopping engine...")
    audio_engine.stop()

def send_test_message():
    message = "Test Task From GUI"
    print(f"GUI: Sending: {message}")
    dpg.set_value("status_text", f"Sending: {message}")
    audio_engine.control_queue.put(message)

results_queue = queue.Queue()
audio_engine = AudioEngine(results_queue)

dpg.create_context()

with dpg.window(label="SIN Workspace", tag="Primary Window", width=400, height=200):
    dpg.add_text("SIN // Minimal Audio Architect")
    
    with dpg.group(horizontal=True):
        dpg.add_button(label="Start Engine", callback=start_engine_callback)
        dpg.add_button(label="Stop Engine", callback=stop_engine_callback)
    
    dpg.add_button(label="Send Test Message", callback=send_test_message)
    dpg.add_text("Ready", tag="status_text")

with dpg.window(label="Node Editor", tag="Node Editor Window"):
    with dpg.node_editor(tag="Node Editor"):
        with dpg.node(label="Input Node", tag="node_1", pos=[100, 100]):
            with dpg.node_attribute(label="Input Attr", tag="attr_1_in", attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text("Input")
            
            with dpg.node_attribute(label="Output Attr", tag="attr_1_out", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_text("Output")

        with dpg.node(label="Output Node", tag="node_2", pos=[400, 100]):
            with dpg.node_attribute(label="Input Attr", tag="attr_2_in", attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text("Input")
        
        dpg.add_node_link("attr_1_out", "attr_2_in", tag="link_1")

dpg.create_viewport(title='SIN', width=1280, height=720)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)

dpg.set_exit_callback(stop_engine_callback)

while dpg.is_dearpygui_running():
    try:
        result = results_queue.get(block=False)
        print(f"GUI: Received result: {result}")
        dpg.set_value("status_text", result)
    except queue.Empty:
        pass
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()