# Known limitations and validation scope

## Reproducibility

- Trained weights, SavedModel, encoders, datasets, and footage are intentionally excluded. A fresh clone cannot perform full inference without them.
- Python requirements were inferred from imports and the historical project period. Dependency installation, GPU compatibility, and end-to-end inference have not been validated for this publication.
- The label vocabulary is limited to the original character/action classes. This is not arbitrary-video semantic search.
- No reproducible benchmark supports claims about model accuracy, retrieval quality, or throughput.

The frontend dependency installation also reported an unsupported legacy engine declaration and a deprecation/security warning for the existing Axios version. Updating legacy dependencies is separate from this source-curation work.

## Existing implementation issues

- Timestamp conversion in `info_retrieval` divides the sequential frame index by 100 and FPS, then interprets decimal components as minutes/seconds. This is not a standard frame-to-time conversion and needs correction and testing against actual detector frame output.
- The parser assumes paired detections and particular Darknet stdout formatting. It may omit or misalign frames, so simply changing the timestamp formula would not establish correct synchronization.
- Effects and detection streams are truncated to the shorter stream without validating alignment.
- The backend rewrites a shared HTML template and a shared `effects.json`; concurrent uploads/searches can interfere.
- Upload names and raw filename requests lack robust path validation. There is no authentication, upload limit, or production error handling, and debug mode is enabled. Keep this version local; it is not ready for public hosting.
- The Darknet subprocess command contains shell-redirection tokens although it does not use a shell. Output is captured through a pipe; the command and return-code handling need cleanup.
- Frontend progress is placeholder behavior, and an upload can appear in the list before processing finishes.
- The training notebooks contain exploratory paths/cells and need dataset, split, preprocessing, and export checks before reuse. Their saved outputs are not retained as evaluation evidence.

## Publication changes

The preparation changes only local connectivity defaults, filters the video list to MP4 filenames so the directory placeholder is not shown, clears stale timestamp HTML, and removes notebook output/metadata. It does not repair the historical inference or retrieval algorithms. Check `VALIDATION.md` for the checks actually performed.
