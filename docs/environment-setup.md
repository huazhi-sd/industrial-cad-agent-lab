# Environment Setup

This page records the public setup pattern for the local CAD-agent lab. It intentionally avoids private paths, API keys, and company files.

## Core tools

- Python 3.12 for local scripts and build123d/CadQuery-style generation.
- FreeCAD 1.1.x for STEP inspection and FreeCAD MCP experiments.
- CAD Viewer for quick local STEP review.
- GitHub for public logs, issues, and reproducible contribution notes.

## Python packages

Install the repository dependencies:

```powershell
python -m pip install -r requirements.txt
```

For tool-specific experiments, prefer isolated environments or `uv` where possible.

## FreeCAD STEP inspection

Use FreeCAD's bundled Python when direct `FreeCADCmd.exe` execution is unreliable:

```powershell
& "D:\Program Files\FreeCAD 1.1\bin\python.exe" `
  "<repo>\tools\freecad\inspect_step.py" `
  "<input.step>" `
  --json "<output.json>" `
  --md "<output.md>"
```

## Public logging policy

- Public logs are written in English.
- Chinese/raw working notes stay in a local private archive.
- Logs should record evidence, commands, results, limitations, and follow-up actions.

