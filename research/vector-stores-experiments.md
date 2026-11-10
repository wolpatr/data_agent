# Vector stores + embeddings for experiment records — fact-finding (v0.3)

**Research date:** 2026-11-10 · **Status:** research-only fact-finding — no decision made here · **Scope:** relational store + embedding/vector layer for freqtrade walk-forward/k-fold backtest experiment records (hundreds → possibly low-thousands of rows), for a later RAG-based explainability idea; plus later news-headline embeddings. Constraints: Windows desktop, local-first, uv/pip install surface, no cloud vendor, nothing paid.

**Method / verification level:** primary sources only (official docs, GitHub repos, PyPI, model cards), fetched 2026-11-10. Claim marks: **[Verified]** = stated on a primary source fetched this session; **[Verified-local]** = reproduced on this machine (repo uv venv, Windows x64); **[Unverified]** = plausible but not confirmed against a primary source this session; **[Unverified-detail]** = source exists but the specific detail was not read.

Everything version-shaped was additionally cross-checked by a `uv pip install --dry-run` resolution in the repo venv on 2026-11-10 (Python 3.13.12): resolved 117 packages across the full candidate set; would-install 70.

---

## TL;DR (facts only)

- **Embedded/local vector stores that install via pip on Windows today** [Verified-local 2026-11-10]: `sqlite-vec 0.1.9` (292.8 kB wheel, no heavy deps), `chromadb 1.5.9`, `lancedb 0.41.0`, `qdrant-client 1.20.0` (has local mode) + new `qdrant-edge-py` in-process engine, `duckdb 2.0.0` + experimental `vss` extension. `pgvector` is not embeddable — it extends a running Postgres server.
- **SQLite + sqlite-vec is the only candidate that puts relational rows and vectors in one file with zero server/admin**, matching the project's existing SQLite habit (freqtrade DBs). Trade-off: sqlite-vec is pre-v1 ("expect breaking changes") and its Python release train is at 0.1.9 stable / 0.1.10a4 pre-release [Verified].
- **pgvector gives the strongest relational+vector integration** (one Postgres DB, SQL joins between facts and vectors, ACID) but requires installing and operating a Postgres server on Windows, plus an MSVC build or Docker for the extension [Verified].
- **Local embedding default for short technical text: sentence-transformers `all-MiniLM-L6-v2`** — 384-dim, 22.7M params, Apache-2.0, truncates past 256 word pieces [Verified]; it is also Chroma's built-in default EF and has ONNX files on the HF repo. `fastembed` (ONNX Runtime, no PyTorch) defaults to `BAAI/bge-small-en-v1.5` (384-dim) [Verified].
- **No official per-CPU latency figures exist in the sources fetched** for any candidate model on this machine class [Verified absence — benchmark locally before locking a model].
- **Documented practice for experiment-metadata similarity is hybrid, not "embed the numbers":** exact structured dimensions are queried with relational/metadata filters (every store documents this); text-embedding models are documented for *text*; raw numeric/feature vectors can be stored as plain float vectors and compared with L2/cosine in every store [Verified]. No primary source found endorsing running text-embedding models on pure numeric records (absence noted, not proof).
- **Write paths are all idempotent-upsert shaped:** SQLite `ON CONFLICT … DO UPDATE` (with the caveat it cannot fire on virtual tables — i.e. not on vec0), pgvector `ON CONFLICT (id) DO UPDATE`, Chroma `collection.upsert`, Qdrant `upsert` (+ insert-only mode); re-indexing on model change follows the dual-write + backfill pattern documented by Qdrant [Verified].

---

## 1. Comparison table

| # | Store | Engine & maturity | Windows / pip install surface [all Verified-local 2026-11-10] | Relational + vector in one store? | Persistence | Python API maturity | Metadata/filtering power | License |
|---|---|---|---|---|---|---|---|---|
| 1 | **sqlite-vec** (`sqlite-vec` 0.1.9 stable; 0.1.10a4 pre-release) | SQLite extension, pure C, `vec0` virtual tables; explicit "pre-v1, expect breaking changes" [Verified] | `pip install sqlite-vec`; win_amd64 wheel 292.8 kB; stdlib `sqlite_vec.load(db)`; recommends SQLite ≥ 3.41 (repo venv has 3.50.4 ✅) | **Yes — vectors and relational tables in the same SQLite file** (vec0 tables coexist with normal tables) | Standard SQLite file | Small, stable-in-shape API; docs marked work-in-progress; pre-v1 | vec0 metadata columns (≤16; only `=`,`!=`,`<`,`<=`,`>`,`>=`; no `LIKE`/`IS NULL`), partition keys (≤4, ~"100s of vectors per partition" guidance), aux columns (≤16, not filterable) [Verified] | MIT **or** Apache-2.0 (dual) [Verified] |
| 2 | **pgvector** (v0.8.7) | Postgres extension; HNSW + IVFFlat ANN, exact search as default; Postgres 13+ [Verified] | Needs a **running Postgres server** + extension built with MSVC (`nmake /F Makefile.win`, admin shell, `PGROOT`) or Docker image `pgvector/pgvector:pg13–pg18` [Verified] | **Yes — full Postgres**: vector is a column type; joins, ACID, FTS, partitions | Postgres server (WAL, replication) | Mature; `pgvector` pip client resolves at 0.5.1; SQLAlchemy/psycopg integration [Verified install; API detail Unverified] | SQL `WHERE` with b-tree/partial indexes; iterative index scans since 0.8.0; multi-dim vectors via expression+partial indexes [Verified] | PostgreSQL Licence per repo `LICENSE` file [file exists — text Unverified-detail] |
| 3 | **Chroma** (chromadb 1.5.9) | Embedded (in-process) or client-server; Apache-2.0 OSS [Verified] | `pip install chromadb` — heaviest dep tree of the set (resolved tree includes `onnxruntime`, `opentelemetry-*`, `grpcio`, `bcrypt`, `mmh3`, `pypika`; attribution to chromadb from combined tree — Unverified-detail) | No — dedicated vector store; experiment rows stay in SQLite/other | `PersistentClient(path=...)` (default dir `.chroma`); in-memory `Client()`; client-server `chroma run` [Verified] | Mature, high-level (`add/upsert/query`, `get_or_create_collection`); docs push Chroma Cloud heavily [Verified] | Metadata `where` filters, full-text & regex search, dense+sparse hybrid — all documented capabilities of collections [Verified] | Apache-2.0 [Verified — docs home] |
| 4 | **LanceDB Embedded** (lancedb 0.41.0) | Embedded library over columnar **Lance format** (Arrow-native); OSS [Verified] | `pip install lancedb pandas`; **default wheel requires AVX2 (x86-64-haswell) — crashes `import lancedb` on older CPUs; `lancedb-compat` fallback exists** [Verified] | No — its own table format; relational-style tables with typed columns + vector columns in same table | Local directory (or object storage); **table versioning** documented [Verified] | Mature Python SDK; SQL over tables is **Enterprise-only** [Verified — quickstart step 5 note] | Filtering + full-text + hybrid + reranking per docs; vector distance L2/cosine [Verified at feature-blurb level] | Apache-2.0 [Verified — repo LICENSE text fetched] |
| 5 | **DuckDB VSS** (`duckdb 2.0.0` + `vss` extension) | DuckDB core extension, **experimental**; HNSW index on `FLOAT[n]` ARRAY columns [Verified] | `INSTALL AND LOAD vss` inside DuckDB; duckdb pip resolves on Windows [Verified] | Yes — DuckDB file (columnar analytics engine) | **By default HNSW indexes only persist in in-memory DBs; `hnsw_enable_experimental_persistence=true` recommended NOT for production; entire index re-serialized on checkpoint; index must fit in RAM** [Verified] | Simple SQL extension; brute-force + HNSW-accelerated `ORDER BY … LIMIT` [Verified] | Full DuckDB SQL (columnar); FLOAT vectors only; deletes marked-stale + `PRAGMA hnsw_compact_index` [Verified] | MIT per duckdb repo [Unverified-detail] |
| 6 | **FAISS** (`faiss-cpu` 1.16.0) | Library of ANN algorithms only — no query API, no metadata, no persistence layer of its own [Verified — task-known; repo fetched only for license] | `pip install faiss-cpu` wheels resolve on Windows [Verified-local] | No — you build your own storage + filter logic around it | You implement it (file-based index snapshots) | Low-level; MIT license; used as an ANN building block | None built in | MIT [Verified — LICENSE text fetched] |
| 7 | **Qdrant** (server; qdrant-client 1.20.0) | Self-hosted vector DB (Docker `qdrant/qdrant`, ports 6333 REST / 6334 gRPC) [Verified] | Docker on Windows; client pip resolves [Verified-local] | No — dedicated store; payload = JSON docs | qdrant_storage directory on host volume [Verified] | Mature REST/gRPC + rich Python client; `client.upsert`, `query_points`, payload `Filter` [Verified] | Very strong: payload filters (`must`/`should`/`must_not`, ranges, full-text), payload indexes, facets [Verified] | Apache-2.0 per repo [Unverified-detail] |
| 7b | **Qdrant Edge** (`qdrant-edge-py`, new in 2026 docs) | **In-process embedded engine** (Python/Rust bindings); per-shard directory on disk, WAL, quantization [Verified] | pip `qdrant-edge-py` [Verified docs; wheel resolves — Unverified (not in dry-run set)] | No — dedicated store per shard | Local directory, WAL, `close()/load()` [Verified] | New API surface (2026); `EdgeConfig`/`EdgeShard`; no background optimizer — app calls `optimize()` [Verified] | payload filters + payload indexes + facets, same filter model as Qdrant [Verified] | Same-family repo (qdrant/qdrant `lib/edge`); license [Unverified-detail] |
| 7c | **qdrant-client local mode** | In-process emulation inside the Python client; `QdrantClient(":memory:")` appears in fastembed's official usage example [Verified via fastembed README] | Included in `qdrant-client` pip; also `qdrant-client[fastembed]` extra [Verified] | No | In-memory / local-path persistence [half-Verified: memory mode Verified; path-persistence detail Unverified this session] | Long-standing client feature | Same filter API as server [Verified pattern] | Apache-2.0 [Unverified-detail] |

---

## 2. Candidates — section per store (facts + exact URLs)

### 2.1 sqlite-vec — SQLite extension
- Maturity: explicit warning on the repo README: *"`sqlite-vec` is a pre-v1, so expect breaking changes!"* [Verified] — https://github.com/asg017/sqlite-vec
- Release train [Verified, PyPI]: stable **0.1.9** (2026-03-31), pre-release **0.1.10a4** (2026-05-18) — https://pypi.org/project/sqlite-vec/ (win_amd64 wheel 292.8 kB; total release 912.9 kB).
- Capabilities [Verified — https://alexgarcia.xyz/sqlite-vec/features/vec0.html]: `vec0` virtual tables store float/int8/binary vectors; **metadata columns** (TEXT/INTEGER/FLOAT/BOOLEAN only, strict-typed, max 16; KNN-`WHERE` supports only `=`, `!=`, `>`, `>=`, `<`, `<=` — `LIKE`, `IS NULL`, functions are errors); **partition keys** (max 4; guidance "make sure every unique partition key value has ~100s of vectors"; docs literally give a news-headlines partitioned-by-date example); **auxiliary columns** (`+col`, max 16; large text/blobs not filterable).
- Python usage [Verified — https://alexgarcia.xyz/sqlite-vec/python.html]: `pip install sqlite-vec` → `db.enable_load_extension(True); sqlite_vec.load(db)`; recommends **SQLite ≥ 3.41** for some features. [Verified-local] repo venv = Python 3.13.12, `sqlite3.sqlite_version` = **3.50.4** → requirement satisfied.
- Sponsorship/status: Mozilla Builders project (Mozilla, Fly.io, Turso, SQLite Cloud, Shinkai) [Verified — README].
- Write-path note [Verified — https://www.sqlite.org/lang_upsert.html]: SQLite `UPSERT` "does not currently work for virtual tables" → vec0 rows are updated by **delete + insert**, not `ON CONFLICT`.

### 2.2 pgvector — Postgres extension
- Version & support [Verified — https://github.com/pgvector/pgvector]: **v0.8.7** install branch, Postgres **13+**; exact search by default; HNSW (m=16, ef_construction=64, ef_search=40) and IVFFlat; halfvec/binary/sparsevec; **iterative index scans since 0.8.0**; hybrid search recipe with Postgres FTS + RRF; `vector` up to 2,000 dims indexable (16,000 storable).
- Windows cost [Verified]: build via `x64 Native Tools Command Prompt for VS`, `nmake /F Makefile.win install` (admin), or `docker pull pgvector/pgvector` (pg13–pg18 tags). Either way **a Postgres server must be installed, run, backed up, and version-matched** — the operational cost the task flagged is real and documented.
- Python client [Verified install]: `pgvector` 0.5.1 resolved in repo venv dry-run; project = https://github.com/pgvector/pgvector-python (linked from README; API details Unverified).
- Filtered-ANN behavior [Verified]: `WHERE` filters applied *after* HNSW index scan by default; b-tree/partial indexes recommended, iterative scans recover recall (`hnsw.iterative_scan`).

### 2.3 Chroma — embedded vector DB
- Client modes [Verified — https://docs.trychroma.com/docs/run-chroma/clients.md]: in-memory `chromadb.Client()`; **`chromadb.PersistentClient(path="/path")`** persists automatically to disk (default `.chroma`); `chroma run` client-server; `chromadb.CloudClient` is presented first in docs (cloud-first docs posture).
- Core API [Verified — https://docs.trychroma.com/docs/overview/getting-started.md]: `create_collection` / `get_or_create_collection`, `add`, `upsert` (docs: "switch `add` to `upsert` to avoid adding the same documents every time"), `query` with `query_texts` or `query_embeddings`, unique string IDs per document.
- Capabilities at collection level [Verified — https://docs.trychroma.com/]: dense + sparse vector search, metadata filtering, full-text & regex search, pluggable embedding functions (OpenAI/Cohere/HF/sentence-transformers…).
- Default embedding function [Verified — https://docs.trychroma.com/docs/embeddings/embedding-functions.md]: **sentence-transformers `all-MiniLM-L6-v2`, runs locally, auto-downloads model files**; custom EFs implement `EmbeddingFunction`.
- Dependency weight [Verified-local]: combined candidate dry-run resolved 117 packages (70 to install); sqlite-vec+fastembed alone resolve just 31 (17 to install) — chromadb sits at the heavy end of the pip surface.

### 2.4 LanceDB — embedded, Arrow/Lance-native
- Model [Verified — https://docs.lancedb.com/basics/lancedb-embedded.md]: "open-source, embedded retrieval library that runs inside your application process, with no separate database server"; same Lance format as the paid Enterprise offering; local disk or object storage.
- Quickstart facts [Verified — https://docs.lancedb.com/quickstart.md]: `pip install lancedb pandas`; `db = lancedb.connect("dir")`; tables hold regular columns + `embedding` vector columns side by side (incl. nested structs); `.search(vector).select(...).limit(2).to_pandas()`; IVF-Flat index creation; **SQL over the connection is Enterprise-only**; **default wheel targets x86-64-haswell (AVX2+FMA+F16C) — older CPUs crash with `Illegal instruction`; `lancedb-compat` is the fallback package**.
- Versioning [Verified — https://docs.lancedb.com/]: "Table versions let you trace each training run back to the exact data it used" — an interesting fact for experiment provenance.
- Write paths [Verified as doc index blurb]: ingest page covers "Create tables, append records, and update or delete rows" — https://docs.lancedb.com/ingestion.md (API-level upsert semantics Unverified).

### 2.5 DuckDB VSS — extension status
- [Verified — https://duckdb.org/docs/2.0/core_extensions/vss.html]: "experimental extension"; HNSW on fixed-size `FLOAT[n]` columns; metrics l2sq/cosine/ip; **"the HNSW index can only be created on tables in in-memory databases by default, unless `SET hnsw_enable_experimental_persistence=true`"**, and: *"we still recommend that you do not use this feature in production environments"* — WAL recovery for custom indexes is not properly implemented (crash risk = data loss/corruption of the index); persistent index is **fully re-serialized on every checkpoint**; index must fit in RAM and does not count toward `memory_limit`; deletes are marked-stale with `PRAGMA hnsw_compact_index('name')`.
- Relevance here: DuckDB already a plausible analytics/parquet tool in Python; but vss persistence posture is the weakest of all candidates for a store of record.

### 2.6 FAISS — library only
- MIT [Verified — https://raw.githubusercontent.com/facebookresearch/faiss/main/LICENSE]; `faiss-cpu` 1.16.0 resolves on Windows [Verified-local].
- Facts per task premise (no dedicated query API, no metadata filtering, no server) — nothing in FAISS itself provides persistence/idempotent CRUD; it would sit *behind* a custom layer. No dedicated fetch of the README this session beyond the license [Unverified-detail].

### 2.7 Qdrant — server, client local mode, and Edge
- Self-hosted [Verified — https://qdrant.tech/documentation/quickstart/]: Docker `qdrant/qdrant`, `client.upsert(...)` with `PointStruct(id, vector, payload)`, `query_points(..., query_filter=Filter(must=[FieldCondition(key=..., match=MatchValue(...))]))`; payload indexes recommended for filtered search at scale. Heavier operational footprint on Windows (Docker requirement called out in docs).
- Embedded options [Verified — https://qdrant.tech/documentation/edge/edge-quickstart/]: **Qdrant Edge** — "lightweight vector search engine that supports Python and Rust and runs directly in-process"; `pip qdrant-edge-py`; `EdgeShard.create(dir, EdgeConfig(vectors={...}))`; upsert via `UpdateOperation.upsert_points`; payload indexes (`create_field_index`), filters, facets; **no background optimizer — app calls `edge_shard.optimize()`**; WAL (+ "disable WAL" option), `close()`/`load()` round-trip. New engine (docs current 2026; maturity young).
- Classic client local mode [half-Verified]: `QdrantClient(":memory:")` documented as "For experimentation" inside fastembed's official Qdrant example (https://github.com/qdrant/fastembed README); path-based local persistence detail not re-verified this session [Unverified].

---

## 3. Embedding models for short technical text

### 3.1 Verified candidates

| Model | Dims | Params | License | Truncation | Notes | Source |
|---|---|---|---|---|---|---|
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | 22.7M | Apache-2.0 [Verified — card] | >256 word pieces | Sentence & short-paragraph encoder; 177M downloads/month; ONNX + OpenVINO files exist on the HF repo; Chroma's default EF; trained on 1B+ sentence pairs | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 [Verified] |
| `sentence-transformers/all-mpnet-base-v2` | 768 | 0.1B (~110M) | Apache-2.0 [Verified — card] | >384 word pieces | Stronger quality tier in the same sbert family; 20.5M downloads/month; TEI docker container documented for serving | https://huggingface.co/sentence-transformers/all-mpnet-base-v2 [Verified] |
| `BAAI/bge-small-en-v1.5` (fastembed default) | 384 [Verified via fastembed README code: "Vector of 384 dimensions"] | small English retrieval model, MTEB lineage | MIT per HF card [Unverified-detail] | — | fastembed's out-of-the-box model; supports query/passage prefixes | https://github.com/qdrant/fastembed [Verified] |

- **ONNX route [Verified]:** `fastembed` ("Light: … We don't require a GPU and don't download GBs of PyTorch dependencies, and instead use the ONNX Runtime"; `add_custom_model` accepts any HF model with an ONNX file; Apache-2.0 license verified on repo). `onnxruntime` 1.31.1 resolved in the repo venv dry-run [Verified-local]. MiniLM/MPNet repos expose ONNX/OpenVINO artifacts [Verified — library chips on model cards].
- **Install surface [Verified-local 2026-11-10]:** `sentence-transformers` 6.2.0 and `fastembed` 0.9.1 both resolve on Windows/Python 3.13; fastembed+sqlite-vec together = only **17 packages** to install (`onnxruntime`, `tokenizers`, `huggingface-hub`, `pillow`, …) — no torch. sentence-transformers pulls the torch stack [Unverified-detail on torch wheel size] but resolved cleanly.
- **CPU latency on this machine class: no primary source publishes it.** The fetched model cards contain model size/params and training details, not per-CPU latency tables. Treat any "X ms/sentence on CPU" claim as unverified until benchmarked locally; at hundreds→thousands of records, one-off embedding cost is bounded anyway (batch jobs, not interactive).
- **Context for later news headlines:** MiniLM truncates at 256 word pieces — fine for headlines; partition-key example in sqlite-vec docs is literally news headlines by date [Verified].

### 3.2 Structured vs text embeddings for experiment metadata — documented facts only

1. **Text-embedding models are documented and trained for text.** Both sbert cards state: "maps sentences & paragraphs to a N dimensional dense vector space … intented as a sentence and short paragraph encoder" [Verified]. Nothing fetched documents text-embedding models applied to pure numeric/tabular records.
2. **Structured query dimensions are handled relationally everywhere.** Every candidate documents metadata filtering as the mechanism for exact facts: sqlite-vec metadata columns [Verified], pgvector WHERE + b-tree/partial indexes [Verified], Qdrant payload filters + payload indexes [Verified], Chroma metadata filtering [Verified], LanceDB filtering/SQL + computed columns [Verified at blurb level].
3. **Raw feature vectors as literals are natively supported** for a *literal distance* semantics on metrics: each store accepts arbitrary float vectors — pgvector `vector`/`halfvec` [Verified], sqlite-vec float/int8/binary [Verified], Lance `FixedSizeList<Float32>` columns [Verified], DuckDB `FLOAT[n]` [Verified], Qdrant named vectors [Verified]. So "experiment-metric similarity" can be implemented as an L2/cosine query over a standardized feature vector (e.g. scaled Sharpe/DD/win-rate) without any text encoder — semantics are then distance-between-facts, not semantic similarity.
4. **Practitioner pattern visible in official docs is hybrid:** pgvector README ships a hybrid-search example combining vector similarity with Postgres FTS/RRF [Verified]; Qdrant documents hybrid queries (dense+sparse) [Verified]. For experiment records this maps to: filter on structured facts (pair, timeframe, feature-group id, fold count) + similarity over (a) text summary embeddings and/or (b) raw metric feature vectors.
5. **Absence noted (fact, not proof):** the fetched primary sources contain no endorsement and no recipe for embedding tabular/numeric experiment records *through a text-embedding model*; treating numbers-cosine as "semantic similarity" of runs would be folk practice, unsupported by the sources fetched.

---

## 4. Relational side — plain SQLite vs Postgres for experiment records

SQLite's own checklist [Verified — https://www.sqlite.org/whentouse.html, updated 2025-05-31]:
- "Device-local storage with low writer concurrency and less than a terabyte of content, SQLite is almost always a better solution. … fast and reliable … requires no configuration or maintenance."
- Client/server preferred when: data separated from the app by a network; **many concurrent writers**; big data (SQLite caps at 281 TB, single file); "Otherwise → choose SQLite!"
- SQLite limitation of note: "SQLite will only allow one writer at any instant in time" (unlimited readers).

Postgres deltas that matter at this scale [as capability facts]: multi-writer concurrency, network access by design, server-side backups/roles, the pgvector extension living in the same ACID database as the facts [Verified — pgvector README]. Deltas SQLite gives back: zero service to install/run/backup on Windows; the vector extension lives in the same file/process as the facts [Verified — sqlite-vec docs]; already the freqtrade default.

Freqtrade context [Verified — https://www.freqtrade.io/en/stable/advanced-setup/]: "freqtrade is using a SQLite database where it stores various types of information…"; `--db-url sqlite:///tradesv3.dryrun.sqlite`; PostgreSQL and MariaDB are "tested and are known to work" via SQLAlchemy **but**: *"By using one of the below database systems, you acknowledge that you know how to manage such a system. The freqtrade team will not provide any support with setup or maintenance (or backups)."* — i.e. switching the *bot*'s DB to Postgres removes team support; a *separate* experiment store is orthogonal to that.

Capability-delta summary at the project's scale (hundreds → low-thousands of rows): both engines cover single-writer batch recording + SQL analytics; the deltas are operational (service vs file) and concurrency (single writer vs multi-writer), not feature parity for this workload. The vector-layer choice is coupled to it: pgvector requires Postgres; sqlite-vec requires SQLite; LanceDB/Chroma/Edge are file-based *neighbors* usable with either relational side.

---

## 5. Write-path patterns (file-based runner → store), with cited examples

1. **Idempotent upsert by natural key (experiment_id)** — SQLite: `INSERT … ON CONFLICT(experiment_id) DO UPDATE SET …` with `excluded.col` to take the new values; multiple `ON CONFLICT` clauses allowed since 3.35.0; UPSERT fires only on uniqueness constraints; and it **cannot be used on virtual tables** → the vec0 layer uses delete-then-insert keyed off the relational PK. [Verified — https://www.sqlite.org/lang_upsert.html]. A documented refinement: the `WHERE excluded.validDate>phonebook2.validDate` guard makes DO UPDATE a no-op for stale re-runs, i.e. write-order protection [Verified — same page].
2. **Vector-layer upsert patterns** — pgvector ships the exact idiom: `INSERT INTO items (id, embedding) VALUES (…) ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding` [Verified — https://github.com/pgvector/pgvector]. Chroma: `collection.upsert(ids, documents, …)` [Verified — getting-started]. Qdrant: `client.upsert` is the native write op, and the migration tutorial uses `update_mode=INSERT_ONLY` upserts so a restartable backfill never overwrites newer writes [Verified — migration tutorial].
3. **Runner wiring example in this project's own ecosystem:** freqtrade's CLI takes `--db-url` (SQLAlchemy URL) and writes records to a SQLite file, creating it if missing — a documented file-based-runner → single-file-store pattern [Verified — advanced-setup].
4. **Re-indexing / model-change strategy (the one documented end-to-end example):** Qdrant's "Migrate to a New Embedding Model with Zero Downtime" tutorial: (a) re-embedding **requires retaining the source text** ("Re-embedding requires access to the original data… This data can come from a primary database, or it may be stored in the payloads"); (b) **dual writes** to old and new during migration; (c) batched `scroll` backfill with insert-only upserts, resumable via a persisted offset, and "because the conditional upserts would not overwrite any points… you could safely restart the migration process from the beginning"; (d) switch reads via alias flip or named-vector `using` parameter; (e) deletes/partial updates must be paused or handled explicitly [Verified — https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/].
5. **Multi-model coexistence in one store:** pgvector's FAQ documents storing vectors of *different dimensions* in one table with a `model_id` column in the PK + expression/partial indexes per model [Verified — pgvector README FAQ]. This is the documented shape for "same experiment, several embedding versions".
6. **Vector-store-side versioning:** LanceDB documents table versioning ("trace each training run back to the exact data it used") [Verified]; DuckDB VSS rewrites the whole HNSW index on checkpoint — cheap to drop-and-rebuild at this scale [Verified].

---

## 6. Contradictions & tensions found

1. **sqlite-vec "runs anywhere!" vs "pre-v1, expect breaking changes"** [both Verified, same README] — README marketing vs maturity warning; docs site itself is marked "work-in-progress". Windows support is solid on the wheel, but the release train is still alpha-tagged (0.1.10a4).
2. **LanceDB "search, filtering, and SQL" vs Embedded reality** — the docs home describes SQL-capable search, while the quickstart explicitly marks SQL as an **Enterprise** feature of Embedded [Verified both pages]. Read as: Embedded gets Python filter APIs; SQL-over-tables is a paid tier.
3. **DuckDB VSS in core-extensions docs vs "don't use in production"** — same official page both lists the extension and recommends against persisted indexes in production (crash-recovery unimplemented; whole-index rewrite per checkpoint) [Verified].
4. **Chroma docs posture** — CloudClient leads the client docs and the install page suggests Chroma Cloud for "production", while the OSS embedded `PersistentClient` remains an unqualified, working local option [Verified].
5. **Qdrant has two overlapping embedded stories** — the aging client-local mode (":memory: For experimentation", shown in fastembed's README) and the new 2026 Qdrant Edge engine; Qdrant's own interfaces page documents neither, only server clients [Verified both directions].
6. **Freqtrade Postgres support tension** — "tested and known to work" vs explicit no-support warning from the maintainers [Verified].
7. **MiniLM speed folklore** — community numbers (e.g. "2800 sents/s on A100") circulate via old sbert pages; the fetched model cards do not contain per-CPU latency → any local latency claim needs an on-machine benchmark [Verified absence].

---

## 7. Design implications for v0.3 (neutral — no decision made)

- **Minimal-install path that matches existing habits:** SQLite (already in the venv at 3.50.4 ≥ 3.41) + `sqlite-vec` (~0.3 MB wheel) puts facts and vectors in one file, zero services, `uv add sqlite-vec` only. Costs: pre-v1 stability, delete+insert writes for vec0, and metadata filtering limited to `=`/range ops on ≤16 typed columns.
- **Strongest single-store relational path:** Postgres + pgvector gives joins between facts and vectors, SQL-grade filtering, and mature upserts — at the documented cost of running + administering a Postgres server and building the extension (MSVC or Docker) on Windows.
- **Server-free alternatives with their own file formats:** LanceDB (Arrow-native, table versioning, AVX2 wheel caveat), Chroma (heaviest deps, embedded PersistentClient, MiniLM default), Qdrant Edge (young in-process engine). Each keeps the relational side and the vector side in *different* stores, so facts-vs-vector consistency moves into the runner.
- **Any choice keeps experiment rows as the source of truth**; every vector store here is subordinate to an idempotent write keyed by `experiment_id` (SQLite/pgvector ON CONFLICT, Chroma/Qdrant upserts), with vec0 requiring delete+insert [Verified].
- **Embedding-model facts:** default-grade local option is `all-MiniLM-L6-v2` (384-dim, Apache-2.0, ONNX available; also the default inside Chroma and fastembed examples); 768-dim upgrade path is `all-mpnet-base-v2`; ONNX-first route is `fastembed`/onnxruntime (default `bge-small-en-v1.5`, 384-dim). Latency on this machine is unbenchmarked — benchmark before committing.
- **Persist `embedding_model` + version per embedding row** (pgvector FAQ shows the pattern with `model_id` in the PK + partial indexes); re-embedding requires retaining source text — the Qdrant tutorial's dual-write + insert-only-backfill pattern is the one documented re-indexing recipe and it is store-agnostic in spirit.
- **Structured-vs-text:** official docs support *filters* for facts, *text embeddings* for free-text summaries, and *raw float feature vectors* for literal metric similarity; no source supports embedding numeric records through a text encoder — any such design would be un-evidenced.
- **News-headline layer later:** same 384-dim MiniLM path covers headlines (<256 word pieces); sqlite-vec docs' own partitioning example is headlines-by-date; Qdrant/hybrid and pgvector/FTS recipes exist for keyword+vector mixes.
- **Cheap de-risking for v0.3:** candidates differ mainly in install weight and maturity, so a 20-record spike (upsert, filtered KNN, delete, re-embed) per top candidate would convert the remaining unknowns into facts — consistent with the existing fact-finding files in `research/`.

---

## Appendix — primary source index (all fetched 2026-11-10)

| Claim cluster | URL | Mark |
|---|---|---|
| sqlite-vec README, maturity warning, sponsors, install matrix | https://github.com/asg017/sqlite-vec | Verified |
| sqlite-vec PyPI 0.1.9 / 0.1.10a4, win wheel + license | https://pypi.org/project/sqlite-vec/ | Verified |
| sqlite-vec Python usage + SQLite ≥3.41 note | https://alexgarcia.xyz/sqlite-vec/python.html | Verified |
| sqlite-vec vec0 metadata/partition/aux columns + limits | https://alexgarcia.xyz/sqlite-vec/features/vec0.html | Verified |
| pgvector v0.8.7, capabilities, Windows nmake, Docker, FAQ | https://github.com/pgvector/pgvector | Verified |
| DuckDB vss experimental + persistence warnings | https://duckdb.org/docs/2.0/core_extensions/vss.html | Verified |
| Chroma about/license, clients (PersistentClient), getting-started (upsert), default EF MiniLM | https://docs.trychroma.com/ (+ /docs/run-chroma/clients.md, /docs/overview/getting-started.md, /docs/embeddings/embedding-functions.md) | Verified |
| LanceDB embedded model, quickstart (AVX2 caveat, SQL=Enterprise), versioning | https://docs.lancedb.com/ (+ /basics/lancedb-embedded.md, /quickstart.md) | Verified |
| FAISS MIT license | https://raw.githubusercontent.com/facebookresearch/faiss/main/LICENSE | Verified |
| LanceDB Apache-2.0 license | https://raw.githubusercontent.com/lancedb/lancedb/main/LICENSE | Verified |
| Qdrant server quickstart, filters; interfaces page; Edge quickstart | https://qdrant.tech/documentation/quickstart/, /documentation/interfaces/, /documentation/edge/edge-quickstart/ | Verified |
| Qdrant embedding-model migration (dual-write, insert-only backfill, source-data retention) | https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/ | Verified |
| fastembed ONNX approach, default model, miniLM-with-qdrant example, Apache-2.0 | https://github.com/qdrant/fastembed | Verified |
| all-MiniLM-L6-v2 card (384d, 22.7M, Apache-2.0, 256 word pieces) | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 | Verified |
| all-mpnet-base-v2 card (768d, 0.1B, Apache-2.0, 384 word pieces) | https://huggingface.co/sentence-transformers/all-mpnet-base-v2 | Verified |
| SQLite UPSERT (virtual-table limitation, excluded., stale-guard example) | https://www.sqlite.org/lang_upsert.html | Verified |
| SQLite appropriate-uses checklist | https://www.sqlite.org/whentouse.html | Verified |
| Freqtrade SQLite default + PG/MariaDB no-support warning | https://www.freqtrade.io/en/stable/advanced-setup/ | Verified |
| Repo venv: Python 3.13.12, SQLite 3.50.4; dry-run resolutions (sqlite-vec 0.1.9, chromadb 1.5.9, lancedb 0.41.0, duckdb 2.0.0, faiss-cpu 1.16.0, fastembed 0.9.1, qdrant-client 1.20.0, sentence-transformers 6.2.0, pgvector 0.5.1, onnxruntime 1.31.1) | local: `uv run python -c "import sqlite3…"`; `uv pip install --dry-run …` in repo venv, 2026-11-10 | Verified-local |
| qdrant-client path persistence; pgvector/duckdb/qdrant license texts; pgvector-python API details; LanceDB upsert semantics; torch dependency size | respective repos/docs | Unverified / Unverified-detail |
