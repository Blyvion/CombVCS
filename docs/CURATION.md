# Publication scope

The repository was assembled using an explicit file selection from the original project. The original working directory and its staged files were left intact.

## Included

- Current Vue source, public assets, package manifest/lockfile, build configuration, and optional static server.
- Flask API, effect inference script, and the HTML template used by the player.
- Custom move detector configurations and labels. Both label locations are retained because the Darknet metadata resolves `data/obj.names` from the backend working directory.
- Two training notebooks, with code/markdown preserved and outputs/execution counts removed. The effect notebook uses the more complete Downloads training variant rather than the capstone variant that attempts to load an existing model.
- Documentation, an inferred Python dependency baseline, ignore rules, and runtime directory placeholders.

## Excluded

| Original material | Reason |
| --- | --- |
| CUDA/cuDNN, NVIDIA, Anaconda installers and downloaded wheels | Machine setup downloads, not application source |
| Detector weights, SavedModel directories, serialized encoders | Binary runtime artifacts; supplied separately |
| Gameplay videos, frame images, annotation datasets and archives | Bulky training/demo inputs; redistribution not established |
| Vendored Darknet source, binaries, object files, sample assets | Upstream dependency; only project configuration is retained |
| `dist/`, caches, checkpoint notebooks, nested `.git/` directories | Generated output or local metadata |
| `src_old/`, copied templates, duplicate notebooks, scratch JSON/logs | Superseded experiments or generated results |
| Saved timestamps and generated inference JSON | Runtime output tied to excluded videos |

No bulk `git add` was run in the original directory. Its pre-existing staged models and video were not included in this publication. The repository history used for publication begins with the existing remote README commit, followed by the curated project commit.

## Small source changes

- Replace original deployment IPs with loopback addresses for local use.
- Allow Flask bind host/port overrides through environment variables.
- Show only MP4 names in `/listvideos` rather than including `.gitkeep`.
- Normalize trailing whitespace in source/configuration files.
- Remove stale query results from the checked-in player template.

No model performance results, individual contribution claims, or project license were invented.
