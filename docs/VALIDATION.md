# Publication validation

Checked on October 21, 2026:

| Check | Result |
| --- | --- |
| Frontend `npm ci` using the existing lockfile | Passed; 1,016 packages installed |
| Frontend `npm run build` | Passed with bundle-size warnings |
| Python syntax parsing of both backend scripts | Passed |
| Notebook JSON and removal of outputs/execution counts | Passed |
| Relative Markdown documentation links | Passed |
| Publication file selection | No model binaries, videos, datasets, installers, dependency directories, nested repositories, or generated builds selected |
| Common credential-pattern scan | No matching private-key, GitHub-token, or AWS-access-key patterns found; not a comprehensive secret audit |

The frontend was built using Node.js 24.19.0 and npm 10.9.4 in the preparation environment. Installation warned about an older dependency's engine declaration and the existing Axios version. Build output also warned about outdated Browserslist data, deprecated Node APIs, and bundle sizes. A successful build does not establish browser behavior or dependency security.

**Not verified:** backend dependency installation, backend startup, full video inference, CUDA/cuDNN compatibility, model accuracy, timestamp correctness, and end-to-end browser interaction. The required external models and training inputs are not part of this publication. Python requirements are an inferred historical baseline rather than a recovered lockfile.

## Archive addition checks

The original poster and report cover, results, and screenshot pages were visually inspected. All report text was extracted for review. The copied PDF, poster, LaTeX source, bibliography, and 11 referenced figures match the source files by SHA-256; see `archive/SHA256SUMS`. Relative documentation links and LaTeX figure references were checked. Duplicate compressed report archives matched the unpacked files. Application code did not change, so the frontend build was not repeated. The archived LaTeX source was not recompiled, and historical model results were not rerun.
