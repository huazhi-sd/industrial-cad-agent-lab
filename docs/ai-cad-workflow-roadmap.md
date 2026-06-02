# AI CAD Workflow Roadmap

This repository is a public lab for industrial CAD agent workflows. The core direction is not a single CAD platform. The goal is to make agent-driven industrial product design more reliable through STEP-first geometry, parametric source files, validation scripts, and reproducible review images.

## Current focus

- Build small public CAD examples that can be shared without company-sensitive data.
- Convert repeated CAD mistakes into written contracts and executable validators.
- Compare early CAD agent tools such as text-to-CAD skills, AgentCAD, build123d MCP, FreeCAD MCP, kernelCAD, and Onshape API/MCP experiments.
- Keep browser UI automation as a secondary path. Prefer structured APIs, local scripts, STEP inspection, and deterministic outputs.

## Near-term projects

- mATX case datum assembly: motherboard tray, motherboard datum, GPU datum, and compatibility checks.
- STEP inspection wrappers for FreeCAD and other CAD runtimes.
- Small mechanical examples that expose real agent failure modes, such as handedness, view conventions, assembly part count, and feature-plane validation.

## Long-term direction

- A higher-fidelity PC case workflow with compatibility checks for motherboard, GPU, PSU, CPU cooler, storage, and airflow.
- Cooling equipment and liquid-cooling infrastructure research as a longer-term engineering track.
- Public contributions to early AI + CAD tools when Windows, STEP, validation, or workflow issues are reproducible.

## Repository policy

- Public documents and logs are English by default.
- Chinese/raw notes are archived locally and are not committed.
- Company CAD files, supplier drawings, API keys, and private engineering details are not committed.
