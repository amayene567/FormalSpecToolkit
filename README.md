# FormalSpecToolkit

Measurements of re-verification cost on real commits of MongoDB's TLA+ specifications.
Artifacts for the technical report *The Re-verification Cost of Evolving Distributed
Protocols: A Pilot Study on MongoDB's TLA+ History* (version 3, October 2026).

## Contents of `pilot/`

| Path | Content | Report section |
|---|---|---|
| `fetch_specs.sh` | Regenerates `specs/` from `mongodb/mongo` at the studied commits | 2 |
| `raw_logs/r1/` | Result 1, RaftMongo (SERVER-45853): parent, invariants only, child; `rerun1/` holds the three alternated reruns | 3 |
| `raw_logs/log2_*` | Result 2, 4 servers (did not converge) | 4 |
| `raw_logs/log3_*`, `log4_*` | Result 2, 3 servers, two runs | 4 |
| `canon.py` | Canonicalization of TLC state dumps modulo server symmetry | 5 |
| `overlap/hashes_summary.txt` | Line counts and SHA-256 of the sorted canonical (`cp_*`) and non-permuted (`np_*`) hash files, and the canonical intersection (2,413,165). The hash files themselves (about 400 MB) are not committed; `canon.py` regenerates them from TLC dumps | 5 |
| `reuse_analysis.py`, `reuse_results.txt` | Earlier raw textual comparison (intersection 2,041,276). Superseded by `canon.py`: the 371,889 apparent new states were symmetry artifacts | 5 |
| `refinement_check/` | TLC check that the child refines the parent, with a failing converse control | 5 |

Every run whose counts or times the report uses ends with
"Model checking completed. No error has been found." The `log2_*` runs and
`r1/log_apres.txt` (liveness, capped at 600 s) did not complete, as the report states.

## Specifications are not redistributed

The MongoDB specifications are the work of their authors. `RaftMongo.tla` and
`MongoReplReconfig.tla` are licensed under CC BY 3.0 US; the model-checking modules and
configurations carry no license header. `pilot/specs/` is therefore not tracked;
regenerate it with:

    git clone --filter=blob:none https://github.com/mongodb/mongo mongo
    pilot/fetch_specs.sh mongo

| Result | Parent (avant) | Child (après) |
|---|---|---|
| 1, RaftMongo (SERVER-45853) | `d422e688b9e4` | `348880238de3` |
| 2, MongoReplReconfig (SERVER-47430) | `ba6cbcc3b17d` | `dd278880390a` |

Our only changes, both in `fetch_specs.sh`: the constructed "invariants only"
configuration of Result 1 is the child configuration without its `PROPERTY` line, and
Result 2 uses `Server = {n1, n2, n3}` instead of four servers.

## Tool

`tla2tools.jar` v1.7.4 (TLC2 2.19, rev 5a47802), SHA-256
`936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`, run as
`java -XX:+UseParallelGC -jar tla2tools.jar -workers 1 <MC module>.tla`.

## License

Scripts and analysis code: MIT (see license). Logs: CC BY 4.0.
