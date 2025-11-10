import dearpygui.dearpygui as dpg
from audio_engine import AudioEngine
from node_graph import GraphManager
from nodes import NODE_REGISTRY
import queue
from theme import apply_theme

def show_node_context_menu(sender, app_data, user_data):
    try:
        if dpg.is_item_hovered("Node Editor"):
            mouse_x, mouse_y = dpg.get_mouse_pos(local=False)
            dpg.set_item_pos("Node Context Menu", [int(mouse_x), int(mouse_y)])
            dpg.configure_item("Node Context Menu", show=True)
    except Exception as e:
        print(f"GUI: Failed to show node context menu: {e}")

def hide_node_context_menu(sender, app_data, user_data):
    try:
        if dpg.is_item_shown("Node Context Menu") and not dpg.is_item_hovered("Node Context Menu"):
            dpg.configure_item("Node Context Menu", show=False)
    except Exception:
        pass

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

def _parameter_changed_callback(sender, app_data, user_data):
    node = user_data["node"]
    param_name = user_data["param_name"]
    node.params[param_name] = app_data

def _node_selected_callback(sender, app_data, user_data):
    node_object = user_data
    dpg.delete_item("Parameter View", children_only=True)

    if not node_object:
        return

    dpg.add_text(f"Node: {node_object.NODE_NAME}", parent="Parameter View")
    
    for param_name, default_value in node_object.params.items():
        dpg.add_text(param_name, wrap=-1, parent="Parameter View")
        dpg.add_input_text(
            default_value=default_value,
            width=-1,
            callback=_parameter_changed_callback,
            user_data={"node": node_object, "param_name": param_name},
            parent="Parameter View"
        )

def add_node_callback(sender, app_data, user_data):
    node_type = user_data
    if not node_type or node_type not in NODE_REGISTRY:
        return

    node_tag = dpg.generate_uuid()
    node_object = graph_manager.add_node(node_type, node_tag)
    
    if not node_object:
        print(f"GUI: Error: Could not create node of type {node_type}")
        return
        
    attr_def = node_object.get_attributes()
    inputs_def = attr_def.get("inputs", {})
    outputs_def = attr_def.get("outputs", {})

    with dpg.node(label=node_object.NODE_NAME, tag=node_tag, parent="Node Editor"):
        
        for input_name, input_type_str in inputs_def.items():
            attr_tag = dpg.generate_uuid()
            node_object.input_attr_map[input_name] = attr_tag
            
            with dpg.node_attribute(label=input_name, tag=attr_tag, attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text(input_type_str)

        for output_name, output_type_str in outputs_def.items():
            attr_tag = dpg.generate_uuid()
            node_object.output_attr_map[output_name] = attr_tag
            
            with dpg.node_attribute(label=output_name, tag=attr_tag, attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_text(output_type_str)
    
    with dpg.item_handler_registry() as node_handler:
        dpg.add_item_clicked_handler(callback=_node_selected_callback, user_data=node_object)
    
    dpg.bind_item_handler_registry(node_tag, node_handler)
    
    dpg.configure_item("Node Context Menu", show=False)

def delete_node_callback():
    print("GUI: Delete key pressed.")
    
    selected_nodes = dpg.get_selected_nodes("Node Editor")
    
    if selected_nodes:
        dpg.delete_item("Parameter View", children_only=True)

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

with dpg.window(tag="Primary Window", no_title_bar=True, no_close=True, no_move=True):
    with dpg.group(horizontal=True):
        with dpg.child_window(width=300):
            dpg.add_text("SIN // Minimal Audio Architect")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start Engine", callback=start_engine_callback)
                dpg.add_button(label="Stop Engine", callback=stop_engine_callback)
            dpg.add_button(label="Process Graph", callback=process_graph_callback)
            dpg.add_text("Ready", tag="status_text")
            
            dpg.add_separator()
            dpg.add_text("Parameters")
            with dpg.group(tag="Parameter View"):
                pass
        
        with dpg.child_window(width=-1):
            with dpg.node_editor(tag="Node Editor", callback=link_callback, delink_callback=delink_callback):
                pass

with dpg.window(tag="Node Context Menu", no_title_bar=True, no_resize=True, no_move=True, no_scrollbar=True, modal=False, show=False):
    for node_type_name, node_class in NODE_REGISTRY.items():
        dpg.add_menu_item(
            label=f"Add: {node_class.NODE_NAME}",
            callback=add_node_callback,
            user_data=node_type_name
        )
    dpg.add_separator()
    dpg.add_menu_item(label="Close", callback=lambda: dpg.configure_item("Node Context Menu", show=False))

dpg.create_viewport(title='SIN', width=1280, height=720)
dpg.setup_dearpygui()
apply_theme()

dpg.set_primary_window("Primary Window", True)

with dpg.handler_registry(tag="Global Key Handler"):
    dpg.add_key_press_handler(key=dpg.mvKey_Delete, callback=delete_node_callback)

with dpg.handler_registry(tag="Global Mouse Handler"):
    dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left, callback=hide_node_context_menu)
    dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Right, callback=show_node_context_menu)

dpg.show_viewport()

dpg.set_exit_callback(stop_engine_callback)

while dpg.is_dearpygui_running():
    try:
        result = results_queue.get(block=False)
        print(f"GUI: Received result {result}")
        dpg.set_value("status_text", result)
    except queue.Empty:
        pass
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()