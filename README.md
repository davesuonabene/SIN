# SIN
A Minimal, Offline Audio Node Editor

## Core Architecture

This application uses a node-based graph to define an audio processing chain. The graph is processed offline.

* **GUI (`main.py`):** A `dearpygui` interface for building the node graph.
* **Graph Logic (`node_graph.py`):** The `GraphManager` performs a topological sort to create an execution plan.
* **Asynchronous Engine (`audio_engine.py`):** An `AudioEngine` worker thread receives the plan and executes the full graph computation.

## Roadmap: First Beat

The immediate goal is to create a simple, two-track beat by loading and merging two audio samples.

1.  **Refactor (Cleanup):**
    * Remove `audiocraft_server.py` from the project.
    * Remove the `AudioCraftNode` from `nodes.py`.
    * Remove the AudioCraft server start/stop buttons and status text from `main.py`.

2.  **Implement `SampleLoaderNode`:**
    * We will use `librosa` (from our approved stack) for this.
    * Create a new node, `generator/sample_loader`, in `nodes.py`.
    * It will have one parameter: `filepath`.
    * Its `compute` method will use `librosa.load(self.params['filepath'], sr=None)` to load an audio file.
    * It will return `{"audio_out": (audio_array, sample_rate)}`.

3.  **Implement `MixerNode`:**
    * Create a new node, `utility/mixer`, in `nodes.py`.
    * It will have two inputs: `audio_in_1` and `audio_in_2`.
    * Its `compute` method will receive two `(array, rate)` tuples. It must verify the sample rates match.
    * It will sum the `numpy` arrays. We will assume arrays are the same length for the minimal implementation.
    * It will return `{"audio_out": (mixed_array, sample_rate)}`.

4.  **First Run:**
    * A user can add two `SampleLoaderNode`s and one `MixerNode`.
    * Add a `FileOutNode`.
    * Link: `SampleLoaderNode` -> `MixerNode` (input 1), `SampleLoaderNode` -> `MixerNode` (input 2), `MixerNode` -> `FileOutNode`.
    * Set the filepaths for the two sample loaders in the "Parameter View".
    * Click "Process Graph".
    * The application will generate an `output.wav` containing the mixed beat.