# LLM Benchmark and Evaluation Lab

A small, reproducible evaluation harness for OpenAI-compatible chat completions endpoints. It records exact-match accuracy, mean latency, token usage when reported, per-case outputs, and errors. It ships with an offline fixture provider so its evaluation logic can be tested without credentials or fabricated model results.

## Run offline

```bash
python -m llm_eval.cli --provider fixture --output results.json
python -m unittest discover -s tests -v
```

## Run a configured model

```bash
export LLM_BASE_URL=https://your-compatible-endpoint/v1
export LLM_MODEL=your-available-model-id
export LLM_API_KEY=your-key
python -m llm_eval.cli --provider compatible --output results.json
```

`LLM_BASE_URL` accepts HTTPS or localhost HTTP. The harness sends the included synthetic evaluation prompts to that endpoint. Check provider terms and avoid private data. The output file includes raw prompts and answers; do not publish results from sensitive datasets. No frontier model has been run or benchmarked in this repository.

## Method and limits

The built-in cases test simple facts with exact-match reference strings. This is a **smoke test**, not a broad reasoning or RAG benchmark. An answer with different wording can be marked wrong. Latency is wall-clock client time, including network overhead; token counts use provider-reported usage when present. There is no cost estimate without a separately verified price table. For a meaningful comparison, expand the curated dataset, use repeated trials and confidence intervals, score factual grounding with reviewed evidence, and report model versions and dates.
