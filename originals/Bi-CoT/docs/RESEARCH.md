# Research notes

The supplied 2025 paper draft describes a training-free plugin for multi-hop QA. It exposes intermediate questions, answers, and evidence to help diagnose error propagation. Forward self-aware QA checks whether the retrieved evidence supports each answer. Reverse verification revisits the original question, answer type, comparison structure, and dependencies before producing the final answer and core evidence.

The draft uses MDR retrieval and `allenai/unifiedqa-t5-large` as its initial QA backbone. It describes one paraphrase per sub-question to vary retrieval queries, and GPT-4.1/GPT-4o for the plugin stages. These statements come from the author's paper draft; the repository does not claim that every described component has a final, isolated implementation in the recovered notebooks.

## Reported results

The draft's first table reports answer EM/F1 of 24.16/33.15 for the baseline, 32.67/42.62 with self-aware QA, and 42.77/55.40 for the full method. Relative to the baseline, the full method improves EM by 18.61 percentage points and F1 by 22.25 percentage points in that reported experiment.

The draft also reports that approximately 65.3% of questions reached reverse verification, with evidence availability limiting the rest. A second table reports a different evaluation comparison, but the exact subset and protocol are not recoverable from the inspected text. Those second-table numbers are therefore not used as a general full-dataset headline here.

No expensive experiments were rerun when preparing this archive. The benchmark split, exact question IDs, API model snapshots, complete final prompt variants, and environment need to be resolved before reproducing the reported results. The bundled offline example is synthetic and supplies no evidence for these benchmark claims.

## Publication identity

- Local manuscript: *Plug-and-Play Bi-CoT: Self-Aware Forward Reasoning and Reverse Verification for Explainable Multi-Hop QA*.
- Authors shown in the manuscript: 강지헌 and 정수환, with Yonsei University and Pukyong National University affiliations respectively.
- The author's CV lists a shorter title, *Bi-CoT: Forward Reasoning and Reverse Verification for Explainable Multi-Hop QA*, at the 6th Korea AI Conference, 2025.

The publication venue is recorded from the supplied CV. This release does not add a DOI, proceedings URL, award, or review status that was not verified in the supplied materials.
