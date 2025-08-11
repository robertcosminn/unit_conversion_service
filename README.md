# Unit Conversion Service 

Convert common units (*length*, *weight*, *temperature*) straight from your terminal while ticking every box of the homework brief — MVCS architecture, Pydantic v2 validation, SQLite persistence, Click UX, lint‑clean code and a pinch of caching.

---

## ✨ Aspects

* **MVCS layout** – easy to reason about & extend
* **Zero external services** – SQLite file DB; clone → install → run
* **Pydantic v2** – strong typing + runtime validation
* **Click CLI** – auto `--help`, colors, sub‑commands
* **LRU cache** – instant repeat conversions
* **flake8 + pytest** – quality gates ready for CI

---

## 🗂️ Folder layout

```
unit_conversion_service/
├─ app/
│  ├─ __init__.py      # marks package
│  ├─ cli.py           # Click commands (controller / view)
│  ├─ db.py            # DB engine + helpers (infrastructure)
│  ├─ models.py        # Pydantic + SQLAlchemy models (model)
│  └─ services.py      # Business logic + in‑memory cache (service)
├─ tests/              # pytest sample
├─ .flake8             # linter config
├─ requirements.txt    # reproducible deps
└─ conversions.sqlite3 # auto‑generated on first run
```

---

## 🚀 Quick start

```bash
# 1.  Clone & enter repo
git clone https://github.com/<your‑user>/unit_conversion_service-.git
cd unit_conversion_service-

# 2.  (Optional) create virtual env
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3.  Install dependencies
pip install -r requirements.txt
```

First conversion:

```bash
python -m app.cli length 2.5 --from km --to mi -v
```

```
┌────────────────────────────┬─────────┐
│ Details                    │ Result  │
├────────────────────────────┼─────────┤
│ 2.5 km → 1.553428 mi       │ 1.553428│
└────────────────────────────┴─────────┘
```

> ℹ️ `conversions.sqlite3` is created on first run and every request is persisted.

---

## 📖 Command reference

### General help

```bash
python -m app.cli --help          # top‑level
python -m app.cli length --help   # per‑command help
```

### Conversion commands

| Category        | Example command                                        | Supported units             |
| --------------- | ------------------------------------------------------ | --------------------------- |
| **Length**      | `python -m app.cli length 10 --from mi --to km`        | `m, cm, mm, km, ft, in, mi` |
| **Weight**      | `python -m app.cli weight 5 --from lb --to kg`         | `kg, g, lb, oz`             |
| **Temperature** | `python -m app.cli temperature 300 --from K --to C -v` | `C, F, K`                   |

Add `-v/--verbose` for a pretty table; omit for raw numeric output.

### Cache utilities *(optional)*

If you enabled the cache sub‑commands:

```bash
python -m app.cli cache stats   # hit/miss counters & size
python -m app.cli cache dump    # list cached requests → result
python -m app.cli cache clear   # flush cache
```

### Developer toolbox

```bash
flake8 .            # lint → should print nothing
pytest -q           # run unit tests (sample included)

# Inspect DB (requires sqlite3 CLI)
sqlite3 conversions.sqlite3 \
  "SELECT id, category, src_value, src_unit, dst_unit, result, created_at \
   FROM conversions ORDER BY id DESC LIMIT 5;"
```

---

## 🏗️ How it works (pipeline)

1. **Click CLI** parses args → Python variables.
2. **Pydantic** `ConversionRequest` validates & normalises input.
3. **Service layer** chooses:

   * factor‑table math (length / weight)
   * formula mapping (temperature)
4. Result wrapped in `ConversionResponse` and memoised in an **LRU cache** (128 entries).
5. **SQLAlchemy ORM** inserts a row into SQLite (`conversions` table).
6. CLI prints either numeric or pretty‑table view.

Because layers are decoupled, you can bolt on FastAPI, Docker, Prometheus or new unit categories with minimal edits.


