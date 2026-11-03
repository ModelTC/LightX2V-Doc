import time
import uuid
from pathlib import Path

import requests

base_url = "http://localhost:8080"
response = requests.post(f"{base_url}/v1/tasks/video/", json={
    "prompt": "A cat walking on a sunny beach.",
    "negative_prompt": "blurry, low quality",
    "seed": 42,
    "size": [480, 832],
    "num_frames": 81,
    "save_result_path": f"quickstart_{uuid.uuid4().hex}.mp4",
}, timeout=30)
response.raise_for_status()
task_id = response.json()["task_id"]
print(f"Task: {task_id}", flush=True)

deadline = time.monotonic() + 1800
while time.monotonic() < deadline:
    response = requests.get(f"{base_url}/v1/tasks/{task_id}/status", timeout=30)
    response.raise_for_status()
    task = response.json()
    if task["status"] == "completed":
        break
    if task["status"] in {"failed", "cancelled"}:
        raise RuntimeError(f"{task['status']}: {task.get('error') or task_id}")
    print(task["status"], flush=True)
    time.sleep(2)
else:
    raise TimeoutError(f"Timed out waiting for task {task_id}; query its status before retrying.")

output = Path("save_results/first_video.mp4")
output.parent.mkdir(parents=True, exist_ok=True)
with requests.get(f"{base_url}/v1/tasks/{task_id}/result", stream=True, timeout=(10, 300)) as response:
    response.raise_for_status()
    with output.with_suffix(".mp4.part").open("wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            file.write(chunk)
output.with_suffix(".mp4.part").replace(output)
print(f"Saved to: {output.resolve()}")
