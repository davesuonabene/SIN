class BaseNode:
    def __init__(self, dpg_tag):
        self.dpg_tag = dpg_tag
        self.inputs = {}
        self.outputs = {}

    def compute(self, control_queue):
        print(f"Computing node {self.dpg_tag}...")
        
        task = {
            "type": "compute",
            "node_tag": self.dpg_tag
        }
        
        control_queue.put(task)

class GraphManager:
    def __init__(self, audio_engine):
        self.nodes = {}
        self.links = {}
        self.audio_engine = audio_engine

    def add_node(self, node_type, dpg_tag):
        print(f"GraphManager: Adding node {dpg_tag} of type {node_type}")
        if node_type == "BaseNode":
            new_node = BaseNode(dpg_tag=dpg_tag)
            self.nodes[dpg_tag] = new_node
        else:
            print(f"GraphManager: Unknown node type {node_type}")

    def remove_node(self, node_tag):
        if node_tag in self.nodes:
            print(f"GraphManager: Removing node {node_tag}")
            del self.nodes[node_tag]
        else:
            print(f"GraphManager: Warning: Node {node_tag} not found in manager.")

    def on_link_added(self, link_tag, attr_out, attr_in):
        print(f"GraphManager: Storing link {link_tag}: {attr_out} -> {attr_in}")
        self.links[link_tag] = (attr_out, attr_in)

    def on_link_removed(self, link_tag):
        print(f"GraphManager: Removing link {link_tag}")
        self.links.pop(link_tag, None)

    def find_links_for_attributes(self, attributes):
        links_to_remove = []
        for link_tag, (attr_out, attr_in) in self.links.items():
            if attr_out in attributes or attr_in in attributes:
                links_to_remove.append(link_tag)
        return links_to_remove

    def process_graph(self):
        print("GraphManager: --- Starting Graph Process ---")
        
        for dpg_tag, node in self.nodes.items():
            node.compute(self.audio_engine.control_queue)
        
        print("GraphManager: --- Graph Process Submitted ---")