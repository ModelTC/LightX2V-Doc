# Interfaces and Integrations

Choose an interaction style, then follow the application's installation instructions. The LightX2V inference engine and these applications are maintained separately; check each application for supported models and dependencies.

| Goal | Entry point | Workflow |
| --- | --- | --- |
| Generate through a browser form | [Gradio-Lightx2v](https://github.com/ModelTC/Gradio-Lightx2v) | Install the separate Gradio app, configure models and start its web UI |
| Compose node workflows | [ComfyUI-Lightx2vWrapper](https://github.com/ModelTC/ComfyUI-Lightx2vWrapper) | Install the nodes in the ComfyUI environment and import a matching example workflow |
| Use a native Apple Silicon Mac application | [LightX2V APP](https://github.com/ModelTC/LightX2V-Mac-App) | Follow the app's installation and supported-model instructions |
| Build a client | [Service quickstart](../getting_started/index.md) | Start an HTTP service, submit requests and download results |

## Gradio { #gradio }

<a id="gradio-deployment-guide"></a>

For users who prefer forms for prompts, input files and generation results.

1. Check the [Gradio-Lightx2v installation instructions](https://github.com/ModelTC/Gradio-Lightx2v) for your system and target model.
2. Install its dependencies in the required environment and configure base weights and any matching quantized or distilled weights.
3. Run the application's startup command and open the address it prints.

The inference repository's former `app/` entry point has been removed. Installing LightX2V does not install Gradio.

## ComfyUI { #comfyui }

<a id="comfyui-deployment"></a>

### ComfyUI-Lightx2vWrapper

For existing ComfyUI users who want to combine generation with other processing nodes.

1. Install the plugin and dependencies using the [node repository's instructions](https://github.com/ModelTC/ComfyUI-Lightx2vWrapper), checking which Python environment ComfyUI uses.
2. Download weights matching the workflow and configure model paths in the nodes. Do not substitute a workflow for a different model unchanged.
3. Start from a supplied example workflow, then add supported LoRA, quantization or other optimization nodes.

Interfaces and nodes change with application versions. Report missing nodes, workflow imports and UI issues to the integration repository. Report inference issues reproducible in standalone LightX2V to [LightX2V Issues](https://github.com/ModelTC/LightX2V/issues).
