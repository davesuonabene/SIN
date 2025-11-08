import threading
import queue
import time

class AudioEngine:
    def __init__(self, results_queue):
        self.control_queue = queue.Queue()
        self.results_queue = results_queue
        self.worker_thread = None
        self.is_running = False

    def start(self):
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self.processing_loop)
        self.worker_thread.start()

    def stop(self):
        if not self.is_running:
            return
        
        self.is_running = False
        self.control_queue.put(None)
        if self.worker_thread:
            self.worker_thread.join()
        self.worker_thread = None

    def processing_loop(self):
        while self.is_running:
            try:
                task = self.control_queue.get(timeout=0.1)
                if task is None:
                    break
                
                print(f"AudioEngine: Received task: {task['type']}")
                
                if task['type'] == 'process_graph':
                    result = self.execute_graph_task(task)
                    self.results_queue.put(result)

            except queue.Empty:
                pass
        
        print("AudioEngine processing loop stopped.")

    def execute_graph_task(self, task):
        print("AudioEngine: --- Starting Graph Process ---")
        
        sorted_nodes = task['sorted_nodes']
        link_map = task['link_map']
        nodes_map = task['nodes_map']
        
        attribute_data_map = {}
        
        for node_tag in sorted_nodes:
            node = nodes_map[node_tag]
            
            inputs = {}
            for input_attr_tag in node.inputs:
                if input_attr_tag in link_map:
                    source_attr_tag = link_map[input_attr_tag]
                    inputs[input_attr_tag] = attribute_data_map.get(source_attr_tag)
                else:
                    inputs[input_attr_tag] = None
            
            try:
                outputs = node.compute(inputs)
                for output_attr_tag, value in outputs.items():
                    attribute_data_map[output_attr_tag] = value
            except Exception as e:
                print(f"AudioEngine: Error computing node {node_tag}: {e}")
                return f"Error: Node {node_tag} failed."

        print("AudioEngine: --- Graph Process Finished ---")
        return "Graph processing finished successfully."