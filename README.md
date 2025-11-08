# SIN
A minimal, asynchronous AI audio node editor.

## Core Architecture

This application is built on a non-blocking, event-driven architecture designed for heavy, asynchronous computation (like AI model inference) while maintaining a responsive user interface.

* **GUI (`main.py`):**
    * The UI is built with `dearpygui`.
    * The node editor uses event callbacks (`link_callback`, `delink_callback`) for all link management. There is no polling.
    * The main GUI thread is responsible *only* for user interaction and dispatching tasks. It performs no computation.

* **Graph Logic (`node_graph.py`):**
    * The `GraphManager` holds the logical state of all nodes and links.
    * When the "Process Graph" button is pressed, the manager performs a topological sort (Kahn's algorithm) to determine the correct node execution order.
    * It then packages this execution plan (the sorted list of nodes and link data) into a single task.

* **Asynchronous Engine (`audio_engine.py`):**
    * The `AudioEngine` runs a single, persistent worker thread.
    * The task from the `GraphManager` is sent to the `AudioEngine`'s `control_queue`.
    * The worker thread receives this task, executes the full graph computation in the correct order, and manages all data flow between nodes.
    * This ensures that AI inference or audio processing does *not* block the GUI.

## Roadmap

The current foundation supports asynchronous, graph-based computation. The next steps are to build functional nodes and integrate real-time processing.

1.  **Specialized Node Implementation:**
    * Create `ModelNode`: A node to hold AI model instructions (e.g., text prompts, settings) and eventually run AudioCraft inference.
    * Create `AudioOutputNode`: A node to receive audio data (as a `numpy` array) and render it to a file.

2.  **GUI Node Selection:**
    * Implement a minimal UI mechanism (e.g., a right-click context menu) to allow the user to add specific node types (`ModelNode`, `AudioOutputNode`) to the editor.

3.  **AI & Audio Integration:**
    * Integrate `audiocraft` (and `torch`) into the `ModelNode`'s `compute` method.
    * Use `scipy.io.wavfile` in the `AudioOutputNode`'s `compute` method to save the resulting audio buffer.

4.  **Real-Time Audio:**
    * Refactor the `AudioEngine` to support a real-time `sounddevice` stream.
    * This will involve processing the graph repeatedly on small audio buffers, evolving from the current "bulk generation" model to a live processing one.