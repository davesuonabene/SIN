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
                message = self.control_queue.get(timeout=0.1)
                if message is None:
                    break
                
                print(f"AudioEngine received: {message}")
                
                print("AudioEngine: Starting long task...")
                time.sleep(2)
                print("AudioEngine: Long task finished.")
                
                result = f"Finished processing: {message}"
                self.results_queue.put(result)

            except queue.Empty:
                pass
        
        print("AudioEngine processing loop stopped.")