# A Lightweight Four-Credential Authentication and Key Agreement Protocol for AI-Enabled Edge-IIoT

This repository contains the revised manuscript, the reproducible benchmark and AVISPA artifacts, and the response letter for the CMC special-issue revision.

## Contents

- `manuscript/` — clean and tracked LaTeX sources, bibliography, template definitions, and the network-model figure.
- `supplementary/benchmarks/` — the host reference benchmark and its recorded JSON output.
- `supplementary/avispa/` — the HLPSL model, WSL instructions, and AVISPA result logs.
- `response/` — the cover letter, response letter source, reviewer blocks, and response-letter bibliography.
- `artifacts/` — the compiled clean manuscript, tracked manuscript, and latest response-letter PDFs.

## Reproducibility notes

The protocol-field profile is `H_160(m) = Trunc_160(SHA-256(m))`. The benchmark measures the underlying full SHA-256 primitive and applies truncation only when a digest is serialized as a protocol field. The reference fuzzy routine is a deterministic timing surrogate (sample, salt, helper digest, and two HMAC-SHA-256 calls), not a mandated error-correcting fuzzy extractor.

From `manuscript/`, compile the clean manuscript with `latexmk -pdf TSP_CMC_SI_rev6_v2_min.tex`. The tracked source uses the supplied `TSP_CMC_SI_rev6_v2_min_track_bibliography.tex` helper. Benchmark and AVISPA execution instructions are included beside their artifacts.

Repository: <https://github.com/secagg4AsyncFL/A-Lightweight-Four-Credential-Authentication-and-Key-Agreement-Protocol-for-AI-Enabled-Edge-IIoT>
