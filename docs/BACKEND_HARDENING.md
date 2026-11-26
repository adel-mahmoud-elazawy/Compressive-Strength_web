# Backend Production Hardening — Implementation Report

**Date:** 2026-11-26
**Target:** `D:\Loay\Compressive-Strength_web-main\concrete-web\backend`
**Outcome:** The existing FastAPI concrete-strength prediction service was hardened in place. Its API contract and Vercel deployment path are unchanged.

---

## 1. What was asked and what was locked

The user asked for a "perfect backend" and a detailed Markdown report of the work. Brainstorming narrowed this to **production hardening only** of the existing backend. Two constraints were locked by the user:

1. Keep the API contract: `/health`, `/meta`, `/predict` and every success-response field stay identical.
2. Acceptance = focused tests plus a live smoke test.

Additional scope decisions made during design: no new runtime dependencies, preserve `api/index.py` and `vercel.json`, and write this report to `docs/BACKEND_HARDENING.md`.

The repository is **not a git repository**, so no branch, commits, or pull request were created. Verification relies on test output and live HTTP responses recorded below.

---

## 2. Workflow and skills used

| Stage | Skill / workflow | What it contributed |
|---|---|---|
| Discovery | `find-skills` | Searched the skills ecosystem with `npx skills find "fastapi backend"`. Most results had very low install counts; the locally installed catalog was stronger, so no external skill was installed. |
| Requirements | `brainstorming` | Explored the existing project, asked one question at a time, fixed scope, constraints, acceptance bar, and approach. |
| Meta | `using-superpowers`, `caveman` | Enforced skill-first behavior and terse terminal responses. |
| Design | `writing-plans` | Produced a five-task, test-first implementation plan with file-level interfaces. |
| Execution | `executing-plans` | Ran the plan inline, task by task, with a scratch ledger for recovery. |
| Implementation | `test-driven-development` | Every production change was preceded by a failing test that was observed failing. |
| Domain guidance | `fastapi-patterns`, `security-review`, `error-handling`, `backend-patterns`, `python-patterns`, `python-testing`, `api-design` | Guided lifespan use, typed response models, CORS, input validation, generic error messages, and test structure. |
| Final gate | `verification-before-completion` | Required fresh command output before any completion claim. |

Approach chosen: **targeted in-place hardening** rather than a rewrite or layered refactor. The service has one model, three endpoints, and no database, so a rewrite would add risk without benefit.

---

## 3. Baseline findings

| # | Finding | Risk | Status |
|---|---|---|---|
| 1 | `app/config.py` defaulted `CORS_ORIGINS` to `...,*` and `main.py` computed `allow_credentials=True` for that list. | Any browser origin could call the API with credentials. | Fixed |
| 2 | `app/model.py` created `model_manager = ConcreteModelManager()` at import time and `ConcreteModelManager.__init__` called `load_model()`. | A missing or corrupt `.pkl` made module import fail; the app could not even start to report the problem. Cold starts also paid the load cost at import. | Fixed |
| 3 | `POST /predict` wrapped everything in `except Exception` and returned `detail=f"Prediction failed: {str(e)}"`. | Internal exception text, paths, or stack context leaked to clients. | Fixed |
| 4 | A JSON number such as `1e999` parsed to `inf`; Pydantic rejected it, but FastAPI's default 422 serializer tried to emit `input: inf` and raised `ValueError`. | Malformed input produced a 500 instead of a 422. | Fixed |
| 5 | No automated tests existed. | No regression protection for the prediction contract or the hardening changes. | Fixed — 25 tests |
| 6 | The bundled model was pickled with scikit-learn 1.6.1; the runtime has 1.8.0 installed. | `InconsistentVersionWarning` on load; results may differ across versions. | Documented as residual risk |

---

## 4. Changes made, file by file

### `app/config.py`
- Added `DEFAULT_CORS_ORIGINS` with localhost origins only.
- Added `_parse_origins()` which splits on commas and strips whitespace from each origin.
- Added `CORS_ALLOW_CREDENTIALS`, set to `False` when `"*"` appears in the origin list.
- Kept `MODEL_PATH` and `BASE_DIR` unchanged.

**Why:** CORS is now an explicit allowlist. A wildcard is possible but must be requested deliberately, and it automatically disables credentials.

### `app/main.py`
- Imports `CORS_ALLOW_CREDENTIALS` and uses it directly in `CORSMiddleware` instead of the previous `CORS_ORIGINS != ["*"]` heuristic.
- `lifespan` now calls `model_manager.load_model()` unconditionally at startup and does not raise on failure; the failure is recorded in the manager.
- Added `_json_safe()` and a `RequestValidationError` handler that keeps the standard `{"detail": [...]}` body but converts non-finite floats to strings before JSON serialization. Status is literal `422` to avoid a deprecated constant.
- Added three exception handlers:
  - `ModelUnavailableError` → `503 {"detail": "Model is not available"}`, logged as a warning.
  - `PredictionError` → `500 {"detail": "Prediction failed due to an internal error"}`, logged with `logger.exception`.
  - Generic `Exception` → `500 {"detail": "Internal server error"}`, logged with `logger.exception`.
- Added `_cors_headers()` so the outer generic 500 handler echoes an allowed origin and the credentials flag. Without it, that response bypassed `CORSMiddleware` and browsers saw an opaque CORS failure.
- Added an additive `/ready` readiness probe: `200 {"status":"ready","model_loaded":true}` when loaded, `503 {"status":"unavailable","model_loaded":false}` when not. `/health` keeps its legacy shape for the frontend.
- Removed the broad `try/except` in `predict_concrete_strength`; it now returns `model_manager.predict(mix_input)` directly.
- Kept `/health`, `/meta`, `/predict`, their tags, response models, titles, and version unchanged.

**Why:** Startup degrades gracefully instead of crashing. Clients see stable, generic error messages; detailed diagnostics stay in server logs. The success contract is untouched.

### `app/model.py`
- Constructor no longer loads the model. It initializes `regressor`, `classifier`, `cutoff`, `is_loaded=False`, and `load_error=None`.
- `load_model()` now returns `bool`, catches load failures, stores a typed message (`ExceptionType: text`) in `load_error`, resets state, and returns `False` instead of raising.
- Startup diagnostics use `logger.info` / `logger.warning` instead of `print()`.
- `predict()` raises `ModelUnavailableError("Model bundle is not loaded")` when the model is unavailable instead of lazily reloading it inside a request.
- `add_features()`, the raw feature order, the regression/classification logic, all rounding, and every response field are byte-for-byte unchanged.

**Why:** Model loading is a startup concern, not a request concern. Failure state is observable and does not crash the process.

### `app/errors.py` (new)
- `ModelUnavailableError` and `PredictionError` typed exceptions.

**Why:** Exception handlers can map specific failure modes to specific status codes without string matching.

### `app/schemas.py`
- Intentionally unchanged. The installed Pydantic version already rejects `NaN`/`Infinity`. Adding a redundant validator would not have fixed the observed 500; the fix belonged in error serialization. This decision is recorded in the task ledger.

### `.env.example`
- Removed the `*` entry from the sample CORS list.
- Documented that wildcard disables credentialed requests and added an optional `MODEL_PATH` example.

### `requirements-dev.txt` (new)
- Declares `pytest` and `httpx` on top of `-r requirements.txt`, so a clean install can collect the tests. Runtime dependencies remain unchanged.

### `requirements.lock.txt` (new)
- Exact versions captured from the verified Python 3.13.7 environment, including runtime and test packages. A brand-new venv installed from this lock passed `pip check` and all 25 tests.

### `concrete-web/README.md`
- CORS deployment instructions now require an explicit frontend origin and no longer recommend `*`.

### `tests/` (new)
- `test_config.py` — CORS defaults, wildcard/credentials coupling, whitespace trimming.
- `test_model_lifecycle.py` — import with missing bundle, corrupt bundle, constructor side effects, load success/failure, typed errors on unavailable model and inference failure.
- `test_schemas.py` — Pydantic rejection of non-finite values, API returns 422 for `1e999`, valid defaults accepted.
- `test_errors.py` — no internal detail in 500, generic 503, health and readiness reporting, CORS allow/deny headers including generic 500, wildcard credentials coupling at HTTP level, Vercel entrypoint import from another working directory.

---

## 5. Verification evidence

### 5.1 Automated tests

Command run from `backend/`:

```
python -m pytest -q
```

Final observed result:

```
25 passed, 20 warnings in 5.63s
```

The 20 warnings are all `InconsistentVersionWarning` from scikit-learn (finding 6); no deprecation warnings remain from the new code.

Per-task red/green evidence:

| Task | RED evidence | GREEN evidence |
|---|---|---|
| 1 — Config/CORS | 3 failed: default list contained `*`, untrimmed origins | `tests/test_config.py` 3 passed |
| 2 — Model lifecycle | 5 failed: import raised `FileNotFoundError`, constructor loaded eagerly, `load_model()` returned `None`, no typed error | `tests/test_model_lifecycle.py` 5 passed |
| 3 — Non-finite input | API test failed with `ValueError: Out of range float values are not JSON compliant: inf` | `tests/test_schemas.py` 5 passed |
| 4 — Errors/security | 2 failed: `"secret internal detail"` appeared in the 500 body; unavailable model returned 500 instead of 503 | `tests/test_errors.py` 6 passed |
| Final pass | 4 failed: generic 500 lacked CORS headers, `/ready` returned 404, corrupt bundle message untyped | all new tests passed; suite 25 passed |

### 5.2 Live smoke test — healthy model

Server started with `PORT=8099 python run.py`. Observed responses:

```
HEALTH: {"status":"healthy","service":"concrete-strength-api","model_loaded":true,"cutoff_mpa":33.72}
META: fields=8 examples=4 model=GradientBoostingRegressor + Median Cutoff Classifier
PREDICT: {"predicted_strength_mpa":37.44,"label":"STRONG","cutoff_mpa":33.72,"is_strong":true,"equivalent_psi":5430.0,"water_cement_ratio":0.64,"water_binder_ratio":0.47,"total_binder_kg_m3":380.0,"curing_age_days":28.0}
CORS_EVIL_HEADER:
```

The prediction response contains all nine original success fields. An unlisted origin receives no `Access-Control-Allow-Origin` header.

### 5.3 Live smoke test — missing model bundle

Server started with `PORT=8098`, `MODEL_PATH` pointing to a nonexistent file. Server log and responses:

```
INFO:     Application startup complete.
[ModelManager] Failed to load model bundle: Model bundle file not found at: ...\missing_model.pkl ...
INFO:     127.0.0.1:59738 - "GET /health HTTP/1.1" 200 OK
Model unavailable: Model bundle is not loaded
INFO:     127.0.0.1:59738 - "POST /predict HTTP/1.1" 503 Service Unavailable

DEGRADED_HEALTH: {"status":"healthy","service":"concrete-strength-api","model_loaded":false,"cutoff_mpa":33.72}
DEGRADED_PREDICT_BODY: 503 {"detail":"Model is not available"}
```

The service starts, reports the real model state, and returns a safe 503 for predictions.

### 5.4 Clean environment verification (Python 3.13)

A fresh venv was created with Python 3.13 and installed from `requirements.txt` + `requirements-dev.txt`:

```
Successfully installed ... scikit-learn-1.6.1 ...
No broken requirements found.
25 passed, 1 warning in 11.36s
```

The single warning is a Starlette notice about `httpx` vs `httpx2`; there is no `InconsistentVersionWarning`. A second, brand-new venv installed from `requirements.lock.txt` produced the same result: `No broken requirements found.` and `25 passed, 1 warning in 10.31s`. A live server on the first venv returned the same prediction as the 3.14 environment:

```
PY313_HEALTH: {"status":"healthy","service":"concrete-strength-api","model_loaded":true,"cutoff_mpa":33.72}
PY313_PREDICT: {"predicted_strength_mpa":37.44,"label":"STRONG", ...}
```

### 5.5 Live smoke test — readiness probe

Two servers were started, one with the real bundle (`PORT=8097`) and one with a missing bundle (`PORT=8096`). Observed responses:

```
8097 200 {"status":"ready","model_loaded":true}
8096 503 {"status":"unavailable","model_loaded":false}
```

`/health` kept its original response shape in both cases; `/ready` is additive and gives orchestrators a real readiness signal.

---

## 6. Decisions and deviations from the plan

1. **No git operations.** The repository is not a git repo. Plan steps that said "commit" were replaced with diff review. No `git init` was performed because that is an unrequested repository change.
2. **HTTP 503 mapping moved to Task 4.** The plan placed it in the model-lifecycle task, but the exception handler is a Task 4 deliverable. Task 2 pinned manager state and the typed exception; Task 4 pinned the HTTP mapping.
3. **No redundant schema validator.** The installed Pydantic already rejects non-finite values. The real defect was error serialization, fixed in `app/main.py`.
4. **CORS and entrypoint tests characterized existing correct behavior.** They passed before implementation, but they now protect the locked contract against regression.
5. **Final-review fixes.** A fresh reviewer found that `PredictionError` had a registered handler but no producer, so real inference failures fell through to the generic handler. `app/model.py` now wraps inference failures in `PredictionError`, proven by a new RED→GREEN test. The reviewer also flagged the CORS default change as a deployment migration; `concrete-web/README.md` and this report now state the required environment variable explicitly.
6. **Follow-up cleanup.** Addressed the remaining fixable review minors: generic 500 CORS headers, corrupt-bundle test, HTTP-level wildcard CORS test, direct exception-class assertion, `logger` instead of `print()`, typed `load_error` text, `requirements-dev.txt`, and a real `/ready` probe. Each behavior change was preceded by a failing test.

---

## 7. Residual risks and next steps

| Risk | Detail | Suggested action |
|---|---|---|
| Python / model runtime — RESOLVED | A clean `pip install -r requirements.txt -r requirements-dev.txt` on Python 3.14.4 failed (`metadata-generation-failed` compiling `scikit-learn==1.6.1`; no 3.14 wheel). On Python 3.13 the same install succeeded, `pip check` was clean, 25 tests passed with only a Starlette/httpx deprecation warning, and the live prediction was unchanged at 37.44 MPa with no sklearn warning. `.python-version` now pins 3.13 for Vercel. | Use Python 3.13. No retraining or scikit-learn upgrade is needed. |
| No rate limiting | The hardening scope did not include request throttling. `/predict` is unauthenticated. | Add a rate limiter at the edge (Vercel) or in middleware before public exposure. |
| No authentication | The API is public by design; no auth was added because it would change the frontend contract. | Add auth only with a coordinated frontend change. |
| `/health` always says `status: "healthy"` | The legacy field stays `"healthy"` when the model is missing, to preserve the frontend contract. | Use the new `/ready` endpoint (200 ready / 503 unavailable) for orchestrator readiness. |
| Pickle trust | `joblib.load` executes pickled code. `concrete_model.pkl` must remain a trusted artifact. | Keep the bundle under version control with review; never load user-supplied pickle files. |
| Dependency reproducibility — RESOLVED | Python is pinned by `.python-version` (3.13), test deps by `requirements-dev.txt`, and exact versions by `requirements.lock.txt`. A fresh venv installed from the lock: `pip check` clean, 25 tests passed. | Use `requirements.lock.txt` for byte-for-byte reproducible installs. |

---

## 8. How to reproduce

From `D:\Loay\Compressive-Strength_web-main\concrete-web\backend`, using Python 3.13 (pinned in `.python-version`):

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.lock.txt   # exact versions
# or: .venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe run.py
```

Then request:

```
GET  http://127.0.0.1:8000/health
GET  http://127.0.0.1:8000/ready
GET  http://127.0.0.1:8000/meta
POST http://127.0.0.1:8000/predict
Content-Type: application/json

{"Cement":280.0,"Blast_Furnace_Slag":100.0,"Fly_Ash":0.0,"Water":180.0,
 "Superplasticizer":5.0,"Coarse_Aggregate":970.0,"Fine_Aggregate":770.0,"Age":28.0}
```

Configuration is read from the environment; see `.env.example`.

**Required deployment migration:** the old default CORS list contained `*`. It now contains only `http://localhost:3000` and `http://127.0.0.1:3000`. Any existing deployed backend that relied on the old default **must** set `CORS_ORIGINS` to the deployed frontend's exact origin (for example `https://concrete-strength-frontend.vercel.app`), or every browser request from that frontend will fail CORS. `concrete-web/README.md` has been updated with this requirement. Do not use `*` in production: it also disables credentialed requests.
