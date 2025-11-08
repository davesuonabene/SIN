from collections import deque

class BaseNode:
    def __init__(self, dpg_tag, input_attrs=None, output_attrs=None):
        self.dpg_tag = dpg_tag
        self.inputs = {tag: None for tag in (input_attrs or [])}
        self.outputs = {tag: None for tag in (output_attrs or [])}

    def compute(self, inputs):
        print(f"Computing node {self.dpg_tag} with inputs: {inputs}")
        
        output_value = 1.0 
        
        if self.inputs:
            try:
                first_input_key = list(self.inputs.keys())[0]
                input_value = inputs.get(first_input_key)
                if input_value is not None:
                    output_value = input_value
            except Exception:
                pass
        
        outputs = {}
        for output_key in self.outputs:
            outputs[output_key] = output_value
        
        print(f"Node {self.dpg_tag} produced outputs: {outputs}")
        return outputs

class GraphManager:
    def __init__(self, audio_engine):
        self.nodes = {}
        self.links = {}
        self.audio_engine = audio_engine

    def add_node(self, node_type, dpg_tag, input_attrs=None, output_attrs=None):
        print(f"GraphManager: Adding node {dpg_tag} of type {node_type}")
        if node_type == "BaseNode":
            new_node = BaseNode(
                dpg_tag=dpg_tag, 
                input_attrs=input_attrs, 
                output_attrs=output_attrs
            )
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
        print("GraphManager: --- Preparing Graph Process Task ---")
        
        node_lookup_by_attr = {}
        for node_tag, node in self.nodes.items():
            for attr in node.inputs:
                node_lookup_by_attr[attr] = node_tag
            for attr in node.outputs:
                node_lookup_by_attr[attr] = node_tag
        
        adj = {node_tag: [] for node_tag in self.nodes}
        in_degree = {node_tag: 0 for node_tag in self.nodes}
        
        link_map = {}

        for attr_out, attr_in in self.links.values():
            if attr_out in node_lookup_by_attr and attr_in in node_lookup_by_attr:
                source_node = node_lookup_by_attr[attr_out]
                dest_node = node_lookup_by_attr[attr_in]
                
                if dest_node not in adj[source_node]:
                    adj[source_node].append(dest_node)
                    in_degree[dest_node] += 1
                
                link_map[attr_in] = attr_out
            
        queue = deque([node_tag for node_tag in self.nodes if in_degree[node_tag] == 0])
        sorted_nodes = []
        
        while queue:
            node_tag = queue.popleft()
            sorted_nodes.append(node_tag)
            
            for neighbor in adj[node_tag]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(sorted_nodes) != len(self.nodes):
            print("GraphManager: Error: Cycle detected in graph. Process aborted.")
            return

        print(f"GraphManager: Submitting task for execution order: {sorted_nodes}")
        
        task = {
            'type': 'process_graph',
            'sorted_nodes': sorted_nodes,
            'link_map': link_map,
            'nodes_map': self.nodes
        }
        
        self.audio_engine.control_queue.put(task)
        
        print("GraphManager: --- Graph Process Submitted ---")