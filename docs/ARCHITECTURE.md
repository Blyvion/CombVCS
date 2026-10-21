# Architecture and API

## Processing flow

1. `VideoUploader.vue` submits an MP4 as multipart field `video` to `/processvideo`.
2. Flask saves the file under `static/saved_videos/` and runs Darknet synchronously.
3. `create_result_json` parses detector stdout into character/move records.
4. `effect_detector.py` loads the SavedModel and encoders, resizes each video frame to 224 × 224, normalizes its values, and predicts an effect.
5. `combine_json_files` merges the streams by sequential frame index, stopping at the shorter stream.
6. `/search` loads that video's JSON and constructs captions from the two character/move records plus effect.
7. `TfidfVectorizer` fits those captions; cosine similarity ranks them against the query. Scores below `0.5` are discarded.
8. The server writes timestamp text and modifies the shared HTML template; the frontend reloads its player iframe to display results.

The active retrieval function is `info_retrieval`. Older experimental helpers and BM25 imports remain in the source but are not the active search path.

## Frame record

Illustrative schema, not an evaluation result:

```json
[
  {
    "frame_0": {
      "char1": { "char": "cloud", "move": "forward_air" },
      "char2": { "char": "zss", "move": "shield" },
      "effect": "none"
    }
  }
]
```

Move underscores become spaces in the caption. The JSON is stored in the backend working directory under the video stem. `effects.json` is a shared intermediate file.

## HTTP interface

| Method | Route | Request | Result |
| --- | --- | --- | --- |
| GET | `/ping` | None | JSON `"pong!"` |
| GET | `/listvideos` | None | JSON with `status`, `message`, `videolist` |
| POST | `/processvideo` | Multipart `video` | Processes video; success JSON after completion |
| POST | `/search` | Form `text`, `filename` | Rendered player HTML; updates timestamp file/template |
| GET | `/<filename>` | Video filename in URL | Player HTML; resets timestamp list |
| GET | `/<filename>~` | Trailing `~` | Player HTML preserving timestamp list |
| POST | `/getvideo` | Raw filename body | Video bytes |
| POST | `/deletevideo` | Raw filename body | JSON deletion result |

These are prototype contracts, not hardened public APIs. Processing has no job queue, durable progress tracking, or authentication. Videos and annotations are filesystem-backed; there is no database.
