# PRD — GeoGov Lite (Python Backend)

Goal: From a feature artifact, return a Yes/No on whether geo-specific compliance logic is required, with reasoning, candidate regulations, citations, confidence, and an audit receipt. Support bulk analysis + CSV and a simple evidence ZIP.

Language: Python 3.11
Framework: FastAPI (+ Uvicorn)
LLM: Anthropic/OpenAI (env-switchable)
RAG: Mem0 as your memory/RAG layer (vector + metadata)
Scraping: Firecrawl, Exa, Perplexity (pluggable clients)
Store: SQLite for hackathon simplicity (upgrade path to Postgres)
Search: Hybrid (BM25 via rank_bm25 + vector via Mem0)

⸻

1) Success criteria
	•	Single analysis ≤ 3s p95 (with cached RAG).
	•	Deterministic final Yes/No from rules engine given same inputs.
	•	outputs.csv generated for the provided dataset.
	•	Evidence export contains: policy snapshot, receipts.jsonl, outputs.csv, merkle.txt.

⸻

2) Inputs & Outputs

2.1 Feature Artifact (request)

{
  "feature_id": "F-2381",
  "title": "Personalized Home Feed v3",
  "description": "Reranks videos using watch history; EU rollout planned.",
  "docs": ["https://internal/prd", "https://internal/trd"],
  "code_hints": ["uses ageGate()", "if region in ['EU','EEA']:"],
  "tags": ["recommender","personalization","minors_possible"]
}

2.2 Decision (response)

{
  "feature_id": "F-2381",
  "needs_geo_compliance": true,
  "reasoning": "Personalized recommender in the EU → DSA requires a non-personalized option & transparency/appeals for moderation decisions.",
  "regulations": ["EU-DSA"],
  "signals": ["personalization","EU","recommender"],
  "citations": [{"source":"mem0://dsa/recommender_opt_out#p2","snippet":"..."}],
  "confidence": 0.81,
  "matched_rules": ["EU_DSA_RECS"],
  "hash": "sha256-...",
  "ts": "2025-08-27T06:03:21Z",
  "policy_version": "v0.1.0"
}

2.3 CSV columns

feature_id,title,needs_geo_compliance,reasoning,regulations,confidence,signals,citations,matched_rules,policy_version,ts

⸻

3) Scope & Non-goals

In scope: single & bulk analyze, RAG retrieval, LLM ensemble (Finder/Counter/Judge), deterministic rules engine, receipts hashing, CSV/ZIP export, scraping workers.
Out of scope (hackathon): auth, full code scanning, multi-tenant RBAC, streaming.

⸻

4) High-level architecture

fastapi app
 ├─ /api/analyze            (POST)  one artifact → decision
 ├─ /api/bulk_analyze       (POST)  list → outputs.csv (+ store receipts)
 ├─ /api/evidence           (GET)   zip of receipts + csv + policy snapshot
 ├─ /api/health             (GET)
 └─ /api/refresh_corpus     (POST)  trigger scrape+ingest (admin/dev)

internal/
 ├─ rag/        (mem0 client, indexer, retriever)
 ├─ scrape/     (firecrawl.py, exa.py, perplexity.py, aggregator.py)
 ├─ llm/        (finder.py, counter.py, judge.py, client.py)
 ├─ rules/      (engine.py, schema.py, rules.yaml)
 ├─ signals/    (extract.py  → tags/text/NER/regex)
 ├─ evidence/   (receipts.py, merkle.py, csvio.py, zipkit.py)
 ├─ models/     (pydantic schemas)
 └─ util/       (logging, settings)
data/
 ├─ mem0/       (chunks/embeddings)
 ├─ receipts.jsonl
 ├─ outputs.csv
 └─ policy_snapshot.yaml


⸻

5) Modules (function-level requirements)

5.1 rag/ (Mem0)
	•	index_documents(docs: list[RawDoc]) -> int
	•	retrieve(query: str, k:int=6) -> list[Chunk]
	•	hydrate_citations(chunks) -> list[Citation]
Notes: store jurisdiction, topic, source_url, updated_at. Use Mem0’s vector store; fall back to FAISS if needed.

5.2 scrape/
	•	firecrawl.fetch(urls|queries) -> list[RawDoc]
	•	exa.search(query) -> list[Result] (returns URL + snippet)
	•	perplexity.answer(query) -> Summary + citations
	•	aggregator.refresh(topics:list[str]) -> IngestionReport
Behavior: dedupe by URL+hash; write to mem0 with source tags (eu_dsa, ncmec, ca_sb976, fl_minors, ut_minors).

5.3 signals/extract.py
	•	extract_signals(artifact) -> SignalSet
	•	Keywords/regex: “personalized|ranking|feed”, “minor|under 18|teen”, “appeal|takedown|notice”, “EU|EEA|France|Germany”, “NCMEC|CSAM”.
	•	NER (optional): spacy small model for countries/ages.
	•	Code hints: scan code_hints[] for region checks / age gates.

5.4 llm/
	•	finder(artifact, chunks) -> FinderOut
	•	counter(artifact, chunks) -> CounterOut
	•	judge(artifact, finder_out, counter_out) -> JudgeOut
	•	JSON-only outputs; temperature 0.2–0.4; strict Pydantic validation.
Prompts (summaries):
	•	Finder: “List geo-reg obligations that could apply; cite chunk ids; return signals[].”
	•	Counter: “Argue non-legal/business geofence; list missing_signals[].”
	•	Judge: “Merge; normalize signals; produce confidence 0–1; no Yes/No.”

5.5 rules/engine.py
	•	Input: artifact, signals, judge.notes, raw text corpus (for simple text_contains).
	•	File: rules.yaml (policy-as-code).
	•	API: evaluate(signals: SignalSet, text: str) -> Verdict
	•	returns (verdict: bool, matched_rules: list[str], regulation: list[str], reason: str)
	•	Operators: when_any, when_all, and_text, and_not_text, tokenized case-insensitive contains.

Starter rules.yaml (cover target regimes):

- id: EU_DSA_RECS
  when_any:
    tags: ["recommender","personalization"]
    text: ["personalized feed","ranking"]
  and_text: ["EU","EEA","Europe"]
  verdict: true
  regulations: ["EU-DSA"]
  reason: "Personalized recommender in the EU → non-personalized option & transparency."
- id: DSA_MOD_APPEALS
  when_any_text: ["remove","takedown","moderation","appeal"]
  and_text: ["EU","EEA","Europe"]
  verdict: true
  regulations: ["EU-DSA"]
  reason: "Moderation decisions for EU users require explanation & appeals."
- id: MINORS_ADS_STATE
  when_any: { tags: ["ads","targeting"] }
  and_text: ["minor","under 18","teen","age gate","parental"]
  verdict: true
  regulations: ["CA-SB976","FL-OPM","UT-SMRA"]
  reason: "Minors & targeting imply state restrictions; age gates/parental controls."
- id: NCMEC_REPORTING
  when_any_text: ["NCMEC","CSAM","child sexual abuse"]
  verdict: true
  regulations: ["US-NCMEC"]
  reason: "Safety features intersect with NCMEC reporting duties."
- id: BUSINESS_GEOFENCE
  when_all_text: ["geofence","market test","US"]
  verdict: false
  regulations: []
  reason: "Business-driven geofence (not legal requirement)."

5.6 evidence/
	•	write_receipt(decision: Decision) -> str_hash (append JSONL; compute sha256 over canonical JSON)
	•	merkle_root(hashes:list[str]) -> str
	•	export_csv(decisions:list[Decision]) -> path
	•	zipkit.make_zip(files: list[path]) -> bytes

⸻

6) API Endpoints (FastAPI)

POST /api/analyze

Body: Feature Artifact
Flow: extract signals → RAG retrieve → Finder → Counter → Judge → Rules evaluate (final Yes/No) → write receipt → return Decision.
Response: Decision JSON
Errors: 400 validation; 502 LLM/RAG; 500 internal.

POST /api/bulk_analyze

Body: {"items":[<FeatureArtifact>...]}
Flow: run /analyze per item (async pool), accumulate decisions, write outputs.csv, keep receipts.
Response: {"count":N,"csv_path":"data/outputs.csv"} (or return file).

GET /api/evidence

Query: feature_id?, since?, until?
Returns: ZIP (policy snapshot, receipts in window, outputs.csv if exists, merkle.txt).

GET /api/health

Return build info + rules.yaml hash + mem0 corpus stats.

POST /api/refresh_corpus

Dev/admin action: run scrape.aggregator.refresh() for predefined topics/URLs; index into Mem0.

⸻

7) Data & Storage
	•	SQLite (hackathon):
	•	Optional receipts table mirrored from JSONL (for quick filtering).
	•	Filesystem:
	•	data/receipts.jsonl (append-only)
	•	data/outputs.csv
	•	data/policy_snapshot.yaml (copy of rules at deploy)
	•	data/mem0/ (vector store files)

⸻

8) Configuration

.env

OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
FIRECRAWL_API_KEY=...
EXA_API_KEY=...
PERPLEXITY_API_KEY=...
RAG_TOPK=6
POLICY_VERSION=v0.1.0

settings.py loads env via pydantic-settings.

⸻

9) Libraries
	•	FastAPI, uvicorn
	•	pydantic (v2), python-dotenv
	•	mem0 (RAG/memory) + faiss-cpu (fallback)
	•	rank_bm25 (BM25)
	•	httpx (async clients for Firecrawl/Exa/Perplexity)
	•	tenacity (retry LLM/scrape calls)
	•	numpy, scikit-learn (optional)
	•	spacy (small model, optional)
	•	pyyaml (rules), orjson (fast JSON), hashlib
	•	pandas / csv (export)
	•	zipfile (evidence ZIP)

⸻

10) Orchestration logic (pseudocode)

async def analyze(artifact: FeatureArtifact) -> Decision:
    sigs = extract_signals(artifact)
    chunks = rag.retrieve(" ".join([artifact.title, artifact.description] + sigs.hints), k=RAG_TOPK)
    fnd  = await finder(artifact, chunks)
    ctr  = await counter(artifact, chunks)
    jdg  = await judge(artifact, fnd, ctr)
    verdict = rules.evaluate(jdg.signals or sigs, text=artifact.title + " " + artifact.description)
    decision = Decision(
        feature_id=artifact.feature_id,
        needs_geo_compliance=verdict.ok,
        reasoning=verdict.reason,
        regulations=verdict.regulations,
        signals=list(set(sigs.to_list() + jdg.signals)),
        citations=rag.hydrate_citations(fnd.citations),
        confidence=jdg.confidence,
        matched_rules=verdict.matched_ids,
        ts=utcnow(),
        policy_version=POLICY_VERSION
    )
    decision.hash = write_receipt(decision)
    return decision


⸻

11) Testing
	•	Unit: rules evaluator (golden cases), signal extractor, CSV writer, merkle root.
	•	LLM stub: fixture JSON for Finder/Counter/Judge to make tests deterministic.
	•	Integration: /api/analyze happy path, bulk CSV generation, evidence ZIP creation.

⸻

12) Demo data & scripts
	•	scripts/load_dataset.py → reads the synthetic dataset JSON/CSV and calls /api/bulk_analyze.
	•	scripts/dev_refresh_corpus.py → seeds Mem0 with pre-curated DSA & state law excerpts.

⸻

13) Operational notes
	•	Cache Mem0 index in process global to avoid reload on each request.
	•	Timeouts: LLM calls 4s each; total endpoint budget ~3s with caching.
	•	Log every step with a request id; include LLM model/version and rules hash in the receipt.

⸻

14) Risks & mitigations
	•	LLM hallucination → Rules engine makes final call; receipts include citations + prompt/model versions.
	•	External API flakiness → tenacity retries; scrape is best-effort and cached.
	•	Performance → hybrid retrieval (BM25 first) + small top-k.

⸻

15) Deliverables checklist
	•	FastAPI app deployed (or uvicorn main:app --reload)
	•	/api/analyze & /api/bulk_analyze working
	•	data/outputs.csv produced for provided dataset
	•	/api/evidence returns a ZIP with receipts, CSV, policy snapshot, merkle
	•	README with local run + sample curls
	•	3-min demo script

⸻

16) Exact endpoint contracts (OpenAPI summary)
	•	POST /api/analyze → 200: Decision | 400 | 502 | 500
	•	POST /api/bulk_analyze → 200: {"count": int, "csv_path": str}
	•	GET /api/evidence → 200: application/zip
	•	GET /api/health → 200: {"ok": true, "rules_hash": "...", "mem0_docs": 1234}
	•	POST /api/refresh_corpus → 202: {"ingested": n, "sources": {...}}

⸻

17) Starter prompts (drop-in)

Finder

You are a compliance analyst. Given a product feature and retrieved legal snippets,
list geo-regulatory obligations that COULD apply. Return JSON with fields:
signals[], claims[{regulation, why, citations[]}]. Be concise and grounded in the snippets.

Counter

You are a red-team reviewer. Argue why the feature may NOT require geo-specific legal logic
(e.g., business geofence). Return JSON with counter_points[], missing_signals[], citations[].

Judge

You are the adjudicator. Merge Finder and Counter. Normalize a deduplicated signals[] list,
produce notes (1-2 sentences), and a confidence in [0,1]. Do not decide YES/NO.
Return JSON: {signals:[], notes:"", confidence:0.x}


⸻

18) README run block (for Claude to generate later)

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# POST /api/analyze with sample payloads in samples/*.json


⸻

If you want, I can follow up with:
	•	rules.yaml full starter (covering EU-DSA, CA-SB976, FL-OPM, UT-SMRA, US-NCMEC),
	•	FastAPI handler skeletons,
	•	and minimal Mem0/BM25 retrieval code stubs you can paste in.