# Cloud_Demo — Pixyz scripts for Unity Asset Manager pipelines

## What this project is
A collection of Python scripts written against the **Pixyz SDK** (now rebranded
by Unity as the **"Unity Asset Transformer SDK"**), intended to run as processing
steps inside **Unity Asset Manager** pipelines. Scripts import a source 3D/CAD
file, run one or more Pixyz operations on it, and export the processed result.

- **SDK version:** v2026.3.1.1
- **Python module:** `pxz` (unchanged from the Pixyz-branded SDK — function names
  and module layout carry over 1:1 to the Unity-branded build)
- **Docs root:** https://docs.unity.com/en-us/asset-transformer-sdk/2026.1/
  - Manual: `.../manual/functions/<topic>`
  - Python API reference: `.../api/python/<module>_functions`

## Common script pattern
Every script follows roughly the same shape:

```python
import pxz
from pxz import core, scene, io, algo

if pxz.get_current_session() == None:
    pxz.initialize()

print(f'Pixyz version: {core.getVersion()}')
core.configureInterfaceLogger(True, True, True)
core.addConsoleVerbose(core.Verbose.INFO)

root = io.importScene(input_file)
# ... processing ...
io.exportScene(output_file, root)

pxz.release()
```


## Scripts in this directory
- **`Pixyz_Hello_World.py`** — minimal session init/logging smoke test, no
  import/export. Good starting skeleton for a new script.
