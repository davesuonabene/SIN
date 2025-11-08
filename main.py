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

# Track known links to detect new ones (link_callback not supported in dearpygui 2.1.0)
known_links = {"link_1"}

def delink_callback(sender, app_data):
    """Called when a link is deleted. app_data is the link tag."""
    global known_links
    print(f"GUI: Link deleted via callback: {app_data}")
    # Don't delete the item here - dearpygui handles it
    # Just update our tracking
    known_links.discard(str(app_data))
    graph_manager.on_link_removed(app_data)

def add_node_callback():
    node_tag = dpg.generate_uuid()
    attr_in_tag = dpg.generate_uuid()
    attr_out_tag = dpg.generate_uuid()

    dpg.add_node(label="New Node", tag=node_tag, parent="Node Editor", pos=[200, 200])
    
    dpg.add_node_attribute(label="Input", tag=attr_in_tag, attribute_type=dpg.mvNode_Attr_Input, parent=node_tag)
    dpg.add_text("Input", parent=attr_in_tag)
    
    dpg.add_node_attribute(label="Output", tag=attr_out_tag, attribute_type=dpg.mvNode_Attr_Output, parent=node_tag)
    dpg.add_text("Output", parent=attr_out_tag)
    
    graph_manager.add_node("BaseNode", node_tag)

def delete_node_callback():
    print("GUI: Delete key pressed.")
    
    selected_nodes = dpg.get_selected_nodes("Node Editor")
    for node_tag in selected_nodes:
        print(f"GUI: Deleting node {node_tag}")
        
        all_attributes = []
        if dpg.get_item_children(node_tag, 1):
            all_attributes = dpg.get_item_children(node_tag, 1)

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
    with dpg.node_editor(tag="Node Editor", delink_callback=delink_callback):
        
        with dpg.node(label="Input Node", tag="node_1", pos=[100, 100]):
            with dpg.node_attribute(label="Input Attr", tag="attr_1_in", attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text("Input")
            with dpg.node_attribute(label="Output Attr", tag="attr_1_out", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_text("Output")
        
        graph_manager.add_node("BaseNode", "node_1")

        with dpg.node(label="Output Node", tag="node_2", pos=[400, 100]):
            with dpg.node_attribute(label="Input Attr", tag="attr_2_in", attribute_type=dpg.mvNode_Attr_Input):
                dpg.add_text("Input")
        
        graph_manager.add_node("BaseNode", "node_2")

        link_tag = dpg.add_node_link("attr_1_out", "attr_2_in", tag="link_1")
        graph_manager.on_link_added(link_tag, "attr_1_out", "attr_2_in")

dpg.create_viewport(title='SIN', width=1280, height=720)
dpg.setup_dearpygui()

with dpg.handler_registry(tag="Global Key Handler"):
    dpg.add_key_press_handler(key=dpg.mvKey_Delete, callback=delete_node_callback)

dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)

def detect_new_links():
    """Poll for new links and register them with the graph manager."""
    global known_links
    try:
        # Get links from slot 1 (links are stored in slot 1 of node editor)
        children = dpg.get_item_children("Node Editor", slot=1)
        
        # Handle both list and tuple formats
        if isinstance(children, tuple):
            links = list(children) if children else []
        elif isinstance(children, list):
            links = children
        else:
            links = [children] if children else []
        
        if not links:
            return
        
        # Convert all link tags to strings for consistent comparison
        # Also filter out links that don't exist (temporary drag links)
        valid_links = []
        for link in links:
            if link:
                link_str = str(link)
                if dpg.does_item_exist(link):
                    valid_links.append(link_str)
        
        current_links = set(valid_links)
        new_links = current_links - known_links
        
        # Only process truly new links (avoid spam)
        if not new_links:
            # Clean up deleted links from tracking
            known_links &= current_links
            return
        
        for link_tag in new_links:
            try:
                # Double-check it still exists (might have been deleted between checks)
                if not dpg.does_item_exist(link_tag):
                    # Mark as known even if it doesn't exist to avoid spam
                    known_links.add(link_tag)
                    continue
                    
                config = dpg.get_item_configuration(link_tag)
                if not config:
                    # Mark as known even without config to avoid spam
                    known_links.add(link_tag)
                    continue
                
                # Get link endpoints - check all possible key names
                attr_1 = config.get("attr_1") or config.get("attr1") or config.get("source")
                attr_2 = config.get("attr_2") or config.get("attr2") or config.get("destination")
                
                if attr_1 and attr_2:
                    if dpg.does_item_exist(attr_1) and dpg.does_item_exist(attr_2):
                        print(f"GUI: ✓ Detected new link {link_tag}: {attr_1} -> {attr_2}")
                        graph_manager.on_link_added(link_tag, attr_1, attr_2)
                        known_links.add(link_tag)
                    else:
                        print(f"GUI: Link {link_tag} has invalid attributes: {attr_1}, {attr_2}")
                        # Still mark as known to avoid spam
                        known_links.add(link_tag)
                else:
                    # Debug: show what keys are available (only once per link)
                    if link_tag not in known_links:
                        print(f"GUI: Link {link_tag} missing endpoints. Config keys: {list(config.keys())}")
                        print(f"GUI: Full config: {config}")
                    # Mark as known to avoid spam
                    known_links.add(link_tag)
            except Exception as e:
                print(f"GUI: Error processing link {link_tag}: {e}")
                # Mark as known even on error to avoid spam
                known_links.add(link_tag)
        
        # Clean up deleted links from tracking
        known_links &= current_links
    except Exception as e:
        # Silently fail to avoid spam in normal operation
        pass

dpg.set_exit_callback(stop_engine_callback)

while dpg.is_dearpygui_running():
    try:
        result = results_queue.get(block=False)
        print(f"GUI: Received result: {result}")
        dpg.set_value("status_text", result)
    except queue.Empty:
        pass
    
    detect_new_links()
    dpg.render_dearpygui_frame()

dpg.destroy_context()