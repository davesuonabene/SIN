# SIN
A minimal, asynchronous AI audio node editor.

## Core Architecture

This application is built on a non-blocking, event-driven architecture designed for heavy, asynchronous computation (like AI model inference) while maintaining a responsive user interface.

* **GUI (`main.py`):**
    * The UI is built with `dearpygui`.
    * A right-click context menu in the node editor dynamically adds nodes from a central registry.
    * The main GUI thread is responsible *only* for user interaction and dispatching tasks. It performs no computation.

* **Node Definitions (`nodes.py`):**
    * All nodes are defined in a central `NODE_REGISTRY`.
    * Each node inherits from `BaseNode` and defines its GUI and compute logic.

* **Graph Logic (`node_graph.py`):**
    * The `GraphManager` holds the logical state of all nodes and links, instantiating them from the `NODE_REGISTRY`.
    * When the "Process Graph" button is pressed, the manager performs a topological sort (Kahn's algorithm) to determine the correct node execution order.
    * It then packages this execution plan into a single task.

* **Asynchronous Engine (`audio_engine.py`):**
    * The `AudioEngine` runs a single, persistent worker thread.
    * The task from the `GraphManager` is sent to the `AudioEngine`'s `control_queue`.
    * The worker thread receives this task, executes the full graph computation in the correct order, and manages all data flow between nodes.

## Roadmap

1.  **Node Parameter GUI:** Add GUI elements (e.g., text inputs) to the node definitions to control their internal parameters (e.g., the `prompt` for `AudioCraftNode`).

2.  **Specialized Node Implementation:**
    * Integrate `scipy.io.wavfile` into `FileOutNode` to save incoming `numpy` arrays.
    * Integrate `audiocraft` into `AudioCraftNode` to generate audio from its `prompt` parameter.

3.  **Real-Time Audio:**
    * Refactor the `AudioEngine` to support a real-time `sounddevice` stream.
    * This will involve processing the graph repeatedly on small audio buffers, evolving from the current "bulk generation" model to a live processing one.