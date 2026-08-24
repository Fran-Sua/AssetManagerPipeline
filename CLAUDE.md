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

## Common script pattern: modular pipeline nodes
The scripts in [`Modular_Pipeline/`](Modular_Pipeline/) are each meant to
run as one "Run Script" node in a Unity Asset Manager pipeline, chained
together rather than each doing a full import→process→export on their own.
They hand off scene state through a shared checkpoint file:

```python
TEMP_PIXYZ_FILE_DIR = "/workspace/temp"
TEMP_FILE_NAME = "resume.pxz"
TEMP_FILE = os.path.join(TEMP_PIXYZ_FILE_DIR, TEMP_FILE_NAME)
```

- `import.py` is the only node that imports a real external source file
  (path passed via pipeline command-line arguments); it writes the first
  `resume.pxz`.
- Every middle node (tessellate, merge/remove parts, make materials
  metallic, bake AO, …) loads `resume.pxz`, does one focused operation
  tuned via `--flag=value` command-line arguments, and saves back to
  `resume.pxz`.
- `export.py` is the only node that writes real external output files; it
  loads the final `resume.pxz` and exports it in one or more formats.

There is currently **no shared helper module** — `initPixyz()`,
`importTemporalPixyzScene()`, and `saveTempPixyzFile()` are duplicated
verbatim in every script. When adding a new node, copy this boilerplate
from an existing `Modular_Pipeline/` script rather than reinventing it.

See [`README.md`](README.md) for the full pipeline-usage explanation,
including how command-line arguments map to the Run Script node's config
field and a worked multi-node example.

## Scripts in this directory
- [`Modular_Pipeline/`](Modular_Pipeline/) — the actual pipeline nodes
  (`import.py`, `tessellation.py`, `mergeParts.py`,
  `removePartsByName.py`, `makeMaterialsMetallic.py`,
  `bakeAmbientOcclusionTexture.py`, `bakeAmbientOcclusionVertex.py`,
  `export.py`), all named in camelCase for consistency. See `README.md`
  for details on each.
- [`InitialTests/pixyzHelloWorld.py`](InitialTests/pixyzHelloWorld.py)
  — minimal session init/logging smoke test, no import/export. Good
  starting skeleton for a new script. Predates the modular pipeline
  pattern above and isn't wired into the `resume.pxz` convention.
- [`InitialTests/tessellationTest.py`](InitialTests/tessellationTest.py) —
  an earlier, non-modular prototype of what became
  `Modular_Pipeline/tessellation.py`.
