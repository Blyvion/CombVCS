# Local setup

This is a historical prototype, not a turnkey distribution. The frontend has a saved npm lockfile. No original Python environment lock was found; `web/server/requirements.txt` is an **inferred historical baseline**, not a tested or security-maintained environment. Use an isolated local environment. Python 3.9 matches evidence in the archived project; modern Python/TensorFlow versions may not load these artifacts unchanged.

## Frontend

Install Node.js and npm, then run from the repository root:

```sh
cd web/combvcs
npm ci
npm run build
npm run serve
```

Open `http://localhost:8080`. The UI expects the backend at `http://127.0.0.1:32001`. To change the backend address, update both `src/App.vue` and `src/utils/axios-instance.js`; the upload, delete, and iframe URLs also use port `32001` in their components.

The optional `node server.js` command serves an existing `dist/` build on port `32000`. It does not start the Python backend.

## Backend prerequisites

Supply these files from the original project or a compatible, trusted training run. There is no public model download packaged with this repository.

| Required path under `web/server/` | Purpose |
| --- | --- |
| `yolov3_move_train_last.weights` | Trained character/action detector |
| `effects_model/` | Complete TensorFlow SavedModel directory, including variables |
| `label_encoder.pkl` | Effect label encoder paired with the model |
| `onehot_encoder.pkl` | Effect one-hot encoder paired with the model |
| `darknet/darknet` | Locally built Darknet executable with video/OpenCV support |

Use matching model and encoder versions. Pickle files must come from a trusted source. Do not mix arbitrary class labels, weights, or encoder files.

The supplied `darknet/` folder contains only project-specific configuration. Build AlexeyAB/Darknet separately and copy the resulting executable into `web/server/darknet/darknet`. The original vendored checkout recorded commit `8a0bf84c19e38214219dbd3345f04ce778426c57`; this identifies its provenance, not a guarantee of reproducibility. Consult that upstream checkout's build instructions for OpenCV and, if used, CUDA/cuDNN. Do not commit the upstream source tree or generated binaries here.

The detector's `obj.data` uses `names=data/obj.names`, resolved from the backend working directory; `web/server/data/obj.names` is included for this reason. Its train/validation paths refer to excluded training data and are not needed for inference.

## Start the backend

From the repository root, with Python 3.9 available:

```sh
python3.9 -m venv .venv
. .venv/bin/activate
python -m pip install -r web/server/requirements.txt
cd web/server
mkdir -p static/saved_videos static/saved_timestamps
python app.py
```

Start it **from `web/server`** because the implementation uses relative paths. It binds to `127.0.0.1:32001` by default. `COMBVCS_HOST` and `COMBVCS_PORT` override the bind settings. The app currently downloads NLTK resources during import, so its first startup may require network access.

In a second terminal:

```sh
curl http://127.0.0.1:32001/ping
```

A running backend returns JSON `"pong!"`. Select a short MP4 containing supported gameplay, wait for processing to finish, select it in the video list, and search using class vocabulary such as `cloud forward air`. Timestamp correctness still needs validation; see [limitations](LIMITATIONS.md).

## Training notebooks

- `notebooks/effects_training.ipynb` comes from the complete training variant in the original Downloads folder, including encoder serialization and CNN construction. It requires the excluded `effects/` annotations and images. Its model-save cell is commented out; adapt it before exporting a model.
- `notebooks/yolov3_training.ipynb` contains the Colab/Google Drive detector workflow and its original tutorial attribution. Adapt its Drive paths and supply the annotated dataset and initial weights.

These notebooks preserve experiments; they are not automated, reproducible training pipelines. Their outputs and execution counts were cleared before publication. Notebook-only packages such as Jupyter and matplotlib are not included in the backend requirements.
