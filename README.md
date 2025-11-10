# SIN
A minimal, asynchronous AI audio node editor.

## Core Architecture

This application is built on a non-blocking, event-driven architecture designed for heavy, asynchronous computation (like AI model inference) while maintaining a responsive user interface.

* **GUI (`main.py`):**
    * The UI is built with `dearpygui` using a static, non-floating layout.
    * A left-hand "Controls" panel contains global actions (e.g., "Process Graph") and a "Parameter View".
    * When a node is clicked in the editor, the "Parameter View" is dynamically populated with that node's specific controls.
    * A right-hand "Editor" panel contains the infinite node canvas.

* **Node Definitions (`nodes.py`):**
    * All nodes are defined in a central `NODE_REGISTRY`.
    * Each node inherits from `BaseNode` and cleanly separates its *connections* (`get_attributes`) from its *internal state* (`get_parameters`).

* **Graph Logic (`node_graph.py`):**
    * The `GraphManager` holds the logical state of all nodes and links, instantiating them from the `NODE_REGISTRY`.
    * When the "Process Graph" button is pressed, the manager performs a topological sort (Kahn's algorithm) to determine the correct node execution order.
    * It then packages this execution plan into a single task.

* **Asynchronous Engine (`audio_engine.py`):**
    * The `AudioEngine` runs a single, persistent worker thread.
    * The task from the `GraphManager` is sent to the `AudioEngine`'s `control_queue`.
    * The worker thread receives this task, executes the full graph computation in the correct order, and manages all data flow between nodes.

## Roadmap: First Model Run

Our architecture is now GUI-complete. The next steps focus on making the nodes functional and running our first AI model.

1.  **Implement `FileOutNode` (Audio Saving):**
    * Import `scipy.io.wavfile` and `numpy` in `nodes.py`.
    * Modify the `FileOutNode.compute` method to read its `audio_in` port.
    * It will expect to receive a tuple: `(audio_array, sample_rate)`.
    * It will read the `filename` parameter from `self.params`.
    * It will use `scipy.io.wavfile.write(filename, sample_rate, audio_array)` to save the file.

2.  **Create Test Signal in `AudioCraftNode`:**
    * Before implementing the full AI, we will test the data pipeline.
    * Modify `AudioCraftNode.compute` to generate a simple test signal.
    * It will create a 1-second, 440Hz sine wave as a `numpy` array.
    * It will set a sample rate (e.g., `44100`).
    * It will return `{"audio_out": (sine_array, 44100)}`.
    * **Goal:** Connect the `AudioCraftNode` to the `FileOutNode`, process the graph, and verify that a `.wav` file of a sine wave is created.

3.  **Implement `AudioCraftNode` Model Loading:**
    * Add `_model = None` as a class variable to `AudioCraftNode`.
    * Inside the `compute` method (which runs on the `AudioEngine`'s background thread), check if `_model is None`.
    * If it is, perform the one-time lazy-load:
        * `import torch`
        * `from audiocraft.models import MusicGen`
        * `_model = MusicGen.get_pretrained('facebook/audiocraft-small')`
    * This ensures the model loads asynchronously without freezing the GUI.

4.  **Implement `AudioCraftNode` Inference:**
    * After the model-loading check, the `compute` method will:
        * Get the `prompt` string from `self.params.get("prompt")`.
        * Set the model to generate (e.g., `_model.set_generation_params(duration=5)`).
        * Run inference: `wav_tensors = _model.generate(descriptions=[prompt])`.
        * Extract the audio data: `audio_array = wav_tensors[0].cpu().numpy()`.
        * Get the model's sample rate: `sample_rate = _model.sample_rate`.
        * Return the audio in the expected format: `{"audio_out": (audio_array, sample_rate)}`.

5.  **First Run:**
    * The application will be fully functional.
    * A user can add an `AudioCraftNode` and a `FileOutNode`.
    * Link the two nodes.
    * Click the `AudioCraftNode` to select it.
    * Type a prompt (e.g., "80s synth solo") into the "Parameter View" panel.
    * Click "Process Graph".
    * The application will generate the audio in the background and save it to `output.wav`.