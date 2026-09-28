# Workflow and external requirements

## What can be run immediately

`tools/evaluate_predictions.py` is a standalone offline entrypoint. It accepts a JSON list or JSONL file of gold examples with `_id` and `answer`, plus a JSON prediction map of `{ "question-id": "predicted answer" }`. A Hotpot-style `{ "answer": { "question-id": "predicted answer" } }` wrapper is also accepted. Gold answers may be strings or nonempty lists of accepted strings.

Missing predictions count as zero under both metrics. The report includes the number of gold examples, matched predictions, missing predictions, and prediction IDs outside the gold set. EM and F1 use the SQuAD-style answer normalization found in the recovered notebook. This is an answer-only research metric; use the official dataset evaluator for official HotpotQA reporting.

## Notebook environment

Use a dedicated working copy of the external data. Open notebooks with their working directory set to `notebooks/`. Absolute local roots have been replaced with `../data/workspace`; existing relative paths and the original experiment directory names are retained. Configure those paths to match the experiment you are adapting.

For API-backed cells, supply your own `OPENAI_API_KEY` in the environment before launching Jupyter. The archived experiments reference GPT-4.1, GPT-4o, and an earlier GPT-3.5 variant. Model access and historical behavior are external dependencies, so changing models produces a new experiment.

The optional notebook requirements support the visible `OpenAI` client, PyTorch and Transformers imports. They were not validated through a full inference run. The original MDR bootstrap used Transformers 2.11.0, while the notebook's OpenAI client requires a newer Python ecosystem. Set up MDR independently using its own instructions rather than installing the archived bootstrap cell into the notebook environment.

## Acquire data and models

1. Obtain HotpotQA from the [dataset authors](https://hotpotqa.github.io/), observing its terms. The experiments refer to Full Wiki data and a processed `hotpot_qas_val.json` file. The released example files are synthetic and cannot substitute for the benchmark.
2. Obtain [Multi-hop Dense Retrieval](https://github.com/facebookresearch/multihop_dense_retrieval) from Facebook Research. Follow its setup and download instructions to obtain the retrieval model and Wikipedia index. The notebook references `scripts/eval/eval_mhop_retrieval.py`, `data/hotpot_index/wiki_index.npy`, `data/hotpot_index/wiki_id2doc.json`, and `models/q_encoder.pt` under `data/workspace/multihop_dense_retrieval/`.
3. Obtain [`allenai/unifiedqa-t5-large`](https://huggingface.co/allenai/unifiedqa-t5-large) through Transformers. Check its model card and use an environment appropriate for your hardware.

No benchmark dataset, Wikipedia corpus, retrieval index, checkpoint, or archived prediction dump is bundled.

## Notebook entrypoints

The code is organized as an experimental notebook archive, with repeated function definitions and alternative cells. Select and adapt a coherent variant before running it; sequentially running every cell can override earlier functions and replace intermediate outputs.

| Stage | File | Functions to inspect |
| --- | --- | --- |
| Decomposition | `MDR_own.ipynb` | `decompose_question_with_dependency`, `save_decomposed_question`, `decompose_and_save_all` |
| Dependency preparation | `subQ_preparing.ipynb` | `find_ids_by_depcode`, `list_and_update_dependency_code_all` |
| Retrieval / QA | `MDR_own.ipynb` | `run_step2_mdr_on_0json_all`, `run_step3_fused_qa_mdr_all_with_memory_management` |
| Initial QA / aggregation | `CoT1.ipynb` | `run_qa_and_save_answers`, `run_cot_aggregation` |
| Context support checks | `CoT1.ipynb`, `context_beready.ipynb` | `process_subq_cot2`, `run_cot2`, `is_answer_supported_by_context_return_idx` |
| Final candidate aggregation | `CoT1 copy.ipynb` | `find_final_answer_and_evidence_via_api`, `run_all`, `can_answer_now` |
| Historical result processing | `MDR2DATA.ipynb` | `get_final_predictions_from_basedir`, `evaluate_on_ids` |

## Intermediate format and limitations

The notebooks use question-ID directories with numbered sub-question and variant subdirectories. Files such as `Q.json`, `A.json`, and `P.json` store questions, retrieved context, answers, and dependency information. Their exact schemas vary between notebook cells; inspect the selected writer and its downstream reader together. A unified schema migration was not present in the snapshot.

Several retrieval-failure paths create placeholder/dummy results for debugging, and some routines suppress exceptions. Those outputs are not real retrieval evidence and must be excluded from any research evaluation. Other cells modify or replace intermediate files. Colab mounting/installation and one standalone directory-deletion cell were converted to markdown in this release; data-writing behavior inside research functions remains documented archival code.

A complete standalone implementation of every final paper reverse-verification step was not established from the recovered snapshot. The final aggregation and evidence-checking code is included under its actual names, without relabeling it as a verified complete reproduction. A locked environment, exact evaluation IDs, final prompt manifest, and end-to-end validation are still needed for paper-exact reproduction.
