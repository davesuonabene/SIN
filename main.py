import dearpygui.dearpygui as dpg
from audio_engine import AudioEngine
from node_graph import GraphManager
import queue

def start_engine_callback():
    print("GUI: Starting engine...")
    audio_engine.start()

def stop_engine_callback():
    print("GUI: Stopping engine...")
    audio_engine.stop()

def process_graph_callback():
    message = "--- GUI: Processing Graph ---"
    print(message)
    dpg.set_value("status_text", message)
    graph_manager.process_graph()

def link_callback(sender, app_data):
    attr_out = app_data[0]
    attr_in = app_data[1]
    
    link_tag = dpg.add_node_link(attr_out, attr_in, parent=sender)
    print(f"GUI: Link created via callback: {link_tag}")
    graph_manager.on_link_added(link_tag, attr_out, attr_in)

def delink_callback(sender, app_data):
    link_tag = app_data
    print(f"GUI: Link deleted via callback: {link_tag}")
    dpg.delete_item(link_tag)
    graph_manager.on_link_removed(link_tag)

def add_node_callback():
    node_tag = dpg.generate_uuid()
    attr_in_tag = dpg.generate_uuid()
    attr_out_tag = dpg.generate_uuid()

    dpg.add_node(label="New Node", tag=node_tag, parent="Node Editor", pos=[200, 200])
    
    dpg.add_node_attribute(label="Input", tag=attr_in_tag, attribute_type=dpg.mvNode_Attr_Input, parent=node_tag)
    dpg.add_text("Input", parent=attr_in_tag)
    
    dpg.add_node_attribute(label="Output", tag=attr_out_tag, attribute_type=dpg.mvNode_Attr_Output, parent=node_tag)
    dpg.add_text("Output", parent=attr_out_tag)
    
    graph_manager.add_node(
        "BaseNode", 
        node_tag, 
        input_attrs=[attr_in_tag], 
        output_attrs=[attr_out_tag]
    )

def delete_node_callback():
    print("GUI: Delete key pressed.")
    
    selected_nodes = dpg.get_selected_nodes("Node Editor")
    for node_tag in selected_nodes:
        print(f"GUI: Deleting node {node_tag}")
        
        all_attributes = []
        node_children = dpg.get_item_children(node_tag, 1)
        if node_children:
            all_attributes = node_children

        links_to_delete = graph_manager.find_links_for_attributes(all_attributes)
        
        for link_tag in links_to_delete:
            print(f"GUI: Removing associated link {link_tag}")
            dpg.delete_item(link_tag)
            graph_manager.on_link_removed(link_tag)

        dpg.delete_item(node_tag)
        graph_manager.remove_node(node_tag)

    selected_links = dpg.get_selected_links("Node Editor")
    for link_tag in selected_links:
        print(f"GUI: Deleting link {link_tag}")
        dpg.delete_item(link_tag)
        graph_manager.on_link_removed(link_tag)

results_queue = queue.Queue()
audio_engine = AudioEngine(results_queue)
graph_manager = GraphManager(audio_engine)

dpg.create_context()

with dpg.window(label="SIN Workspace", tag="Primary Window", width=400, height=200):
    dpg.add_text("SIN // Minimal Audio Architect")
    
    with dpg.group(horizontal=True):
        dpg.add_button(label="Start Engine", callback=start_engine_callback)
        dpg.add_button(label="Stop Engine", callback=stop_engine_callback)
    
    dpg.add_button(label="Process Graph", callback=process_graph_callback)
    dpg.add_button(label="Add Node", callback=add_node_callback)
    dpg.add_text("Ready", tag="status_text")

with dpg.window(label="Node Editor", tag="Node Editor Window"):
    with dpg.node_editor(tag="Node Editor", callback=link_callback, delink_callback=delink_callback):
        
        node_1_tag = "node_1"
        node_1_attr_in = "attr_1_in"
        node_1_attr_out = "attr_1_out"
        with dpg.node(label="Input Node", tag=node_1_tag, pos=[100, 100]):
            with dpg.node_attribute(label="Input Attr", tag=node_1_attr_in, attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text("Input")
            with dpg.node_attribute(label="Output Attr", tag=node_1_attr_out, attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_text("Output")
        
        graph_manager.add_node(
            "BaseNode", 
            node_1_tag, 
            input_attrs=[node_1_attr_in], 
            output_attrs=[node_1_attr_out]
        )

        node_2_tag = "node_2"
        node_2_attr_in = "attr_2_in"
        with dpg.node(label="Output Node", tag=node_2_tag, pos=[400, 100]):
            with dpg.node_attribute(label="Input Attr", tag=node_2_attr_in, attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text("Input")
        
        graph_manager.add_node(
            "BaseNode", 
            node_2_tag, 
            input_attrs=[node_2_attr_in], 
            output_attrs=[]
        )

        link_tag = dpg.add_node_link(node_1_attr_out, node_2_attr_in, tag="link_1")
        graph_manager.on_link_added(link_tag, node_1_attr_out, node_2_attr_in)

dpg.create_viewport(title='SIN', width=1280, height=720)
dpg.setup_dearpygui()

with dpg.handler_registry(tag="Global Key Handler"):
    dpg.add_key_press_handler(key=dpg.mvKey_Delete, callback=delete_node_callback)

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